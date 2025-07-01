from hycops.classes.workload.nn import NN
from hycops.classes.workload.stack import Stack
from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.hardware.core_group import Core, CoreGroup
from hycops.classes.hardware.pe_array import PEA
from hycops.classes.hardware.buffer import Buffer
from math import ceil
import logging
logger = logging.getLogger(__name__)

E_MAC = 0.1     # J / mac
class HyCostModelEvaluation:
    """
    启发式方法给出一个tile划分策略(也称core allocation)
    这时的stack中的feature map是strip大小的,需要在宽高纬度上进一步切分成几个tile,重新生成core_num个stack,分别对应到cores (实现 core allocation)
    根据此tile划分,逐个tile进行评估
    
    #* 有个问题,为什么一个核只能计算一个tile呢?能不能多划几个tile,让数据流的灵活度更高,这回归到「多核的核间数据流的问题」,
    #* 能想到的回答是算一遍肯定比算两遍要快,因为单核场景下,因为是单核,不得不算很多遍,
    #* 但是只算一遍的话,跟一个单大核处理相比,多核优势在哪里??,而且在单核的视角里,已经不是层融合处理了
    #* 层融合数据流提出的初衷就是特征图太大,减少intermediate FM的片上存储,而这样的话,inter-FM还是全部存在片上了,本质上依然是layer-by-layer
    #* 但是问题是strip足够小的时候,是可以全部存在片上的,strip大的时候,将导致片上buffer开销过大,为了降buffer,将不得不再次划小tile

    #* 所以,依据采样得到的core的片上act buf容量,首先尝试lbl,如果buf不够,则切分更细力度的tile,这实际上是latency--buffer之间的一个trade-off
    #* 这样的话,一个core依据其act buf容量,将存在一个能够单次Fusion处理的tile_size的上限,大于这个tile_size的就只能切tile了,小于这个tile_size的依然能够单次计算,甚至更快
    #* 然后根据其spatial mapping,能找到一个tile_size的形状,即tile_h 和 tile_w,相当于一个边界tile,然后处理这个边界tile的latency是可以算出来的(这个latency将取决于PEA和buf的match程度)
    #* 每个core都有这样一个边界tile,然后呢??考察每个core的边界tile的处理面积和整个Strip的关系
    """
    def __init__(self,
        nng: List[NN],
        cg: CoreGroup,
        ):
        """
        给定一个NNG, 一个strip大小(已体现在NN中), 一个cg架构, 评估输入特征图是此strip时, NNG部署在cg上的性能数据
        (stack已经划分, tile_size是全灵活的)
        """
        # self.check_valid(cg)    # 检查core group的合法性，如果确保遗传算子不会产生非法cg，可以注释掉这行，如果修改了遗传算子，建议打开
        self.nng = nng
        self.cg = cg
        self.stacks = self.split_nng_2_stack()
        

    def check_valid(self, cg: CoreGroup):
        ''' CG 的合法性检查
        并不会在硬件组建初始化时进行检查, 因为遗传算子可能导致暂时性不合法 '''
        cg.check_valid()
        
        
    def split_nng_2_stack(self) -> List[Stack]:
        """
        nng的数据结构: List[NN], 每一个NN的数据结构: List[stack]
        将每个NN的stack合并在一起, 成为一个大的List[stack]
        """
        stacks = []
        for nn in self.nng:
            stacks += nn.get_stacks()
        return stacks


    def run(self):
        """
        需要将nng拆分成一系列stack, 逐个评估
        单个stack评估: 
        1. 乒乓buffer是否可以足够缓存stack的IFM和OFM, 如果不够, 此cg失败
        2. 多核采用并行切tile的数据流处理stack, 理论上, 将strip任意切成core_num个长方形(tile), 
            然后分别部署到core上, 如果划分tile足够好, 那么core之间的latency将约等
        3. tile_size的优化问题变成了strip的划分问题, 一个启发式的思路是根据core的H/W方向的spatial mapping来确定
        """

        ''' 计算buffer总容量 '''
        self.calc_buffer_capacity()
        
        ''' 评估buffer size容量是否满足当前所有stack的计算 '''
        self.buf_size_too_small = self.check_buf_size_is_too_small()
        
        if self.buf_size_too_small:
            self.total_la = float('+inf')
            self.total_en = float('+inf')
        else:
            ''' 将nng拆分成若干stack, 然后逐个评估 '''   
            self.stacks_evaluation = [self.evaluation_one_stack(stack, self.cg) for stack in self.stacks]   
            
            la_perS, en_perS, extra_info = zip(*self.stacks_evaluation)
            self.la_perS = la_perS
            self.en_perS = en_perS
            self.extra_info = extra_info
            self.total_la = sum(la_perS)
            self.total_en = sum(en_perS)


    def calc_buffer_capacity(self):
        """
        计算CoreGroup的所有buffer容量, unit: KB
        """
        self.ppb_size = self.cg.ppb.get_buf_size()
        self.core_act_buf_size = [c.act_buf.get_buf_size() for c in self.cg.cores]
        self.core_wt_buf_size = [c.wt_buf.get_buf_size() for c in self.cg.cores]
        self.buffer_capacity = sum(self.core_act_buf_size) + sum(self.core_wt_buf_size) + 2*self.ppb_size
        self.min_core_wt_buf_size = min(self.core_wt_buf_size)


    def check_buf_size_is_too_small(self):
        for stack in self.stacks:
            # 检查乒乓buffer和wt buffer的容量
            ifm, ofm = stack.get_stack_ifm_and_ofm()
            wt_amount = stack.get_stack_weight_data_amount()
            if (ifm > self.ppb_size * 1024) or (ofm > self.ppb_size * 1024) or (wt_amount > self.min_core_wt_buf_size * 1024):
                # raise KeyError(f'ifm:{ifm/1024} KB, ofm:{ofm/1024} KB, ppb_size:{self.ppb_size} KB, wt: {wt_amount/1024} KB, min_core_wt: {self.min_core_wt_buf_size} KB')
                return True
        return False


    def wt_buffer_capacity_too_small(self, wt_amount) -> bool:
        """
        检查权重buffer的容量, 每个core的wt_buf需要装载这个stack所有的权重数据, 当wt_buf不足以完成任意一个stack的计算, 返回True
        """
        if self.min_core_wt_buf_size * 1024 < wt_amount:
            return True
        else:
            return False


    @staticmethod
    def evaluation_one_stack(stack: Stack, cg: CoreGroup):
        ''' latency '''
        ppb_bw = cg.ppb.get_buf_bw() / 8    # unit: B/cycle
        computation_delay, computation_energy = HyCostModelEvaluation.evaluation_one_stack_computaiton(stack, cg)
        data_loading_delay    = sum([c.get_unroll()['h'] * c.get_unroll()['w'] * c.get_unroll()['ic'] / ppb_bw for c in cg.cores]) + \
            (stack.get_stack_weight_data_amount() / ppb_bw) # 激活填充时间 + 权重填充时间
        data_offloading_delay = sum([c.get_unroll()['h'] * c.get_unroll()['w'] * c.get_unroll()['oc'] / ppb_bw for c in cg.cores])
        ifm, ofm = stack.get_stack_ifm_and_ofm()
        ppb_transfer_delay = max(ifm, ofm) / ppb_bw
        
        ''' energy '''
        memory_energy = (ifm + ofm + stack.get_stack_weight_data_amount()) * cg.ppb.get_read_cost()
        
        ''' stack latency/energy'''
        stack_comp_la = computation_delay + data_loading_delay + data_offloading_delay
        stack_la = max(stack_comp_la, ppb_transfer_delay)
        stack_en = memory_energy + computation_energy

        #### for debug
        # if stack_la == ppb_transfer_delay:
        #     logger.warning(f'stack_la: stack_comp_la={stack_comp_la}; ppb_transfer_delay = {ppb_transfer_delay}')

        return (stack_la, stack_en, (computation_delay, data_loading_delay, data_offloading_delay, ppb_transfer_delay, memory_energy, computation_energy))


    @staticmethod
    def evaluation_one_stack_computaiton(stack: Stack, cg: CoreGroup):
        ''' evaluation delay for a core group on a stack '''
        tile_area_delay_energy_for_cores = [HyCostModelEvaluation.evaluation_one_core(stack, c) for c in cg.cores]
        area_of_strip = stack.get_ifm_area()
        a_div_d_sum = sum([a/d for (a, d, _) in tile_area_delay_energy_for_cores])
        num_factor = [ceil(area_of_strip / a_div_d_sum / d) for (_, d, _) in tile_area_delay_energy_for_cores]
        HyCostModelEvaluation.set_bad_core_flag(cg, num_factor)
        computation_delay_each_core = [f * d for f, (_, d, _) in zip(num_factor, tile_area_delay_energy_for_cores)]
        # print('computation_delay_each_core:', computation_delay_each_core)  # for debug
        # print('num_factor:', num_factor)  # for debug
        computation_delay = max(computation_delay_each_core)
        
        ''' evaluation energy for a core group on a stack '''
        computation_energy_each_core = [f * e for f, (_, _, e) in zip(num_factor, tile_area_delay_energy_for_cores)]
        computation_energy = sum(computation_energy_each_core)
        
        return computation_delay, computation_energy
    
    
    @staticmethod
    def evaluation_one_core(stack: Stack, core: Core):
        ''' evaluation fusion only one tile's area/delay for a core on a stack'''
        act_buf_size = core.get_act_buf_size()  # unit: KB
        unroll = core.get_unroll()
        ich_plus_och_per_layer = [ich + och for ich, och in zip(stack.ich_per_layer, stack.och_per_layer)]
        unit_tile_data_amount = max(ich_plus_och_per_layer) * unroll['h'] * unroll['w'] / 1024  # unit: KB
        unit_tile_factor = act_buf_size / unit_tile_data_amount
        core_fusion_one_tile_area = unit_tile_factor * unroll['h'] * unroll['w']
        core_fusion_one_tile_delay_per_layer = [ceil(unit_tile_factor) * 
                                                ceil(ich / unroll['ic']) * 
                                                ceil(och / unroll['oc']) * 
                                                ceil(kernel / unroll['fx']) * 
                                                ceil(kernel / unroll['fy']) 
                                                for ich, och, kernel in zip(stack.ich_per_layer, stack.och_per_layer, stack.kernel_size)]
        core_fusion_one_tile_delay = sum(core_fusion_one_tile_delay_per_layer)
        
        ''' evaluation fusion only one tile's energy for a core on a stack'''
        one_tile_macs = sum([unroll['h'] * unroll['w'] * ceil(unit_tile_factor) * ic * oc * k * k 
                             for ic, oc, k, in zip(stack.ich_per_layer, stack.och_per_layer, stack.kernel_size)])
        core_fusion_one_tile_energy = one_tile_macs * E_MAC
        
        return core_fusion_one_tile_area, core_fusion_one_tile_delay, core_fusion_one_tile_energy
    
    @staticmethod
    def set_bad_core_flag(cg: CoreGroup, num_factor: list):
        cg.bad_core = [n==1 for n in num_factor]    # 某个核心的 num_factor 为1，说明其不具备层融合多个tile的能力，本质上在其子图领域做LBL计算，则标记为bad core

    
    def organize_data(self):
        ''' 整理评估的其他数据 '''
        computation_delay_perS, data_loading_delay_perS, data_offloading_delay_perS, ppb_transfer_delay_perS, memory_energy_perS, computation_energy_perS = zip(*self.extra_info)

        self.total_comp_la = sum(computation_delay_perS)
        self.total_loading_la = sum(data_loading_delay_perS)
        self.total_offloading_la = sum(data_offloading_delay_perS)
        self.total_mem_en = sum(memory_energy_perS)
        self.total_comp_en = sum(computation_energy_perS)


    def get_metrics(self):
        """
        返回四个指标: latency, energy, computation, buffer_capacity
        1. latency: 分析模型给出
        2. energy: 分析模型给出(需要buffer的读写能耗模型, 越大的带宽和容量带来的能耗越大)
        3. buffer_capacity: 直接由给定的cg架构给出
        """
        return (self.total_la, self.total_en, self.cg.get_cg_compute(), self.buffer_capacity)


