import random
from hycops.classes.hardware.core_group import *
from hycops.classes.hardware.range_parameter import *
from hycops.classes.hardware.pe_array import *
from hycops.classes.ga.fitness_evaluator import StandardFitnessEvaluator
from hycops.classes.ga.statistics_evaluator import StatisticsEvaluator
from deap import algorithms, base, creator, tools


class CoreGroup_indi(CoreGroup):
    def __init__(self, core_num, ppb, cores):
        super().__init__(core_num, ppb, cores)
        self.fitness = creator.FitnessMulti()


class GeneticAlgorithm:
    def __init__(self, 
        fitness_evaluator, 
        num_generations, 
        num_individuals,
        user_pop=[],
        prob_crossover=0.4,
        prob_mutation=0.6
    ) -> None:
        self.fitness_evaluator = fitness_evaluator  # class to evaluate fitness of each indiviual
        self.num_generations = num_generations  # number of generations
        self.num_individuals = num_individuals  # number of individuals in initial generation
        self.para_mu = int(num_individuals / 5)  # number of indiviuals taken from previous generation
        self.para_lambda = num_individuals  # number of indiviuals in generation
        self.user_pop = user_pop
        self.prob_crossover = prob_crossover  # probablility to perform corssover, prob_crossover + prob_mutation <= 1.0
        self.prob_mutation  = prob_mutation   # probablility to perform mutation,  prob_crossover + prob_mutation <= 1.0

        # class to track statistics of certain generations
        self.statistics_evaluator = StatisticsEvaluator(self.fitness_evaluator)
        self.create_ga()


    def create_ga(self):
        # 定义适应度函数和个体基因型
        creator.create("FitnessMulti", base.Fitness, weights=self.fitness_evaluator.weights)
        creator.create("Individual", CoreGroup_indi, fitness=creator.FitnessMulti)

        # 初始化工具箱
        self.toolbox = base.Toolbox()
        self.hof = tools.ParetoFront()  # initialize Hall-of-Fame as Pareto Front
        self.toolbox.register("individual", self.create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        # 注册评估函数
        self.toolbox.register("evaluate", self.fitness_evaluator.get_fitness)

        # 注册遗传算子
        self.toolbox.register("mate", self.mate)
        self.toolbox.register("mutate", self.mutate)
        self.toolbox.register("select", tools.selNSGA2)
        
        # populate random initial generation
        self.pop = self.toolbox.population(n=self.num_individuals)  # pop is current population


        # replace sub part of initial generation with user provided individuals
        for indv_index in range(len(self.user_pop)):
            self.pop[indv_index] = self._convert_to_indi(self.user_pop[indv_index])

            # don't bias initial population too much, when it comes to 25%, break
            if indv_index >= self.num_individuals / 4:
                break


    def run(self):
        # 定义统计函数
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg (" + ", ".join(self.fitness_evaluator.metrics) + ")", self.statistics_evaluator.get_avg,)
        stats.register("std (" + ", ".join(self.fitness_evaluator.metrics) + ")", self.statistics_evaluator.get_std,)
        stats.register("min (" + ", ".join(self.fitness_evaluator.metrics) + ")", self.statistics_evaluator.get_min,)
        stats.register("max (" + ", ".join(self.fitness_evaluator.metrics) + ")", self.statistics_evaluator.get_max,)

        # 新增虚拟统计项：触发保存种群并返回0
        stats.register("_dummy", lambda _: (
            self.statistics_evaluator.append_generation(self.pop), 
            0  # 返回一个占位值
        )[1])
    
        # 执行(mu+lambda)进化算法
        algorithms.eaMuPlusLambda(
            population=self.pop,
            toolbox=self.toolbox,
            mu=self.para_mu,
            lambda_=self.para_lambda,
            cxpb=self.prob_crossover,
            mutpb=self.prob_mutation,
            ngen=self.num_generations,
            stats=stats,
            halloffame=self.hof,
            verbose=True
        )
        
        return self.pop, self.hof, stats

    
    def create_individual(self):
        core_lst = [CoreGroup.create_core() for _ in range(random.randint(*CORE_NUM_RG))]
        return creator.Individual(
            core_num=len(core_lst),
            ppb=Buffer(size_power=random.randint(*GB_SIZE_POWER_RG), bw_power=random.randint(*BW_POWER_RG)),
            cores=core_lst
            )
    
    
    @staticmethod
    def _convert_to_indi(cg):
        ''' 将CoreGroup对象转换为CoreGroup_indi对象 '''
        attrs = vars(cg)
        return CoreGroup_indi(attrs['core_num'], attrs['ppb'], attrs['cores'])


    def mate(self, indi1: CoreGroup_indi, indi2: CoreGroup_indi, indpd=0.7):
        """
        定义CoreGroup个体的交叉行为:
        1. 有indpd的概率, ppb将会互换交叉
        2. 有indpd的概率, core将会随机交叉
        """
        indi1.clear_bad_cores()
        indi2.clear_bad_cores()
        
        if random.random() < indpd:
            # ppb 交叉，互换即可
            indi1.ppb, indi2.ppb = indi2.ppb, indi1.ppb

        if random.random() < indpd:
            # core 交叉，core_num 各自保持不变，core 随机交叉
            shared_core_lst = indi1.cores + indi2.cores
            random.shuffle(shared_core_lst)
            indi1.cores = shared_core_lst[:indi1.core_num]   # 前 indi1.core_num 个作为indi1的新cores
            indi2.cores = shared_core_lst[-indi2.core_num:]  # 后 indi2.core_num 个作为indi2的新cores

        return indi1, indi2

    def mutate(self, indi: CoreGroup_indi, indpd=0.5):
        """
        定义CoreGroup个体的变异行为:
        1. 有indpd的概率, core_num将会变异
        2. 有indpd的概率, ppb将会变异
        3. 无论如何, core_size将会变异
        """
        indi.clear_bad_cores()
        
        if random.random() < indpd:
            # 有indpd的概率，核的数量数量不变，重置所有核
            indi.cores += [CoreGroup.create_core() for _ in range(indi.core_num)]
        else:
            # 有(1-indpd)的概率，改变核的数量
            if random.random() < 0.7:
                # 增加核的数量
                new_core_num = random.randint(indi.core_num, CORE_NUM_RG[1])
                indi.cores += [CoreGroup.create_core() for _ in range(new_core_num-indi.core_num)]
                indi.core_num = new_core_num
            else:
                # 减小核的数量
                new_core_num = random.randint(CORE_NUM_RG[0], indi.core_num)
                cores = indi.cores
                random.shuffle(cores)
                indi.cores = cores[:new_core_num]
                indi.core_num = new_core_num

        # ping-pang buffer 变异, 和上面的变异是互相独立的
        if random.random() < indpd:
            indi.ppb = Buffer(size_power=random.randint(*GB_SIZE_POWER_RG), bw_power=random.randint(*BW_POWER_RG))

        return (indi,)

    def plot_evolution(self):
        self.statistics_evaluator.plot_evolution()

    def plot_population(self, pop):
        self.statistics_evaluator.plot_population(pop)


if __name__ == '__main__':     
    import numpy as np
    from hycops.classes.workload.WorkloadParser import WorkloadParser
    # user pop cg dut
    c1 = Core(act_buf=Buffer(6, 8), wt_buf=Buffer(5, 7), pe_array=PEA(unroll_power=[3, 4, 4, 2, 0, 0]))  # unroll = [h=8, w=16, oc=16, ic=4, fx=1, fy=1], comp = 8K
    c2 = Core(act_buf=Buffer(7, 8), wt_buf=Buffer(5, 7), pe_array=PEA(unroll_power=[5, 2, 1, 2, 0, 0]))  # unroll = [h=32, w=4, oc=2, ic=4, fx=1, fy=1], comp = 1K
    c3 = Core(act_buf=Buffer(8, 8), wt_buf=Buffer(5, 7), pe_array=PEA(unroll_power=[6, 6, 1, 0, 0, 0]))  # unroll = [h=64, w=64, oc=1, ic=1, fx=1, fy=1], comp = 4K
    cg_dut = CoreGroup(core_num=3, ppb=Buffer(13, 8), cores=[c1, c2, c3])
    
    # workload
    wl_p = WorkloadParser(yaml_path='hycops/inputs/WL/ai_isp_1.yml', fixed_stack=True, h_w=(1920, 540))     # strip size is h_w
    nng_sesr  = wl_p.get_workloads()[0]   # sesr
    nng_srgan = wl_p.get_workloads()[1]   # srgan

    # ga
    my_ga1 = GeneticAlgorithm(fitness_evaluator=StandardFitnessEvaluator(nng=nng_sesr), num_generations=30, num_individuals=3000, user_pop=[cg_dut])
    # pop1, hof1, stats1 = my_ga1.run()
    my_ga2 = GeneticAlgorithm(fitness_evaluator=StandardFitnessEvaluator(nng=nng_srgan), num_generations=20, num_individuals=5000, user_pop=[cg_dut])
    pop2, hof2, stats2 = my_ga2.run()


    # 显示进化
    # my_ga1.plot_evolution()        # 这里画出每一代的population进化图
    # my_ga.plot_population(pop)  # 这里的pop是最后一代中选出的帕累托最优个体，数量为500/10 = 50

    # 记录 hof 在文件中
    # with open('outputs/ga_hof1.txt', 'w') as f:
    #     for ind in hof1:
    #         ind: CoreGroup_indi
    #         print(f"CoreNum: {ind.core_num}, Computation: {ind.get_cg_compute()}, Metrics: {ind.fitness.values}", file=f)

    with open('outputs/ga_hof2.txt', 'w') as f:
        for ind in hof2:
            ind: CoreGroup_indi
            print(f"CoreNum: {ind.core_num}, Computation: {ind.get_cg_compute()}, Metrics: {ind.fitness.values}", file=f)

    # 可视化帕累托前沿
    import matplotlib.pyplot as plt
    # front1 = np.array([ind.fitness.values for ind in hof1])
    front2 = np.array([ind.fitness.values for ind in hof2])
    # plt.scatter(front1[:, 0], front1[:, 1], c="b", label='sesr' , alpha=0.6, marker='o')
    plt.scatter(front2[:, 0], front2[:, 1], c="r", label='srgan', alpha=0.6, marker='o')
    plt.xscale('log')   # 对数坐标
    plt.yscale('log')   # 对数坐标
    plt.xlabel("Computing Power")
    plt.ylabel("Latency")
    plt.title("Pareto Front")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

# 猜想：一个CG中有很多bad core，这些bad core不能显著降低延迟，所以核数量被刷掉了
# 在cme评估中，评估出当前CG中哪些core是bad core，在cg属性中用list标注出来，在变异算子中，把所有bad core变异掉
