import matplotlib.pyplot as plt
import numpy as np
import os
from utils import read_pkl




def plot_two_pareto(hof1, hof2, label1, label2, save_name='plot_two_pareto'):
    front1 = np.array([ind.fitness.values for ind in hof1])
    front2 = np.array([ind.fitness.values for ind in hof2])

    # 可视化帕累托前沿
    plt.scatter(front1[:, 0], front1[:, 1], c="b", label=label1, alpha=0.6, marker='o')
    plt.scatter(front2[:, 0], front2[:, 1], c="r", label=label2, alpha=0.6, marker='s')
    plt.xscale('log')   # 对数坐标
    plt.yscale('log')   # 对数坐标
    plt.xlabel("Computing Power")
    plt.ylabel("Latency")
    plt.title("Pareto Front")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # 双对数坐标范围优化
    plt.xlim(min(front1[:,0].min(), front2[:,0].min())*0.8, 
            max(front1[:,0].max(), front2[:,0].max())*1.2)
    plt.ylim(min(front1[:,1].min(), front2[:,1].min())*0.8, 
            max(front1[:,1].max(), front2[:,1].max())*1.2)

    fig_path=f'outputs/{save_name}.png'
    os.makedirs(os.path.dirname(fig_path), exist_ok=True)
    plt.savefig(fig_path, dpi=800, bbox_inches='tight')
    print(f'Done!, png file at {fig_path}')
    plt.show()


def plot_one_pareto(hof, label, save_name='plot_one_pareto'):
    front = np.array([ind.fitness.values for ind in hof])

    # 可视化帕累托前沿
    plt.scatter(front[:, 0], front[:, 1], c="b", label=label, alpha=0.6, marker='o')
    plt.xscale('log')   # 对数坐标
    plt.yscale('log')   # 对数坐标
    plt.xlabel("Computing Power")
    plt.ylabel("Latency")
    plt.title("Pareto Front")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    fig_path=f'outputs/{save_name}.png'
    os.makedirs(os.path.dirname(fig_path), exist_ok=True)
    plt.savefig(fig_path, dpi=800, bbox_inches='tight')
    print(f'Done!, png file at {fig_path}')
    plt.show()


def plot_two_pareto_with_line(hof1, hof2, label1, label2, save_name='plot_two_pareto_with_line', y_value: list=None):
    front1 = np.array([ind.fitness.values for ind in hof1])
    front2 = np.array([ind.fitness.values for ind in hof2])

    # 可视化帕累托前沿
    plt.figure(figsize=(10, 6))
    sc1 = plt.scatter(front1[:, 0], front1[:, 1], c="b", label=label1, alpha=0.6, marker='o')
    sc2 = plt.scatter(front2[:, 0], front2[:, 1], c="r", label=label2, alpha=0.6, marker='s')
    
    # 添加水平线并找交点
    if y_value is not None:
        # 绘制水平线
        hline = plt.axhline(y=y_value[0], color="g", linestyle="--", linewidth=2, label="Target Latency")
        hline = plt.axhline(y=y_value[1], color="y", linestyle="--", linewidth=2, label="ISP Latency")
        
        # 寻找交点 (允许一定误差范围)
        tolerance = 0.1  # 相对误差容忍度
        mask1 = np.isclose(front1[:, 1], y_value[0], rtol=tolerance)
        mask2 = np.isclose(front2[:, 1], y_value[0], rtol=tolerance)
        
        # 绘制交点标记
        if np.any(mask1):
            plt.scatter(front1[mask1, 0], front1[mask1, 1], 
                       facecolors='none', edgecolors='k', s=200, marker='o', 
                       label=f'Intersection ({label1})')
        if np.any(mask2):
            plt.scatter(front2[mask2, 0], front2[mask2, 1], 
                       facecolors='none', edgecolors='k', s=200, marker='s',
                       label=f'Intersection ({label2})')


    # 坐标设置
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Computing Power")
    plt.ylabel("Latency")
    plt.title("Pareto Front with Target Line")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # 双对数坐标范围优化
    plt.xlim(min(front1[:,0].min(), front2[:,0].min())*0.8, 
            max(front1[:,0].max(), front2[:,0].max())*1.2)
    plt.ylim(min(front1[:,1].min(), front2[:,1].min())*0.8, 
            max(front1[:,1].max(), front2[:,1].max())*1.2)
    
    # 合并图例
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # 去重
    plt.legend(by_label.values(), by_label.keys(), loc='best')

    fig_path=f'outputs/{save_name}.png'
    os.makedirs(os.path.dirname(fig_path), exist_ok=True)
    plt.savefig(fig_path, dpi=800, bbox_inches='tight')
    print(f'Done!, png file at {fig_path}')
    plt.show()


def plot_two_pareto_from_pkl_with_line(pkl_path1, label1, pkl_path2, label2, save_name, y_value):
    hof_dndm = read_pkl(pkl_path1)
    hof_srgan = read_pkl(pkl_path2)
    plot_two_pareto_with_line(hof1=hof_dndm, hof2=hof_srgan, label1=label1, label2=label2, save_name=save_name, y_value=y_value)


def plot_two_buf_en(hof1, hof2, label1, label2, save_name='plot_two_pareto'):
    twod_array1 = np.array([(ind.buffer, ind.energy) for ind in hof1])
    twod_array2 = np.array([(ind.buffer, ind.energy) for ind in hof2])

    # 可视化帕累托前沿
    plt.scatter(twod_array1[:, 0], twod_array1[:, 1], c="b", label=label1, alpha=0.6, marker='o')
    plt.scatter(twod_array2[:, 0], twod_array2[:, 1], c="r", label=label2, alpha=0.6, marker='s')
    plt.xscale('log')   # 对数坐标
    plt.yscale('log')   # 对数坐标
    plt.xlabel("Buffer Capacity")
    plt.ylabel("Energy")
    plt.title("Buffer Capacity -- Energy")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # 双对数坐标范围优化
    plt.xlim(min(twod_array1[:,0].min(), twod_array2[:,0].min())*0.8, 
            max(twod_array1[:,0].max(), twod_array2[:,0].max())*1.2)
    plt.ylim(min(twod_array1[:,1].min(), twod_array2[:,1].min())*0.8, 
            max(twod_array1[:,1].max(), twod_array2[:,1].max())*1.2)

    fig_path=f'outputs/{save_name}.png'
    os.makedirs(os.path.dirname(fig_path), exist_ok=True)
    plt.savefig(fig_path, dpi=800, bbox_inches='tight')
    print(f'Done!, png file at {fig_path}')
    plt.show()
