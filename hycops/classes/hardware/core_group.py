from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.hardware.buffer import Buffer
from hycops.classes.hardware.core import Core
from hycops.classes.hardware.pe_array import *
from hycops.classes.hardware.range_parameter import *
import random

class CoreGroup:
    def __init__(self, core_num: int, ppb: Buffer, cores: List[Core]):
        self.core_num = core_num
        self.cores = cores
        self.ppb = ppb      # single ping-pang buffer, two ppb is totally same
        self.bad_core = [False for _ in range(core_num)]  # 某个core被标记为bad core时，在变异和交叉时将其删除并重组


    def check_valid(self):
        assert self.core_num == len(self.cores), f"core_num input error, {self.core_num} not equal {len(self.cores)}"
        assert CORE_NUM_RG[0] <= self.core_num <= CORE_NUM_RG[1], f"core_num input error: {self.core_num}"
        assert GB_SIZE_RG[0] <= self.ppb.size <= GB_SIZE_RG[1], f"buffer size range error: {self.ppb.size} out of {GB_SIZE_RG}"
        assert BW_POWER_RG[0] <= self.ppb.bw_power <= BW_POWER_RG[1], f"buffer bw range error: {self.ppb.bw_power} out of {BW_POWER_RG}"
        
        for c in self.cores:
            c.check_valid()


    def get_cg_compute(self):
        ''' 所有核算力相加 '''
        each_core_comp = [c.get_compute() for c in self.cores]
        comp = sum(each_core_comp)
        return comp


    def clear_bad_cores(self):
        ''' 清除当前cg中的bad_core, 并填充新造的核, core_num保持不变 '''
        if not sum(self.bad_core):
            return None  # 没有 bad_cores
        filtered_cores = [x for x, flag in zip(self.cores, self.bad_core) if not flag]
        new_cores = [self.create_core() for _ in range(sum(self.bad_core)-1)]   # 减1
        self.cores = filtered_cores + new_cores + [filtered_cores[0]]     # 清除bad core后，为保证正向优化，增加一个已知的好核
        self.bad_core = [False for _ in range(self.core_num)]


    @staticmethod
    def create_core():
        return Core(
            act_buf=Buffer(size=random.randint(*LB_SIZE_RG), bw_power=random.randint(*BW_POWER_RG)),
            wt_buf=Buffer(size=random.randint(*LB_SIZE_RG), bw_power=random.randint(*BW_POWER_RG)),
            pe_array=PEA(unroll_power=create_random_PEA())
        )

    def __str__(self):
        return f"CoreGroup(core_num={self.core_num},total_compute={self.get_cg_compute()},ppb={self.ppb},cores={self.cores})"
    
    def __repr__(self):
        return str(self)
    
    
