from hycops.classes.workload.stack import Stack
from utils import parse_yaml_docs


class StackGen:
    def __init__(self, yaml_path):
        pass

    def get_stacks(self):
        pass


class NN:
    def __init__(self, yaml_path, fixed_stack, h_w):
        if fixed_stack:
            # 因为yml文件里只有一个stack，也没有用stack的格式标注，所以在pares_yaml_docs时，直接返回一个stack的list，因此这个stacks list只有一个元素（一个stack）
            stacks = [Stack(id, stack_di, h_w) for id, stack_di in enumerate(parse_yaml_docs(yaml_path))]
        else:
            stacks_generator = StackGen(yaml_path)  # 创建一个 stack generator，迭代stack划分的设计空间 #但是nmd根本就没写
        self.stacks = stacks
        self.stacks_num = len(self.stacks)
        
    def get_stacks(self):
        return self.stacks

    def __str__(self):
        return f"NN(stack_num={self.stacks_num})"

    def __repr__(self):
        return str(self)

