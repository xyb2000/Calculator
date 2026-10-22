# 要求对照与版本解释

| 要求 | 交付位置 / 验证方式 |
| --- | --- |
| 创建 Calculator ROS 包并构建 | 根目录 `package.xml`、`setup.py`、`resource/Calculator`；`colcon build` |
| Git 初始提交、GitHub、master、功能分支 | 本仓库；`git log --all --graph --oneline` 可检查真实提交与合并 |
| topic、service、launch 概念及启动文件 | `launch/topics.launch.py`、`service.launch.py`、`demo.launch.py` |
| publisher / subscriber | `calculator/publisher.py`、`subscriber.py`；真实话题与监听日志测试 |
| server / client | `calculator/service.py`、`client.py`；标准 AddTwoInts 接口、CLI 与超时测试 |
| test 目录与测试框架 | `test/` 的 pytest / launch_testing；兼容包内 `test/` 的 rostest |
| 至少五个有代表性的服务测试 | ROS 2：13 个独立服务测试方法；ROS 1：12 个独立服务测试方法；均经真实中间件调用 |
| 中文测试报告、英文加分 | `docs/TEST_REPORT.zh-CN.md`、`docs/TEST_REPORT.en.md` |
| 清晰代码结构、可调试、可迁移 | 纯运算层、ROS 适配、CLI 校验、显式超时、日志、调试配置、自动化验证 |
| Python / C++ | 按提交者选定的语言使用 Python；不声称完成 C++ 加分项 |
| 提交仓库链接 | README 顶部与 Git remote；主交付分支 `master` |

## ROS 版本

题目提供的教程链接是 ROS 2 Humble，但 `rostest` 与部分教程步骤编号来自 ROS 1。ROS 2 不使用 ROS 1 的 roscore/catkin/rostest 工具链，因此主包采用官方 ROS 2 对应方式 `ament_python + colcon + pytest + launch_testing`。

为覆盖字面上的 rostest 要求，`compat/ros1/Calculator` 是可以单独复制构建的 Noetic 包，提供 `.srv`、`CMakeLists.txt`、`.test` 和真正调用服务的测试节点。`compat/COLCON_IGNORE` 防止 colcon 将兼容包混入 ROS 2 工作空间。ROS 1 兼容包仅用于该要求的验证；Noetic 已结束官方维护，不作为新项目部署目标。

ROS 2 Humble 对应 Ubuntu 22.04；Jazzy 对应 Ubuntu 24.04。代码只使用两者共有 API。本机选用已有 Ubuntu 24.04/Jazzy，CI 对题目链接对应的 Humble 进行独立验证。

## 包名

ROS 通常要求小写名称。这里为保持题目指定拼写，将 ROS 包命名为 `Calculator`，Python import 保持 `calculator`。catkin_pkg 的兼容规则允许该拼写并给出命名警告。构建、ament 索引、launch 和入口脚本中的包名大小写保持一致。正常新工程建议使用全小写。

## 官方资料

- [Humble 教程](https://docs.ros.org/en/humble/Tutorials.html)
- [Humble 测试](https://docs.ros.org/en/humble/Tutorials/Intermediate/Testing/Testing-Main.html)
- [launch_testing 的 Humble 实现](https://github.com/ros2/launch/tree/humble/launch_testing)
- [ROS 包命名 REP 144](https://www.ros.org/reps/rep-0144.html)
- [Noetic 维护周期](https://www.ros.org/reps/rep-0003.html)
