# Calculator 测试报告

测试日期：2026-10-22。验证代码版本：[`1886a75`](https://github.com/xyb2000/Calculator/commit/1886a75db17cd2c2d6dcdcbf6b7194e11dde9632)。后续文档与合并提交不改变该版本的运行代码。

## 1. 目的与功能范围

验证 Python ROS 包能构建、启动、通过真实中间件通信，并在边界输入与失败场景下保持可解释的行为。

- `talker` 定时发布 `std_msgs/String`，`listener` 接收并记录消息。
- `add_two_ints_server` 提供标准 AddTwoInts 服务，客户端发送一次请求并显示结果。
- 三个 launch 文件分别启动话题示例、服务示例和组合示例，支持命名空间与启动参数。
- 纯运算层定义 int64 输入范围和溢出规则；CLI 校验输入及等待时间。
- ROS 2 采用 pytest/launch_testing；独立 Noetic 包提供真正的 rostest。

## 2. 环境与证据

| 环境 | 测试工具 | 结果 |
| --- | --- | --- |
| 本机 WSL2、Ubuntu 24.04、ROS 2 Jazzy、Python 3.12.3 | colcon 0.21.3、pytest 7.4.4、launch_testing 3.4.12 | 构建及完整测试通过 |
| GitHub Ubuntu runner、Python 3.10 | pytest、pytest-cov、Ruff 0.11.13 | 纯测试、覆盖率、lint、格式检查通过 |
| GitHub `ros:humble-ros-base-jammy` | colcon、pytest、launch_testing | 构建及真实 ROS 2 测试通过 |
| GitHub `ros:jazzy-ros-base-noble` | colcon、pytest、launch_testing | 构建及真实 ROS 2 测试通过 |
| GitHub `ros:noetic-ros-base-focal` | catkin_make、rostest、catkin_test_results | 构建及真实 ROS 1 测试通过 |

[完整通过的 CI 运行记录](https://github.com/xyb2000/Calculator/actions/runs/39735790261)包含四个作业的日志和 XUnit artifacts。本机另验证 `rosdep check` 全部系统依赖满足、官方服务返回 42、官方发布/订阅通信，以及 WSLg 的 Qt 显示连接。

## 3. 测试设计

### 3.1 纯运算与参数

`test/test_arithmetic.py` 有 13 项测试，覆盖普通加法、零、负数、异号、抵消、精确边界、两方向溢出、相反极值、类型和范围拒绝。固定随机种子生成 1,000 对 int64 数据，使用独立位掩码 oracle 核对结果，并验证交换律和零元素性质；它是一个测试方法中的数据检查，不计作 1,000 个独立测试。

`test/test_cli.py` 有 8 项测试，覆盖 int64 边界、超范围、非整数、默认/自定义超时、非正数与 NaN/Inf 拒绝，以及参数错误退出码 2。

### 3.2 真实 ROS 2 服务与话题

`test/test_ros2_integration.py` 通过安装后的 launch 文件启动独立进程，在 `/integration` 命名空间使用真实 DDS 通信。预期值直接写入测试，不复用运算实现产生答案。

| 服务用例 | 输入 a、b | 预期 sum |
| --- | --- | --- |
| 正数 | 2、3 | 5 |
| 零 | 0、0 | 0 |
| 负数 | -7、-9 | -16 |
| 异号 | -7、12 | 5 |
| 抵消 | 123456789、-123456789 | 0 |
| 较大普通数值 | 123456789、987654321 | 1111111110 |
| 最大端点 | 9223372036854775807、0 | 9223372036854775807 |
| 最小端点 | -9223372036854775808、0 | -9223372036854775808 |
| 相反极值 | 最大值、最小值 | -1 |
| 正向溢出 | 最大值、1 | 最小值 |
| 负向溢出 | 最小值、-1 | 最大值 |
| 同方向极值相加 | 最大值两次；最小值两次 | -2；0 |
| 溢出后继续服务 | 溢出请求后继续发送 20+22 和 1+1 | 42；2，进程仍存活 |

另外验证：

- 收到至少三条带配置前缀的消息，计数递增，真实 listener 输出接收日志。
- 实际安装的 CLI 完成 12+30，输出 42 并退出 0。
- 服务不存在时发现等待受限，输出完整服务名并退出 1。
- 使用真实但不执行回调的服务端点验证响应超时，退出 1。
- 三种无效操作数由实际 CLI 进程拒绝，退出 2。
- launch 关闭阶段检查持续节点均正常退出 0。

测试使用有限发现等待、executor spin 和子进程超时，不通过 mock 替代 ROS，也不使用固定 sleep 猜测节点何时就绪。

### 3.3 ROS 1 rostest

兼容包有 12 个独立服务测试方法与 1 个真实话题测试，覆盖正数、零、负数、异号、大数、两个边界和两个方向的溢出。rostest 自动启动 ROS master 和被测节点，经真实服务传输核对结果。CMake 用 `add_rostest` 注册测试，`catkin_test_results` 检查最终 XML；只看 `catkin_make` 的退出状态不足以确认测试成功。

## 4. 实测结果与计数说明

| 检查 | 结果 |
| --- | --- |
| 运算与 CLI | 21 项通过 |
| 运算核心覆盖率 | 语句和分支均 100%；13 条语句、4 个分支全部覆盖 |
| ROS 2 完整 pytest / colcon | 22 个收集项通过，0 errors、0 failures、0 skipped |
| ROS 2 launch suite 内部 | 18 个活动测试方法通过，另有 1 个关闭检查通过 |
| ROS 1 rostest 业务测试 | 13 项通过，0 errors、0 failures |
| ROS 1 catkin XML 汇总 | 14 项、0 errors、0 failures、0 skipped，包含 1 个框架包装项 |
| Ruff lint / format | 全部通过 |
| rosdep 依赖检查 | 所有系统依赖满足 |

ROS 2 的 22 个 pytest 项由 21 个纯测试和 1 个 launch suite 构成；launch suite 内含 19 个测试方法。不能把收集项数、内部方法数和参数数据组数混加后声称为互相独立的测试数量。覆盖率 100% 仅指纯运算核心，不代表 ROS 节点全部代码或所有异常路径都被覆盖。

## 5. 复现

```bash
source /opt/ros/jazzy/setup.bash  # Ubuntu 22.04 改用 humble
# 在仓库目录执行
python3 -m pytest test/test_arithmetic.py test/test_cli.py -v
bash scripts/verify_ros2.sh
```

脚本会构建安装空间、运行全部 ROS 2 测试，并用 `colcon test-result` 检查 XML。默认报告目录为 `test-results/`；缺少 ROS 测试依赖时脚本直接失败，不能把跳过视作通过。ROS 1 的完整复现命令见[兼容包说明](../compat/ros1/Calculator/README.md)。

## 6. 限制与结论

本次验证覆盖了作业功能、正常流程、边界与主要通信失败场景。未进行跨机器网络、长期压力、硬件实时性或生产部署验证。标准 AddTwoInts 不包含错误字段，溢出按文档约定回绕；若业务要求溢出报错，应改用带状态的服务定义。大写包名产生已知命名警告。ROS 1 Noetic 仅作兼容验证，不作为新部署建议。提交使用 Python，不声称完成 C++ 加分项。

在上述已验证环境和契约下，包构建成功，功能与自动化测试均通过。
