from hycops.classes.hardware.core_group import *

# customize your cores
c1 = Core(act_buf=Buffer(6, 8), wt_buf=Buffer(5, 7), pe_array=PEA(unroll_power=[3, 4, 4, 2, 0, 0]))  # unroll = [h=8, w=16, oc=16, ic=4, fx=1, fy=1], comp = 8K
c2 = Core(act_buf=Buffer(7, 8), wt_buf=Buffer(5, 7), pe_array=PEA(unroll_power=[5, 2, 1, 2, 0, 0]))  # unroll = [h=32, w=4, oc=2, ic=4, fx=1, fy=1], comp = 1K
c3 = Core(act_buf=Buffer(8, 8), wt_buf=Buffer(5, 7), pe_array=PEA(unroll_power=[6, 6, 1, 1, 0, 0]))  # unroll = [h=64, w=64, oc=1, ic=1, fx=1, fy=1], comp = 4K

# customize your core_groups
cg1 = CoreGroup(core_num=3, ppb=Buffer(13, 8), cores=[c1, c2, c3])

# user population
user_pop = [cg1]

# check user poop valid
[cg.check_valid() for cg in user_pop]
