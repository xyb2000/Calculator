# Calculator

[![Verification](https://github.com/xyb2000/Calculator/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/xyb2000/Calculator/actions/workflows/ci.yml)

Python 编写的 ROS 计算器：包含发布/订阅、`add_two_ints` 服务与客户端、可组合 launch、真实通信测试和中英文测试报告。运算逻辑与 ROS 适配层分离，便于阅读、调试和复用。

主实现支持 **ROS 2 Humble / Ubuntu 22.04** 与 **ROS 2 Jazzy / Ubuntu 24.04**。仓库和 ROS 包保留题目要求的名称 `Calculator`，Python 模块名为 `calculator`。大写包名会触发 ROS 命名规范警告；这是保留题目拼写的有意选择，不影响构建。

题目混用了 Humble 链接与 ROS 1 `rostest` 术语。主实现使用 ROS 2 的 `pytest + launch_testing`；[独立 ROS 1 兼容包](compat/ros1/Calculator/README.md) 提供真正的 Noetic `rostest`。两种构建系统分别运行，详见[要求对照](docs/requirements.md)。

## 快速开始

以下命令在 Ubuntu Bash 中执行。选用与 Ubuntu 匹配的发行版：22.04 使用 `humble`，24.04 使用 `jazzy`。应已按 [ROS 官方安装说明](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html) 安装相应 ROS 2。

```bash
# Ubuntu 24.04；Ubuntu 22.04 请改为 humble
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install python3-colcon-common-extensions python3-rosdep python3-pytest \
  ros-${ROS_DISTRO}-example-interfaces \
  ros-${ROS_DISTRO}-launch-testing ros-${ROS_DISTRO}-launch-testing-ros

mkdir -p ~/calculator_ws/src
cd ~/calculator_ws
git clone https://github.com/xyb2000/Calculator.git src/Calculator
# rosdep 首次使用需先执行一次 sudo rosdep init，然后执行 rosdep update。
rosdep install --from-paths src/Calculator --ignore-src -r -y
colcon build --packages-select Calculator --symlink-install
source install/setup.bash
ros2 launch Calculator demo.launch.py a:=12 b:=30
```

预期看到发布者 `Publishing`、订阅者 `I heard`，以及客户端 `Result: 12 + 30 = 42`。按 Ctrl+C 退出。每个新终端都需 source ROS 和工作空间。

## 单独运行与配置

```bash
# 终端 A
ros2 run Calculator add_two_ints_server
# 终端 B
ros2 run Calculator add_two_ints_client 12 30
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts '{a: 12, b: 30}'

# 只运行话题示例；使用命名空间与启动参数
ros2 launch Calculator topics.launch.py namespace:=demo publish_period:=0.2 'prefix:=Demo: '
ros2 topic echo /demo/chatter

# 只启动服务，稍后手动调用；所有节点都支持标准 ROS remapping
ros2 launch Calculator service.launch.py namespace:=demo start_client:=false
ros2 run Calculator add_two_ints_client -7 12 --ros-args -r __ns:=/demo
ros2 run Calculator add_two_ints_client 1 2 --discovery-timeout 1 --request-timeout 2
```

`chatter` 使用 `std_msgs/msg/String`，默认每 0.5 秒发布 `Hello World: <递增计数>`，QoS 为 reliable/volatile、深度 10。`publish_period` 和 `prefix` 为启动时只读参数。

服务使用标准 `example_interfaces/srv/AddTwoInts`：`a`、`b`、`sum` 均为有符号 int64。**溢出明确采用 64 位补码回绕**，例如最大值加 1 得到最小值，并记录 WARN；未溢出时就是普通整数加法。CLI 拒绝超出 int64 的输入和无效超时。退出码：成功 `0`，发现/响应失败或中断 `1`，参数错误 `2`。响应超时只停止本地等待，不能撤销服务端已经开始的计算。

## 验证

```bash
cd ~/calculator_ws/src/Calculator
# 不需要 ROS 的核心/参数校验测试
python3 -m pytest test/test_arithmetic.py test/test_cli.py -v
# 已 source ROS 时：构建、运行真实节点/服务/话题测试，检查 XUnit 结果
bash scripts/verify_ros2.sh
```

验证脚本使用临时构建目录；可通过 `CALCULATOR_TEST_WORKSPACE`、`CALCULATOR_TEST_RESULTS` 和 `ROS_DOMAIN_ID` 配置。默认域 73，只进行本机发现。先停止该域里自己运行的同名演示节点，避免干扰测试。纯 Python 环境下直接运行所有 pytest 会跳过 ROS 集成模块；完整验证脚本会预检 ROS 依赖，缺失时直接失败。

开发检查可在隔离虚拟环境中安装 `requirements-dev.txt` 后执行 `ruff check .` 和 `ruff format --check .`。CI 同时验证 Humble、Jazzy、ROS 1 Noetic 及纯 Python；测试结果以 XUnit artifact 保存。

## 阅读与调试入口

- [中文测试报告](docs/TEST_REPORT.zh-CN.md) / [English test report](docs/TEST_REPORT.en.md)
- [结构、接口与设计取舍](docs/architecture.md)
- [命令行、pdb 与 VS Code 调试](docs/debugging.md)
- [作业要求逐项对照](docs/requirements.md)
- [ROS 1 Noetic rostest 兼容包](compat/ros1/Calculator/README.md)

主分支为 `master`，功能分支和合并提交保留在 Git 历史中。源代码不依赖个人机器路径；构建产物、日志和本机环境配置不提交。按要求使用 Python，未实现 C++ 加分项。
