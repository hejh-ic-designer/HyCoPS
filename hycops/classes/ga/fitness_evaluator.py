from hycops.classes.workload.nn import NN
from typing import Generator, Callable, List, Tuple, Any
from utils import pickle_deepcopy
from hycops.classes.cost_model.costmodel import HyCostModelEvaluation
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from hycops.classes.ga.genetic_algorithm import CoreGroup_indi

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
        self.metrics = ["computation", "latency"]


    def get_fitness(self, cg: 'CoreGroup_indi', return_hcme = False):
        hcme = HyCostModelEvaluation(
            nng = pickle_deepcopy(self.nng),
            cg = pickle_deepcopy(cg),
        )
        hcme.run()
        latency, energy, computation, memory_capacity = hcme.get_metrics()  # 按顺序解包

        cg.energy = energy
        cg.buffer = memory_capacity
        
        if not return_hcme:
            return computation, latency
        return computation, latency, hcme



