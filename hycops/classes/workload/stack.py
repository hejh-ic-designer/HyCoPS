from typing import Generator, Callable, List, Tuple, Any
from math import prod


class Stack:
    """
    parse a stack dict.
    
    stack dict example:
    {
        8: {
            'op': 'conv', 
            'in_resb': True, 
            'dim': [270, 480, 64, 64, 3, 3] # h, w, oc, ic, fx, fy
            }, 
        9: {
            'op': 'conv', 
            'in_resb': True, 
            'dim': [270, 480, 64, 64, 3, 3]
            }
    }
    """
    def __init__(self, id: int, stack_di: dict, new_hw: tuple | None = None):
        """一个stack对象, 解析stack的网络信息

        Args:
            id (int): 当前stack在NN中的序号
            stack_di (dict): 原始dict形式的stack描述
            new_hw (tuple | None): 新的宽和高数据, 用来覆盖stack_di中的数据
        """

        self.id = id
        self.stack_di = self.cover_new_h_w(origin_stack=stack_di, new_hw=new_hw) #这里把yml文件中的格式都转化为输入的new_hw格式,也就是strip格式
        self.stack_len = len(stack_di)
        self.stride_per_layer = [layer.get('stride', 1) for layer in self.stack_di.values()] # 默认stride为1
        self.ich_per_layer = [layer['dim'][3] for layer in self.stack_di.values()]      # 输入通道数, 也就是输入feature map的channel数
        self.och_per_layer = [layer['dim'][2] for layer in self.stack_di.values()]      # 输出通道数, 也就是输出feature map的channel数
        self.in_resb = [layer.get('in_resb', None) for layer in self.stack_di.values()] # 是否在残差块中
        self.kernel_size = [layer['dim'][-1] for layer in self.stack_di.values()]       # 卷积核大小, 也就是卷积核的长宽, fx = fy
        self.ofm_h = [layer['dim'][0] for layer in self.stack_di.values()][-1]          # 输出feature map的高
        self.ofm_w = [layer['dim'][1] for layer in self.stack_di.values()][-1]          # 输出feature map的宽
        self.parse_ifm_and_ofm() # 计算输入和输出feature map的面积（二维没考虑通道）和数据量（考虑通道了）

    def cover_new_h_w(self, origin_stack: dict, new_hw: tuple | None) -> dict:
        """
        cover a stack dict with new H and W.
        only support 'stride = 1' currently.
        """
        if new_hw is None:
            return origin_stack
        else:
            new_di = origin_stack.copy()    # 使用副本，不会更改入参的stack_di
            for d in new_di.values():
                d['dim'][0] = new_hw[0] # H
                d['dim'][1] = new_hw[1] # W
            return new_di

    def get_stack_weight_data_amount(self):
        # element or byte
        weight_data_amount_per_layer = [(layer['dim'][-1] * layer['dim'][-2] * layer['dim'][-3] * layer['dim'][-4]) for layer in self.stack_di.values() if layer['op'] != 'pool']
        weight_data_amount = sum(weight_data_amount_per_layer)
        return weight_data_amount

    def parse_ifm_and_ofm(self):
        # fm area
        self.ofm_area_per_layer = [(layer['dim'][0] * layer['dim'][1]) for layer in self.stack_di.values()]
        self.ifm_area_per_layer = [ofm * stride**2 for ofm, stride in zip(self.ofm_area_per_layer, self.stride_per_layer)]

        # fm data amount, unit: B(elements)
        self.ofm_data_amount_per_layer = [(layer['dim'][0] * layer['dim'][1] * layer['dim'][2]) for layer in self.stack_di.values()]
        self.ifm_data_amount_per_layer = [area * ch for area, ch in zip(self.ifm_area_per_layer, self.ich_per_layer)]

    def get_stack_ifm_and_ofm(self):
        ''' get the first layer's IFM and last layer's OFM data amount'''
        return (self.ifm_data_amount_per_layer[0], self.ofm_data_amount_per_layer[-1])  # (ifm, ofm)

    def get_ema_of_all_fused(self):
        ''' used in feature merging project '''
        return  sum(self.get_stack_ifm_and_ofm())   # 返回stack的第一层IFM和最后一层OFM之和

    def get_ifm_area(self):
        return self.ifm_area_per_layer[0]
        
        
        
    def has_outer_add(self):
        self.ops = [layer['op'] for layer in self.stack_di.values()]
        return ('outer_add' in self.ops)

    def __repr__(self) -> str:
        return f"Stack(id={self.id},len={self.stack_len})"
    
    
    
if __name__ == '__main__':
    # from utils import find_first_true_index
    # resnet18
    # h, w, oc, ic, fx, fy
    st0_di =  { 1: {'op': 'conv', 'stride': 2, 'in_resb': False, 'dim': [112, 112, 64, 3, 7, 7]}, 2: {'op': 'pool', 'stride': 2, 'in_resb': False, 'dim': [56, 56, 64, 64, 3, 3]}}
    st1_di =  { 3: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [56, 56, 64, 64, 3, 3]}, 4: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [56, 56, 64, 64, 3, 3]}}
    st2_di =  { 5: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [56, 56, 64, 64, 3, 3]}, 6: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [56, 56, 64, 64, 3, 3]}}
    st3_di =  { 7: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [28, 28, 128, 64, 3, 3]}, 8: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [28, 28, 128, 128, 3, 3]}}
    st4_di =  { 9: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [28, 28, 128, 128, 3, 3]}, 10: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [28, 28, 128, 128, 3, 3]}}
    st5_di =  {11: {'op': 'conv', 'stride': 2, 'in_resb': True, 'dim': [14, 14, 256, 128, 3, 3]}, 12: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [14, 14, 256, 256, 3, 3]}}
    st6_di =  {13: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [14, 14, 256, 256, 3, 3]}, 14: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [14, 14, 256, 256, 3, 3]}}
    st7_di =  {15: {'op': 'conv', 'stride': 2, 'in_resb': True, 'dim': [7, 7, 512, 512, 3, 3]}, 16: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [7, 7, 512, 512, 3, 3]}}
    st8_di =  {17: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [7, 7, 512, 512, 3, 3]}, 18: {'op': 'conv', 'stride': 1, 'in_resb': True, 'dim': [7, 7, 512, 512, 3, 3]}, 19: {'op': 'pool', 'stride': 1, 'in_resb': False, 'dim': [1, 1, 512, 512, 7, 7]}}
    st9_di =  {20: {'op': 'fc', 'stride': 1, 'in_resb': False, 'dim': [1, 1, 1000, 512, 1, 1]}}

    st0 = Stack(id = 1, stack_di=st0_di)
    st3 = Stack(id = 1, stack_di=st3_di)
    st8 = Stack(id = 1, stack_di=st8_di)
    st9 = Stack(id = 1, stack_di=st9_di)
    print(st3.get_stack_weight_data_amount())
    print(st3.get_ema_of_all_fused())
    print()
    print(st3.ofm_area_per_layer)
    print(st3.och_per_layer)
    print(st3.ofm_data_amount_per_layer)
    print()
    print(st3.ifm_area_per_layer)
    print(st3.ich_per_layer)
    print(st3.ifm_data_amount_per_layer)






