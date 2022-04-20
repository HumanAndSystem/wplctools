from setuptools import setup, find_packages


# packages = find_packages()
# print(packages)
setup(
    name="wplctools",
    version="0.1",
    package_dir={"": "src"},
    packages=[
        "wplctools",
    ],
    test_suite="tests",
)
