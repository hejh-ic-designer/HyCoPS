# 用来测试基因型的确定
from hycops.classes.hardware.core_group import *



core1 = Core(act_buf=Buffer(size_power=10, bw_power=20), wt_buf=Buffer(size_power=20, bw_power=10), pe_array=PEA([32, 16, 2, 2, 1, 1]))
core2 = Core(act_buf=Buffer(size_power=10, bw_power=20), wt_buf=Buffer(size_power=20, bw_power=10), pe_array=PEA([32, 16, 2, 2, 1, 1]))
core3 = Core(act_buf=Buffer(size_power=10, bw_power=20), wt_buf=Buffer(size_power=20, bw_power=10), pe_array=PEA([32, 16, 2, 2, 1, 1]))

core_lst = [core1, core2, core3]
my_individual = CoreGroup(core_num=3, ppb1=Buffer(10, 100), ppb2=Buffer(20, 200), cores=core_lst)



