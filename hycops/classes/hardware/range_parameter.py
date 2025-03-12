# design space range parameter
# 以下均为闭区间

CORE_NUM_RG = (1, 16)

LB_SIZE_POWER_RG = (1, 10)     # for act_buf and wt_buf, [2KB, 1MB]

GB_SIZE_POWER_RG = (9, 17)    # for ppb, [512KB, 128MB]
BW_POWER_RG = (8, 17)         # for ppb, [256bit/cc, 16KB/cc], LB的BW无用

UNROLL_HW_POWER_RG = (0, 6)
UNROLL_OCIC_POWER_RG = (0, 7)
UNROLL_FXFY_POWER_RG = (0, 2)

COMP_POWER_RG = (10, 13)    # [1K, 8K]



