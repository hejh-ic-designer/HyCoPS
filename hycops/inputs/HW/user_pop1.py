from hycops.classes.hardware.core_group import *

# customize your cores
c1  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[3, 4, 4, 2, 0, 0])) 
c2  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[5, 2, 1, 2, 0, 0])) 
c3  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[6, 5, 1, 1, 0, 0])) 
c4  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c5  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c6  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c7  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c8  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c9  = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c10 = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c11 = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c12 = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c13 = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c14 = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c15 = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c16 = Core(act_buf=Buffer(10, 8), wt_buf=Buffer(10, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  

# customize your core_groups
cg1 = CoreGroup(core_num=16, ppb=Buffer(17, 17), cores=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])

# user population
user_pop = [cg1, cg1, cg1, cg1, cg1, cg1, cg1, cg1, cg1, cg1]

# check user poop valid
[cg.check_valid() for cg in user_pop]
