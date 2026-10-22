# 调试与排错

## 先确认运行环境

在 WSL 中打开 Bash，而不是使用 Windows Python。每个终端 source 所选 ROS 版本及工作空间。`python3 -c 'import rclpy; print(rclpy.__file__)'` 可确认解释器能找到 ROS。

```bash
printenv ROS_DISTRO
ros2 pkg prefix Calculator
ros2 pkg executables Calculator
ros2 node list
ros2 service list -t
ros2 topic info /chatter --verbose
```

节点采用相对服务/话题名。若 launch 使用 `namespace:=demo`，检查的是 `/demo/add_two_ints` 与 `/demo/chatter`。所有通信进程应使用相同 `ROS_DOMAIN_ID`。若修改域后 CLI 图信息过期，可执行 `ros2 daemon stop` 后重新查询。

## 日志

```bash
ros2 run Calculator add_two_ints_server --ros-args --log-level debug
ros2 launch Calculator demo.launch.py namespace:=demo a:=12 b:=30
```

日志包含完整服务名、请求数值、结果、溢出警告、发布及接收消息。发现超时通常表示服务未运行、域不同或名称不同；响应超时表示服务已发现但没有及时返回。无效参数会在创建节点前退出，避免把输入错误误判成 ROS 发现问题。

## pdb

从仓库目录运行，已 source ROS 时无需先安装模块即可调试 Python 源码：

```bash
python3 -m pdb -m calculator.service
```

在 pdb 中执行 `b calculator/service.py:28`（`response.sum = ...` 所在行），再输入 `c`。另一终端调用：

```bash
ros2 run Calculator add_two_ints_client 12 30 --request-timeout 120
```

用 `p request.a`、`p request.b`、`n`、`p response.sum` 检查回调。暂停服务时需增大客户端响应超时。`python3 -m pdb -m calculator.client 12 30` 可单步调试 CLI。纯运算可直接交互导入 `calculator.arithmetic.add_int64`。

## VS Code / WSL

安装官方 WSL、Python 与 Python Debugger 扩展，在 WSL 模式打开仓库并选择 WSL 的系统 Python。先从已 source ROS 和工作空间的 Bash 启动 `code .`，确认 VS Code 终端能导入 rclpy。不要为安装版 ROS 混用另一套独立 Python 解释器。

仓库提供 `.vscode/launch.json` 的服务端、客户端和发布器调试配置。在 `service.py` 的 `response.sum = ...` 行下断点，启动服务配置，再启动客户端配置。调试配置默认域 73，客户端等待上限 60 秒。手动终端调用时也设置 `export ROS_DOMAIN_ID=73`。

若使用隔离的 VS Code 配置，扩展需装入该配置，Python 扩展应安装在 WSL 远程端。WSL 的 VS Code Server 和 Linux 扩展位于该发行版的虚拟磁盘内。

## 测试失败定位

```bash
python3 -m pytest test/test_arithmetic.py test/test_cli.py -v --pdb
bash scripts/verify_ros2.sh
```

脚本打印完整节点输出与失败断言，XUnit 默认位于仓库 `test-results/`。launch_testing 把多项实际 ROS 断言嵌入一个 pytest launch 用例，查看报告时应同时关注内部 unittest 数量，不能把一项 launch suite 当成仅一次服务测试。

常见情况：

| 现象 | 检查 |
| --- | --- |
| package / executable not found | 是否成功构建并 source 当前 overlay；包名 `Calculator` 大小写 |
| import rclpy 失败 | 是否在 WSL 使用发行版系统 Python，并 source ROS |
| 只有运算测试执行 | ROS 测试依赖是否完整；使用完整验证脚本，不能把 skip 当成通过 |
| 服务发现超时 | 服务进程、完整名称、namespace、remap、ROS_DOMAIN_ID |
| 回调处暂停后客户端失败 | 增大 `--request-timeout` 后重新调用 |
| 大写包名警告 | 保留题目拼写的已知警告，详见要求对照 |
