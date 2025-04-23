# Installation

1. install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) environment

2. clone整个目录文件 (`git clone` this repo)

3. 设置包路径: (出现类似“ModuleNotFoundError: No module named 'hycops'”的错误时, 请使用)
   - 使用`cd` 转到顶层目录
   - 设置包路径，将当前工作目录加入到PYTHONPATH环境变量中, linux/macOS 下使用
    ```bash
    export PYTHONPATH=${PWD}:${PYTHONPATH}
    ```
    如果在Windows下，应使用
    ```bash
    $env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
    ```

# Quick Start

1. `cd` to HYCOPS repo

2. `python run_ga.py` to run experiment

# set your experiment

1. workload is defined at path `hycops/inputs/WL`

2. hardware is defined at path `hycops/inputs/HW`

# customization protocol

## workload

1. 使用 `---` 来切割stack
2. dim 列表必须是六个元素，按照顺序分别代表 h, w, oc, ic, fx, fy
3. 一个stack内，不支持 stride = 2 的卷积层
