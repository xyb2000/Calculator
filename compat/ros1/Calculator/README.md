# ROS 1 compatibility package

This standalone catkin package preserves the literal `rostest` workflow. The
primary package in this repository targets ROS 2 Humble. Use this companion only
when a ROS 1 environment is required: ROS 1 Noetic reached end of life in May 2025.
The package name is intentionally `Calculator` to match the exercise.

## Build in a clean catkin workspace

Prerequisites: Ubuntu 20.04 with ROS Noetic, `catkin`, `rospy`, `std_msgs`,
`message_generation`, and `rostest` installed. Copy only this package into a new
catkin workspace. Do not put the repository root in that workspace: its primary
build system is ament, and the root `CATKIN_IGNORE` intentionally excludes it.

Run the following from the repository root in Bash:

```bash
source /opt/ros/noetic/setup.bash
mkdir -p ~/calculator_catkin_ws/src
cp -R compat/ros1/Calculator ~/calculator_catkin_ws/src/Calculator
cd ~/calculator_catkin_ws
catkin_make
source devel/setup.bash
```

The package uses Python 3. The `catkin_install_python` rules provide executable
wrappers in the devel space and install the four runtime scripts.

## Run

Start the service and string publisher/subscriber together; `roslaunch` starts
the ROS master when necessary:

```bash
roslaunch Calculator demo.launch
```

In a second terminal, source both ROS and the workspace, then call the service:

```bash
rosrun Calculator add_two_ints_client.py 12 30 --timeout 5
rosservice call /add_two_ints "a: 12
b: 30"
rostopic echo /chatter
```

The Python client prints `42` and exits with status 0. Invalid operands fail
argument parsing; discovery timeout or a service error exits with status 1. The
default service discovery timeout is five seconds. ROS 1's synchronous service
call itself uses the transport's timeout behavior once discovery has succeeded.

For a launch-managed example client:

```bash
roslaunch Calculator demo.launch start_client:=true a:=12 b:=30
```

The `add_two_ints` service has signed `int64` operands `a`, `b`, and response field
`sum`. Overflow wraps using signed 64-bit two's-complement arithmetic; for example
`9223372036854775807 + 1` returns `-9223372036854775808`. ROS rejects operands that
cannot be serialized as `int64`. The arithmetic helper is independent of ROS for
easy debugging. `chatter` carries `std_msgs/String` messages at 10 Hz by default;
use `rate_hz:=2` to change the launch rate. Relative names support normal ROS
namespaces and remapping.

## Test

After building and sourcing the workspace:

```bash
rostest Calculator add_two_ints.test
catkin_make run_tests_Calculator
catkin_test_results --verbose build/test_results
```

`rostest` starts its own ROS master, launches the real service and talker, and runs
12 service round trips. Cases include positive values, zero, negative values,
mixed signs, both `int64` bounds, and overflow in both directions. The topic smoke
test waits for a real string message with a bounded timeout. Expected service
values are literal test data and do not reuse the implementation helper.

## Debug

Run individual nodes with `rosrun Calculator <script>.py` while `roscore` is
running, or add `launch-prefix="python3 -m pdb"` to a node in a local copy of the
launch file. Keep service discovery and test timeouts in mind when pausing the
server at a breakpoint. `rosnode list`, `rosservice info /add_two_ints`, and
`rostopic info /chatter` expose the live ROS graph; node logs include operands,
results, and published/received strings.
