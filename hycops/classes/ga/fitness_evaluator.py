from hycops.classes.workload.nn import NN
from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.hardware.core_group import *
from utils import pickle_deepcopy
from hycops.classes.cost_model.costmodel import HyCostModelEvaluation


class FitnessEvaluator:
    def __init__(self, nng: List[NN]):
        self.nng = nng

    def get_fitness(self):
        raise NotImplementedError


class StandardFitnessEvaluator(FitnessEvaluator):
    """
    给定一个NNG, 一个CoreGroup, 分析其latency, energy, computation, memory_capacity
    """
    def __init__(self, nng):
        super().__init__(nng)
        self.weights = (-1.0, -1.0)         # 遗传算法的weight，负数表示最小化优化
        # self.metrics = ["computation", "energy"]
        self.metrics = ["computation", "latency"]


    def get_fitness(self, cg: CoreGroup, return_hcme = False):
        self.cg = cg
        hcme = HyCostModelEvaluation(
            nng = pickle_deepcopy(self.nng),
            cg = pickle_deepcopy(self.cg),
        )
        hcme.run()
        latency, energy, computation, memory_capacity = hcme.get_metrics()  # 按顺序解包
        
        if not return_hcme:
            # return computation, energy
            return computation, latency
        return computation, latency, hcme



