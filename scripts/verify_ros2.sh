#!/usr/bin/env bash
# Run from any directory after sourcing the selected ROS installation.
set -euo pipefail

: "${ROS_DISTRO:?Source your ROS 2 setup.bash before running this script}"
# Do not let optional import skips hide an incomplete ROS test installation.
python3 -c 'import rclpy, launch_testing, launch_ros; from example_interfaces.srv import AddTwoInts'
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
workspace="${CALCULATOR_TEST_WORKSPACE:-${TMPDIR:-/tmp}/calculator-${ROS_DISTRO}-verify}"
results="${CALCULATOR_TEST_RESULTS:-${repo_root}/test-results}"
mkdir -p "$workspace" "$results"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-73}"
export ROS_LOCALHOST_ONLY=1

colcon --log-base "$workspace/log" build \
    --base-paths "$repo_root" --packages-select Calculator \
    --build-base "$workspace/build" --install-base "$workspace/install" \
    --symlink-install --event-handlers console_direct+

# ROS setup scripts can reference unset variables on some supported platforms.
set +u
source "$workspace/install/setup.bash"
set -u
colcon --log-base "$workspace/log" test \
    --base-paths "$repo_root" --packages-select Calculator \
    --build-base "$workspace/build" \
    --test-result-base "$results" \
    --install-base "$workspace/install" --event-handlers console_direct+ \
    --python-testing pytest \
    --return-code-on-test-failure \
    --pytest-args ' -v'
colcon test-result --test-result-base "$results" --verbose