if __name__ == '__main__': 
    c1 = Core(act_buf=Buffer(6, 5), wt_buf=Buffer(5, 5), pe_array=PEA(unroll_power=[3, 1, 4, 2, 2, 0]))  # unroll = [h=8, w=16, oc=16, ic=4, fx=1, fy=1], comp = 8K
    c2 = Core(act_buf=Buffer(7, 5), wt_buf=Buffer(5, 5), pe_array=PEA(unroll_power=[5, 2, 1, 2, 0, 0]))  # unroll = [h=32, w=4, oc=2, ic=4, fx=1, fy=1], comp = 1K
    c3 = Core(act_buf=Buffer(8, 5), wt_buf=Buffer(5, 5), pe_array=PEA(unroll_power=[1, 3, 4, 1, 4, 4])) 
    c4 = Core(act_buf=Buffer(9, 5), wt_buf=Buffer(5, 5), pe_array=PEA(unroll_power=[1, 1, 1, 1, 4, 4])) 
    my_test_cg = CoreGroup(core_num=4, ppb=Buffer(6, 8), cores=[c1, c2, c3, c4])
    
    this_s = Stack(id=1, stack_di={
        1: {
            'op': 'conv',
            'dim': [64, 480, 128, 64, 3, 3]
        },
        2: {
            'op': 'conv',
            'dim': [64, 480, 64, 128, 3, 3]
        }
    })
    
    
    a1, d1, e1 = HyCostModelEvaluation.evaluation_one_core(this_s, c1)
    a2, d2, e2 = HyCostModelEvaluation.evaluation_one_core(this_s, c2)
    a3, d3, e3 = HyCostModelEvaluation.evaluation_one_core(this_s, c3)
    a4, d4, e4 = HyCostModelEvaluation.evaluation_one_core(this_s, c4)
    print('core1', a1, d1, e1/1e6)
    print('core2', a2, d2, e2/1e6)
    print('core3', a3, d3, e3/1e6)
    print('core4', a4, d4, e4/1e6)
    print('strip area:', this_s.get_ifm_area())
    print()

    stack_la, stack_en, _ = HyCostModelEvaluation.evaluation_one_stack(this_s, my_test_cg)
    print(stack_la, stack_en)



