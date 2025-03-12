import argparse
import logging as _logging
from hycops.classes.stages import *

_logging_level = _logging.INFO
_logging_format = (
    "%(asctime)s - %(name)s.%(funcName)s +%(lineno)s - %(levelname)s - %(message)s"
)
_logging.basicConfig(level=_logging_level, format=_logging_format)
logger = _logging.getLogger(__name__)

# set arg parser
parser = argparse.ArgumentParser(description="Setup hycops inputs")
parser.add_argument( "--nn", metavar="Network name", required=True, help="module name to networks")
parser.add_argument( "--resolution", metavar="AI-isp workload resolution", type=int, nargs='+', required=True, help="Feature Map size [W, H], e.g. 1920 1080" )
parser.add_argument( "--name", metavar="experiment name", required=False, help="Customize your experiment name")
args = parser.parse_args()

# set experiment id
experiment_id = f"{args.nn}--{args.resolution}--{args.name}"


# set stage pipeline
StagesPipeline = [
    PickleSaveStage,
    IterateStripStage,
    WorkloadParserStage,
    IterateNNGStage,
    GAStage,
]
mainstage = MainStage(
    list_of_callables = StagesPipeline,
    workload_path = f"hycops/inputs/WL/{args.nn}.yml",
    resolution = args.resolution,                         # ai-isp流水线处理图片的分辨率(W, H)
    strip_h_range = (60, args.resolution[1]/2, 120),      # 详见IterateStripStage，一个strip的高度的范围, (start, end, step)
    dump_filename_pattern = f"outputs/{experiment_id}/?",
    num_generations = 50,
    num_individuals = 500,
    user_pop_path = f'hycops/inputs/HW/user_pop1.py',
    prob_crossover = 0.3, # probablility to perform corssover, prob_crossover + prob_mutation <= 1.0
    prob_mutation  = 0.7  # probablility to perform mutation,  prob_crossover + prob_mutation <= 1.0


)

# start run
logger.info(f"Runing HyCoPS Experiment: {experiment_id}......")
mainstage.run()



""" stage flow
01. 解析网络: 一个NNG写一个文件即可, 否则手写不方便
02. 插stack, 迭代出若干网络负载, 形成了关于stack的设计空间
03. 迭代strip大小
04. 迭代每一个CG
05. 一个CG的算力迭代, 从小到大迭代若干CG的总算力
06. 固定CG的算力, 使用遗传算法采样不同的CG架构, 采样参数: core_num, core_size, heter/homo, tile_size
07. fitness function evaluation, cross/mute/select
08. 得到帕累托边界 (绘图)
09. 针对帕累托边界的每个点, 获取带宽估计
10. 在延迟-算力的帕累托边界图上使用带宽匹配获取最佳设计点
"""


