from math import sqrt
from hycops.classes.hardware.range_parameter import *


class Buffer:
    def __init__(self, size_power: int, bw_power: int):
        """
        Buffer的大小和带宽都是2的倍数, 所以入参是2的幂指数

        Args:
            size_power (int): range in [0, 13] means [1KB, 8MB], unit: KB
            bw_power (int): range in [6, 13] means [64, 8192], unit: bits/cycle
        """
        self.size_power = size_power    # actual size: 2^size_power KB
        self.bw_power = bw_power        # actual bw: 2^bw_power bits/cycle

    def get_buf_size(self):
        '''  2^size_power KB '''
        return 2**self.size_power
    
    def get_buf_bw(self):
        ''' 2^bw_power bits/cycle '''
        return 2**self.bw_power
    
    def get_read_cost(self):
        return self._estimate_port_cost(size=self.get_buf_size(), bw=(self.get_buf_bw()/8))
        
    @staticmethod
    def _estimate_port_cost(size: int, bw: int, is_read: bool = True) -> float:
        """根据buffer 的size 和bandwidth, 估计read 或write 一次的energy

        Args:
            is_read (str): read or write
            size (int): ? KB
            bw (int): ? B/cc

        Returns:
            float: read cost and write cost

        scale:
            先固定最小的单元: 8KB size and 8B/cc 的 read 单次能量为 4(J)

            然后size 或bw 每翻两倍, port read energy 翻一倍

            最后在 read energy 的基础上增加 20% 得到 write energy
        """
        cost_unit_at_8bw_8size = 4
        read_cost = cost_unit_at_8bw_8size * sqrt((size / 8) * (bw / 8))
        if is_read:
            return read_cost
        else:  # write 能量被认为大于 read能量
            return read_cost * 1.2

    def __str__(self) -> str:
        return f"Buffer(size={self.size},bw={self.bw})"
    
    def __repr__(self) -> str:
        return str(self)
