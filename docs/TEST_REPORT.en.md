# Calculator Test Report

Date: 2026-10-22. Validated implementation: [`1886a75`](https://github.com/xyb2000/Calculator/commit/1886a75db17cd2c2d6dcdcbf6b7194e11dde9632). Later documentation and merge commits retain the same runtime code.

## Scope and implementation

The Python package provides a configurable String publisher, a logging subscriber, an AddTwoInts service, a one-shot client, and three composable launch files. Arithmetic and argument parsing are independent of ROS. Relative graph names support namespaces and remapping. Discovery and response waits have separate finite limits; the client returns distinct success, communication-failure, and argument-error exit codes.

The assignment links ROS 2 Humble documentation but also requests ROS 1 rostest. The primary implementation uses ament_python, colcon, pytest, and launch_testing on Humble and Jazzy. An isolated Noetic catkin companion implements the literal rostest workflow. The package preserves the requested spelling `Calculator`, which produces a documented naming warning. The Python import name is `calculator`.

## Environments and evidence

| Environment | Result |
| --- | --- |
| Local WSL2, Ubuntu 24.04, Jazzy, Python 3.12.3, pytest 7.4.4 | Build and complete ROS 2 suite passed |
| GitHub Ubuntu runner, Python 3.10 | Unit tests, coverage, Ruff lint and formatting passed |
| `ros:humble-ros-base-jammy` | Build and real ROS 2 integration tests passed |
| `ros:jazzy-ros-base-noble` | Build and real ROS 2 integration tests passed |
| `ros:noetic-ros-base-focal` | Catkin build and real rostest tests passed |

The [successful CI run](https://github.com/xyb2000/Calculator/actions/runs/39735790261) contains logs and XUnit artifacts for all four jobs. Local checks also confirmed complete rosdep dependencies, the official service returning 42, official publisher/subscriber communication, and a working WSLg Qt display connection.

## Test design

Thirteen arithmetic tests cover ordinary values, zero, negatives, mixed signs, cancellation, exact int64 limits, both overflow directions, invalid types, and invalid ranges. One seeded property test checks 1,000 input pairs against an independent bit-mask oracle, commutativity, and the zero identity. Eight CLI tests verify operand parsing, limits, default/custom timeouts, rejection of non-finite or non-positive timeouts, and argument-error status 2.

The ROS 2 suite launches installed nodes and communicates through DDS. Thirteen named service tests include positive, zero, negative, mixed-sign, cancelling, and large inputs; both int64 endpoints; opposite endpoints; positive and negative overflow; repeated endpoints; and further successful requests after overflow. Literal expected values are independent of the implementation helper. The [Chinese report](TEST_REPORT.zh-CN.md) contains the complete input/expected-result table.

The suite also checks the configured topic prefix, increasing counters, actual listener output, successful execution of the installed CLI, service-discovery timeout, response timeout, and invalid operands. A real service advertised by an unspun node provides the response-timeout scenario. Shutdown checks require clean exit codes. Discovery, spinning, and subprocesses have bounded waits; no mocks replace middleware communication.

The ROS 1 companion provides twelve separate service test methods and one topic test. Rostest starts its own master and real nodes. CMake registers the `.test` file with `add_rostest`, and `catkin_test_results` checks the generated XML.

## Results and counting

| Check | Observed result |
| --- | --- |
| Pure arithmetic and CLI tests | 21 passed |
| Arithmetic statement and branch coverage | 100%; all 13 statements and 4 branches covered |
| ROS 2 pytest / colcon collection | 22 passed; zero errors, failures, or skips |
| Nested ROS 2 launch suite | 18 active methods and 1 shutdown method passed |
| ROS 1 business tests | 13 passed; zero errors or failures |
| Catkin aggregate XML count | 14 passed, including one framework wrapper |
| Ruff and rosdep | Passed; system dependencies satisfied |

The 22 ROS 2 collection items comprise 21 pure tests and one launch suite containing 19 methods. Collection items, nested methods, and input rows must not be added together as independent tests. The 100% coverage claim applies only to the arithmetic module, not every node or error path.

## Reproduction and limitations

Source the selected ROS installation, enter the repository, then run:

```bash
python3 -m pytest test/test_arithmetic.py test/test_cli.py -v
bash scripts/verify_ros2.sh
```

The script builds the package, tests installed nodes, and checks XUnit results. Missing ROS test dependencies fail the full verification script. The companion README documents the separate Noetic commands.

The standard AddTwoInts schema contains only int64 fields and no error status. Overflow therefore follows an explicit signed two's-complement wrap contract, with a server warning. For example, INT64_MAX + 1 returns INT64_MIN. A business requirement to reject overflow would require a different response schema. Timeout cancels local waiting, not work already accepted by a server.

Cross-machine networking, sustained load, real-time performance, and hardware deployment were not tested. Noetic is provided only for compatibility verification. This submission intentionally uses Python and does not claim the C++ bonus. Within the documented environments and contract, all implemented functionality and automated checks passed.
