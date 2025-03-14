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
num_pop = 10000
pbcx = 0.3
pbmt = 0.7
l_div_m = 10

# workload, user pop cg dut
wl_p = WorkloadParser(yaml_path='hycops/inputs/WL/ai_isp_1.yml', fixed_stack=True, h_w=strip_size)     # strip size is h_w
user_pop = parse_user_pop(user_pop_path=f'hycops.inputs.HW.user_pop1')


def run_dndm_ga():
    ''' run ga '''
    print('running GA of dndm...')
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
    my_ga1.plot_evolution()        # 这里画出每一代的population进化图
    return hof1

def run_srgan_ga():
    ''' run ga '''
    print('running GA of srgan...')
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
    # my_ga2.plot_evolution()        # 这里画出每一代的population进化图
    return hof2


if __name__ == '__main__': 
    ### Target latency
    N_ISP = 2
    N_NNG = 2
    FRQ = 100      # MHz
    BW_SYS = 90    # bit/cc, (1000MB/s @100MHz)  80bit/cc * 100MHz = 1000 MB/s
    isp_latency = strip_size[0]*strip_size[1]
    Latency_target = int(strip_size[0]*strip_size[1]*3 / ((BW_SYS / 8 - 3*N_ISP) / N_NNG))
    FPS = (FRQ * 1e6 / Latency_target) * (strip_size[1] / resolution[1])
    print(f'FPS: {FPS}, Latency_target: {Latency_target}, isp_latency: {isp_latency}, bubble rate: {(Latency_target-isp_latency)*100/Latency_target}%')

    ### set name
    dndm_experiment_id = f'dndm_{strip_size[0]}x{strip_size[1]}_{num_gen}_{num_pop}_{pbcx}_{pbmt}_{l_div_m}'
    srgan_experiment_id = f'srgan_{strip_size[0]}x{strip_size[1]}_{num_gen}_{num_pop}_{pbcx}_{pbmt}_{l_div_m}'
    fig_name = f'dndm_srgan_{strip_size[0]}x{strip_size[1]}_{num_gen}_{num_pop}_{pbcx}_{pbmt}_{l_div_m}'
    pkl_path1 = f'outputs/{dndm_experiment_id}.pickle'
    pkl_path2 = f'outputs/{srgan_experiment_id}.pickle'
    txt_path1 = f'outputs/{dndm_experiment_id}.txt'
    txt_path2 = f'outputs/{srgan_experiment_id}.txt'


    # ### run ga
    # dndm_hof = run_dndm_ga()
    # srgan_hof = run_srgan_ga()
    # save_to_pkl(pkl_path1, all_cmes=dndm_hof)
    # save_to_pkl(pkl_path2, all_cmes=srgan_hof)


    ### read pkl
    dndm_hof_from_pkl:  list[CoreGroup_indi] = read_pkl(pkl_path1)
    srgan_hof_from_pkl: list[CoreGroup_indi] = read_pkl(pkl_path2)
    print(f'len of dndm hof: {len(dndm_hof_from_pkl)}; len of srgan hof: {len(srgan_hof_from_pkl)}')


    # #### write Metrics in file
    # with open(txt_path1, 'w') as f:     # 将hof的metrics写在文件里
    #     for ind in dndm_hof_from_pkl:
    #         ind: CoreGroup_indi
    #         print(f"CoreNum: {ind.core_num}, Metrics(computation, latency): {ind.fitness.values}", file=f)
    # with open(txt_path2, 'w') as f:     # 将hof的metrics写在文件里
    #     for ind in srgan_hof_from_pkl:
    #         ind: CoreGroup_indi
    #         print(f"CoreNum: {ind.core_num}, Metrics(computation, latency): {ind.fitness.values}", file=f)
    # print('print to file Done!')


    # extract buffer, energy
    err = 7000     # 提取target latency的误差容忍，上下err个cycles区间
    extract_latency_range = (Latency_target-err, Latency_target+err)
    extracted_hof_dndm  = [h for h in dndm_hof_from_pkl  if extract_latency_range[0] < h.fitness.values[1] < extract_latency_range[1]]     # h.fitness.values[1] is latency
    extracted_hof_srgan = [h for h in srgan_hof_from_pkl if extract_latency_range[0] < h.fitness.values[1] < extract_latency_range[1]]    
    assert (extracted_hof_dndm != []) and (extracted_hof_srgan != [])       # 不能提取出空的indi
    print(f'err_rate: {err*100/Latency_target}, len of extracted dndm hof: {len(extracted_hof_dndm)}; len of extracted srgan hof: {len(extracted_hof_srgan)}')


    # pick the best CG
    core_num_dndm = [h.core_num for h in extracted_hof_dndm]
    core_num_srgan = [h.core_num for h in extracted_hof_srgan]
    print(f'core_num_dndm: {core_num_dndm}')
    print(f'core_num_srgan: {core_num_srgan}')
    sorted_dndm  = sorted(extracted_hof_dndm, key=lambda x: x.buffer)
    sorted_srgan = sorted(extracted_hof_srgan, key=lambda x: x.buffer)
    best_dndm_cg = sorted_dndm[0]
    best_srgan_cg = sorted_srgan[0]
    print(f'best dndm cg: {best_dndm_cg}')
    print(f'best srgan cg: {best_srgan_cg}')

    #### plot from pkl
    plot_two_pareto_with_line(dndm_hof_from_pkl, srgan_hof_from_pkl, 'dndm', 'srgan', save_name=fig_name, y_value=[Latency_target, isp_latency])
    # 在buffer, energy坐标画出散点
    plot_two_buf_en(hof1=extracted_hof_dndm, hof2=extracted_hof_srgan, label1='dndm', label2='srgan', save_name='EnBuf'+fig_name)



# todo
# 因为目前buffer的容量和带宽没有关系，导致随机采样到的buffer参数没有约束
# 如果，设置为越大的容量，拥有越大的带宽，那么，小容量的ppb的延迟会很高，相应的能耗低，大容量的ppb其延迟则取决于算力，能耗高，可以画出屋顶曲线？
# 另外，LB的延迟和能耗并没有考虑，如果考虑act_buf的能耗，那么越大的buf导致越高的能耗和越低的延迟
