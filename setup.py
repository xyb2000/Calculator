"""Install Python nodes, ROS metadata and launch files using ament_python."""

from glob import glob

from setuptools import find_packages, setup

PACKAGE_NAME = "Calculator"

setup(
    name=PACKAGE_NAME,
    version="1.0.0",
    packages=find_packages(exclude=("test", "test.*", "compat", "compat.*")),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{PACKAGE_NAME}"]),
        (f"share/{PACKAGE_NAME}", ["package.xml"]),
        (f"share/{PACKAGE_NAME}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    tests_require=["pytest"],
    zip_safe=True,
    maintainer="xyb2000",
    maintainer_email="212140325+xyb2000@users.noreply.github.com",
    description="A readable, tested ROS calculator in Python",
    license="MIT",
    entry_points={
        "console_scripts": [
            "talker = calculator.publisher:main",
            "listener = calculator.subscriber:main",
            "add_two_ints_server = calculator.service:main",
            "add_two_ints_client = calculator.client:main",
        ],
    },
)
