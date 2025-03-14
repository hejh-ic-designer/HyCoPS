from hycops.classes.hardware.buffer import Buffer
from hycops.classes.hardware.pe_array import PEA
from hycops.classes.hardware.range_parameter import *

class Core:
    def __init__(self, act_buf: Buffer, wt_buf: Buffer, pe_array: PEA):
        self.act_buf = act_buf
        self.wt_buf = wt_buf
        self.pe_array = pe_array

    def check_valid(self):
        self.pe_array.check_valid()
        assert LB_SIZE_RG[0] <= self.act_buf.size <= LB_SIZE_RG[1], f"buffer size range error: {self.act_buf.size} out of {LB_SIZE_RG}"
        assert LB_SIZE_RG[0] <= self.wt_buf.size <= LB_SIZE_RG[1], f"buffer size range error: {self.wt_buf.size} out of {LB_SIZE_RG}"

    def get_unroll(self):
        return self.pe_array.get_unroll()
    
    def get_compute(self):
        return self.pe_array.get_compute()
    
    def get_act_buf_size(self):
        ''' unit: KB '''
        return self.act_buf.get_buf_size()
    
    def __str__(self):
        return f"Core(act_buf={self.act_buf},wt_buf={self.wt_buf},pe_array={self.pe_array})"
    
    def __repr__(self):
        return str(self)
