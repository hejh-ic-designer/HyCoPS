from hycops.classes.hardware.core_group import *

# customize your cores
c1  = Core(act_buf=Buffer(10,  8), wt_buf=Buffer(10,  7), pe_array=PEA(unroll_power=[3, 4, 4, 2, 0, 0])) 
c2  = Core(act_buf=Buffer(20,  8), wt_buf=Buffer(120, 7), pe_array=PEA(unroll_power=[5, 2, 1, 2, 0, 0])) 
c3  = Core(act_buf=Buffer(30,  8), wt_buf=Buffer(120, 7), pe_array=PEA(unroll_power=[6, 5, 1, 1, 0, 0])) 
c4  = Core(act_buf=Buffer(50,  8), wt_buf=Buffer(210, 7), pe_array=PEA(unroll_power=[2, 1, 5, 4, 0, 0]))  
c5  = Core(act_buf=Buffer(90,  8), wt_buf=Buffer(10,  7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c6  = Core(act_buf=Buffer(100, 8), wt_buf=Buffer(130, 7), pe_array=PEA(unroll_power=[2, 1, 4, 5, 0, 0]))  
c7  = Core(act_buf=Buffer(120, 8), wt_buf=Buffer(10,  7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c8  = Core(act_buf=Buffer(140, 8), wt_buf=Buffer(140, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c9  = Core(act_buf=Buffer(160, 8), wt_buf=Buffer(510, 7), pe_array=PEA(unroll_power=[1, 2, 5, 5, 0, 0]))  
c10 = Core(act_buf=Buffer(190, 8), wt_buf=Buffer(10,  7), pe_array=PEA(unroll_power=[2, 1, 5, 4, 0, 0]))  
c11 = Core(act_buf=Buffer(300, 8), wt_buf=Buffer(610, 7), pe_array=PEA(unroll_power=[2, 1, 5, 5, 0, 0]))  
c12 = Core(act_buf=Buffer(490, 8), wt_buf=Buffer(170, 7), pe_array=PEA(unroll_power=[2, 1, 4, 5, 0, 0]))  
c13 = Core(act_buf=Buffer(510, 8), wt_buf=Buffer(10,  7), pe_array=PEA(unroll_power=[1, 1, 5, 5, 0, 0]))  
c14 = Core(act_buf=Buffer(710, 8), wt_buf=Buffer(180, 7), pe_array=PEA(unroll_power=[2, 1, 3, 5, 0, 0]))  
c15 = Core(act_buf=Buffer(910, 8), wt_buf=Buffer(190, 7), pe_array=PEA(unroll_power=[1, 2, 5, 5, 0, 0]))  
c16 = Core(act_buf=Buffer(999, 8), wt_buf=Buffer(100, 7), pe_array=PEA(unroll_power=[1, 1, 4, 5, 0, 0]))  


# customize your core_groups
cg1  = CoreGroup(core_num=16, ppb=Buffer(2000,  17), cores=[c5, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])
cg2  = CoreGroup(core_num=9 , ppb=Buffer(10100,  9), cores=[c1, c6, c7, c11, c12, c13, c14, c15, c16])
cg3  = CoreGroup(core_num=16, ppb=Buffer(12000, 16), cores=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])
cg4  = CoreGroup(core_num=12, ppb=Buffer(22000, 15), cores=[c1, c2, c3, c8, c9, c10, c11, c12, c13, c14, c15, c16])
cg5  = CoreGroup(core_num=16, ppb=Buffer(2200,  14), cores=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])
cg6  = CoreGroup(core_num=16, ppb=Buffer(600,   13), cores=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])
cg7  = CoreGroup(core_num=16, ppb=Buffer(20200, 12), cores=[c1, c2, c3, c4, c1, c6, c7, c8, c9, c10, c10, c12, c13, c11, c15, c16])
cg8  = CoreGroup(core_num=16, ppb=Buffer(62000, 11), cores=[c4, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])
cg9  = CoreGroup(core_num=13, ppb=Buffer(6000,  10), cores=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c14, c15, c16])
cg10 = CoreGroup(core_num=13, ppb=Buffer(43000,  8), cores=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c16])


# user population
user_pop = [cg1, cg2, cg3, cg4, cg5, cg6, cg7, cg8, cg9, cg10]

# check user poop valid
[cg.check_valid() for cg in user_pop]
