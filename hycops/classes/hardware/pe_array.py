from hycops.classes.hardware.range_parameter import *
import random

def create_random_PEA():
    ''' 生成随机的pe unroll, 满足一定的约束 '''
    
    def check_range(unroll_lst, idx):
        if idx in [0, 1]: # h, w
            return (unroll_lst[idx] in range(*UNROLL_HW_POWER_RG))
        if idx in [2, 3]: # oc, ic
            return (unroll_lst[idx] in range(*UNROLL_OCIC_POWER_RG))
        if idx in [4, 5]: # h, w
            if random.random() < 0.5:   # 有这样的概率，在FX和FY的位置加1
                return (unroll_lst[idx] in range(*UNROLL_FXFY_POWER_RG))
            return False
    
    # 随机生成单核算力总和S
    S = random.randint(*COMP_POWER_RG)
    # 初始化数组，所有元素为0
    numbers = [0] * 6
    # 将S个1随机分配到数组中，确保每个数不超过相应位置上限
    for _ in range(S):
        # 找到所有可以增加的位置
        possible_indices = [i for i in range(6) if check_range(numbers, i)]
        # 随机选择一个位置并增加1
        chosen = random.choice(possible_indices)
        numbers[chosen] += 1
    return numbers

class PEA:
    def __init__(self, unroll_power: list):
        """
        example: [5, 4, 3, 1, 0, 0], means spatial unroll of [h, w, oc, ic, fx, fy] is [32, 16, 8, 2, 1, 1]
        其中每个数的 range in [0, 10]
        """ 
        self.unroll_power = unroll_power
        self.compute_power = sum(self.unroll_power)
        self.unroll = [2**i for i in unroll_power]
        self.compute = 2**self.compute_power

    def check_valid(self):
        assert len(self.unroll) == 6, f"pe array unroll input error: {self.unroll}" # unroll 必须是6个数
        assert COMP_POWER_RG[0] <= self.compute_power <= COMP_POWER_RG[1], f"pe array unroll input error: {self.unroll_power}" # 总算力介于1K-16K

    def get_unroll(self):
        ''' 返回计算阵列的展开维度 '''
        return {
            'h' : self.unroll[0],
            'w' : self.unroll[1],
            'oc': self.unroll[2],
            'ic': self.unroll[3],
            'fx': self.unroll[4],
            'fy': self.unroll[5]
        }
        
    def get_compute(self) -> int:
        ''' 返回算力 '''
        return self.compute
    
    def __str__(self) -> str:
        return f"PEA(unroll={self.unroll},compute={self.compute/1024}K)"

    def __repr__(self) -> str:
        return str(self)


if __name__ == '__main__': 
    array = create_random_PEA()
    print("生成的数组:", array)
    print("数组总和:", sum(array))