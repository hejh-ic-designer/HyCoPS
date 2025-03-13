from typing import Generator, Callable, List, Tuple, Any
from hycops.classes.stages.Stage import Stage
from hycops.classes.workload.nn import NN
from hycops.classes.ga.fitness_evaluator import StandardFitnessEvaluator
from hycops.classes.ga.genetic_algorithm import GeneticAlgorithm
from utils import parse_user_pop
import logging
logger = logging.getLogger(__name__)


class GAStage(Stage):
    def __init__(self, list_of_callables: List[Callable], nng: List[NN], num_generations, num_individuals, user_pop_path, prob_crossover, prob_mutation, **kwargs):
        """
        固定一个NNG(包括了WL的stack划分方式), strip_h
        需要采样多核架构的设计空间, 然后评估这个nng的延迟/算力/能耗/内存作为fitness函数
        """
        super().__init__(list_of_callables, **kwargs)
        self.fitness_evaluator = StandardFitnessEvaluator(nng=nng)
        self.num_generations = num_generations
        self.num_individuals = num_individuals
        self.user_pop = parse_user_pop(user_pop_path)
        self.prob_crossover = prob_crossover,
        self.prob_mutation  = prob_mutation


    def run(self):
        self.genetic_algorithm = GeneticAlgorithm(
            fitness_evaluator = self.fitness_evaluator,
            num_generations = self.num_generations,
            num_individuals = self.num_individuals,
            user_pop = self.user_pop,
            prob_crossover = self.prob_crossover,
            prob_mutation = self.prob_mutation
            )
        pop, hof, stats = self.genetic_algorithm.run()
        yield hof, (pop, stats)


    def is_leaf(self) -> bool:
        return True

