# Description 第 3 项：官方 launch 教程复现

复现日期：2026-10-24。选用题目所链接的 ROS 2 Humble 教程，补上其多节点启动示例；原有计算器启动文件单独保留。

## 官方来源与对应关系

- [Humble 官方 Launching nodes 教程](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Launching-Multiple-Nodes/Launching-Multiple-Nodes.html)
- [教程原始 multisim.launch.py](https://github.com/ros2/ros2_documentation/blob/humble/source/Tutorials/Beginner-CLI-Tools/Launching-Multiple-Nodes/launch/multisim.launch.py)
- 本包交付文件：`launch/multisim.launch.py`。
- 上游的两个 `turtlesim_node`、命名空间和 `screen` 输出配置均保留；只补充来源说明、类型标注并统一格式。
- [出处、变更与许可](../THIRD_PARTY_NOTICES.md)随源码和安装后的 ROS 包一并提供。

题目的旧步骤编号与 Humble 目录不完全对应。本次明确以它提供的 Humble 链接中的启动示例为复现对象。

## 运行教程复现

在已经 source ROS 及 Calculator 工作空间的终端运行：

```bash
sudo apt install ros-${ROS_DISTRO}-turtlesim
ros2 launch Calculator multisim.launch.py
```

命令加载的是 **Calculator 包安装的复现文件**。支持图形显示的 Ubuntu 或 WSLg 中应出现两个海龟窗口。在另一终端执行：

```bash
ros2 node list
ros2 topic list
ros2 service list
```

应包含以下接口：

| 对象 | 第一组 | 第二组 |
| --- | --- | --- |
| 节点 | `/turtlesim1/turtlesim` | `/turtlesim2/turtlesim` |
| 位姿话题 | `/turtlesim1/turtle1/pose` | `/turtlesim2/turtle1/pose` |
| 速度话题 | `/turtlesim1/turtle1/cmd_vel` | `/turtlesim2/turtle1/cmd_vel` |
| 重置服务 | `/turtlesim1/reset` | `/turtlesim2/reset` |

## 按教程控制两只海龟

分别在另外两个终端运行以下命令；两个进程需要同时持续发送速度：

```bash
ros2 topic pub --rate 10 /turtlesim1/turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}'
```

```bash
ros2 topic pub --rate 10 /turtlesim2/turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -1.8}}'
```

两只海龟应沿相反方向转动。观察 pose 话题可以核对运动状态；调用某组 reset 服务只重置该组：

```bash
ros2 topic echo /turtlesim1/turtle1/pose
ros2 service call /turtlesim1/reset std_srvs/srv/Empty '{}'
```

完成后在发布命令和 launch 终端分别按 Ctrl+C。

## topic、service 与 launch 在此示例中的作用

| 概念 | 本例中的含义 | 可观察的证据 |
| --- | --- | --- |
| Topic | 速度命令和位姿通过消息流持续传输 | 发布 cmd_vel，订阅 pose，观察运动变化 |
| Service | reset 通过一次请求和响应完成重置 | 指定某个命名空间调用，不重置另一组 |
| Launch | 一条命令创建、配置并管理两个进程 | 两个节点同时出现，命名空间不同，Ctrl+C 后共同退出 |

命名空间让同名节点及接口可以独立存在。只有第一组收到速度时，第二组不应随之移动。

## 自动验证与运行证据

```bash
bash scripts/verify_ros2.sh
```

`test/test_tutorial_launch.py` 从安装空间启动本例，使用真实 ROS 消息、reset 服务和 Qt 节点验证四项行为及正常关闭。Qt 的 `offscreen` 平台让同一验证可以在没有桌面的 CI 容器中运行。

2026-10-24 本机完整验证结果：23 个 pytest 收集项通过，0 errors、0 failures、0 skipped。新增教程 launch suite 包含四个活动测试方法和一个关闭检查。完整结果说明见[中文报告第 7 节](TEST_REPORT.zh-CN.md#7-2026-10-24官方-launch-教程复现补充验证)。

对应实现提交为 [`1c5b10e`](https://github.com/xyb2000/Calculator/commit/1c5b10e2c63d35f3321b605bc9f4d6b08430c02b)。[本次 CI 运行](https://github.com/xyb2000/Calculator/actions/runs/40074713390)的 Python、Humble、Jazzy 与 ROS 1 rostest 四个作业均已通过；Humble/Jazzy 作业包含新增教程的真实运行验证。
