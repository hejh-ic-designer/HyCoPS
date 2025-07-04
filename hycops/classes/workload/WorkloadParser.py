from utils import load_yaml
from hycops.classes.workload.nn import NN
import logging
logger = logging.getLogger(__name__)


class WorkloadParser:
    def __init__(self, yaml_path: str, fixed_stack: bool, h_w: tuple):
        """
        all_nng的数据结构: List[NNG1, NNG2, ...]
        NNG的数据结构: List[NN1, NN2, ...]
        NN(一个class)的数据结构: List[stack1, stack2, ...]
        """
        self.all_nng = self.parse_workload(yaml_path, fixed_stack, h_w)
        
    def parse_workload(self, yaml_path, fixed_stack, h_w):
        wl_origin: dict = load_yaml(yaml_path) # ai_isp数据流读入，1:None 2:hycops/inputs/WL/base_workload/dndm.yml 3:None
        vls = [i for i in wl_origin.values()] + [None]# 在最后加一个None，转换为list

        # parse nng list
        all_nng = []
        cur_nng = []
        prev_vl = None
        for vl in vls:      # vl要么是None，要么是nn的yml路径 
            if vl != None:
                cur_nng.append(NN(vl, fixed_stack, h_w))
            elif vl == None and prev_vl != None:
                # 只有把两个None之间的所有NN都解析完了，才会把当前的nng添加到all_nng中
                all_nng.append(cur_nng)
                cur_nng=[]
            prev_vl = vl
        return all_nng

    def get_workloads(self):
        logger.info(f'stack num for all nngs: {[[nn.stacks_num for nn in nng] for nng in self.all_nng]}')
        return self.all_nng

    def get_nng_num(self):
        return len(self.all_nng)


if __name__ == '__main__': 
    example = 'hycops/inputs/WL/ai_isp_1.yml'
    wl_p = WorkloadParser(yaml_path=example, fixed_stack=True, h_w=(1920, 64))
    
    # get wl
    wl=wl_p.get_workloads()
    print(wl)
    # get nng num
    wl_num=wl_p.get_nng_num()
    print(wl_num, 'NNGs')
    
    