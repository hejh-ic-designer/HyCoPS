import numpy as np
from hycops.classes.workload.WorkloadParser import WorkloadParser
from utils import parse_user_pop, save_to_pkl, read_pkl
from hycops.visualization.plot_pareto import plot_one_pareto, plot_two_pareto, plot_two_pareto_from_pkl_with_line, plot_two_pareto_with_line, plot_two_buf_en
from hycops.classes.ga.genetic_algorithm import GeneticAlgorithm, CoreGroup_indi
from hycops.classes.ga.fitness_evaluator import StandardFitnessEvaluator

# experiment parameter
resolution = (1920, 1080)
strip_size = (resolution[0], 72)
num_gen = 20
num_pop = 5000
pbcx = 0.3
pbmt = 0.7
l_div_m = 10

# workload, user pop cg dut
wl_p = WorkloadParser(yaml_path='hycops/inputs/WL/ai_isp_1.yml', fixed_stack=True, h_w=strip_size)     # strip size is h_w
user_pop = parse_user_pop(user_pop_path=f'hycops.inputs.HW.user_pop1')


def dndm_ga():
    ''' run ga '''
    nng_dndm  = wl_p.get_workloads()[0]   # dndm
    my_ga1 = GeneticAlgorithm(
        fitness_evaluator=StandardFitnessEvaluator(nng=nng_dndm), 
        num_generations=num_gen, 
        num_individuals=num_pop, 
        user_pop=user_pop,
        prob_crossover=pbcx,
        prob_mutation=pbmt,
        lambda_div_mu=l_div_m
        )
    pop1, hof1, stats1 = my_ga1.run()
    # with open('outputs/ga_hof1.txt', 'w') as f:     # 将hof的metrics写在文件里
    #     for ind in hof1:
    #         ind: CoreGroup_indi
    #         print(f"CoreNum: {ind.core_num}, Metrics(computation, latency): {ind.fitness.values}", file=f)
    # my_ga1.plot_evolution()        # 这里画出每一代的population进化图
    return hof1

def srgan_ga():
    ''' run ga '''
    nng_srgan = wl_p.get_workloads()[1]   # srgan
    my_ga2 = GeneticAlgorithm(
        fitness_evaluator=StandardFitnessEvaluator(nng=nng_srgan), 
        num_generations=num_gen, 
        num_individuals=num_pop, 
        user_pop=user_pop,
        prob_crossover=pbcx,
        prob_mutation=pbmt
        )
    pop2, hof2, stats2 = my_ga2.run()
    # with open('outputs/ga_hof2.txt', 'w') as f:     # 将hof的metrics写在文件里
    #     for ind in hof2:
    #         ind: CoreGroup_indi
    #         print(f"CoreNum: {ind.core_num}, Metrics(computation, latency): {ind.fitness.values}", file=f)
    # my_ga2.plot_evolution()        # 这里画出每一代的population进化图
    return hof2


if __name__ == '__main__': 
    ### Target latency
    N_ISP = 2
    N_NNG = 2
    FRQ = 100      # MHz
    BW_SYS = 80    # bit/cc, (1000MB/s @100MHz)  80bit/cc * 100MHz = 1000 MB/s
    isp_latency = strip_size[0]*strip_size[1]
    Latency_target = int(strip_size[0]*strip_size[1]*3 / ((BW_SYS / 8 - 3*N_ISP) / N_NNG))
    FPS = (FRQ * 1e6 / Latency_target) * (strip_size[1] / resolution[1])
    print(f'FPS: {FPS}, Latency_target: {Latency_target}, isp_latency: {isp_latency}')

    ### set name
    dndm_experiment_id = f'dndm_{strip_size[0]}x{strip_size[1]}_{num_gen}_{num_pop}_{pbcx}_{pbmt}_{l_div_m}'
    srgan_experiment_id = f'srgan_{strip_size[0]}x{strip_size[1]}_{num_gen}_{num_pop}_{pbcx}_{pbmt}_{l_div_m}'
    fig_name = f'dndm_srgan_{strip_size[0]}x{strip_size[1]}_{num_gen}_{num_pop}_{pbcx}_{pbmt}_{l_div_m}'
    pkl_path1 = f'outputs/{dndm_experiment_id}.pickle'
    pkl_path2 = f'outputs/{srgan_experiment_id}.pickle'


    #### run ga
    # dndm_hof = dndm_ga()
    # srgan_hof = srgan_ga()
    # save_to_pkl(pkl_path1, all_cmes=dndm_hof)
    # save_to_pkl(pkl_path2, all_cmes=srgan_hof)
    # plot_two_pareto(hof1=dndm_hof, hof2=srgan_hof, label1='dndm', label2='srgan', save_name=plot_name)


    ### read pkl
    hof_dndm:  list[CoreGroup_indi] = read_pkl(pkl_path1)
    hof_srgan: list[CoreGroup_indi] = read_pkl(pkl_path2)
    print(f'len of dndm hof: {len(hof_dndm)}; len of srgan hof: {len(hof_srgan)}')


    #### plot from hof 
    # plot_two_pareto_with_line(hof_dndm, hof_srgan, 'dndm', 'srgan', save_name=fig_name, y_value=[Latency_target, isp_latency])


    # extract buffer, energy
    err = 15000     # 提取target latency的误差容忍，上下err个cycles区间
    extract_latency_range = (Latency_target-err, Latency_target+err)

    extracted_hof_dndm  = [h for h in hof_dndm  if extract_latency_range[0] < h.fitness.values[1] < extract_latency_range[1]]     # h.fitness.values[1] is latency
    extracted_hof_srgan = [h for h in hof_srgan if extract_latency_range[0] < h.fitness.values[1] < extract_latency_range[1]]

    assert (extracted_hof_dndm != []) and (extracted_hof_srgan != [])       # 不能提取出空的indi
    print(f'len of extracted dndm hof: {len(extracted_hof_dndm)}; len of extracted srgan hof: {len(extracted_hof_srgan)}')

    # 在buffer, energy坐标画出散点
    plot_two_buf_en(hof1=extracted_hof_dndm, hof2=extracted_hof_srgan, label1='dndm', label2='srgan', save_name='EnBuf'+fig_name)
    
    