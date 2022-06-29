from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension


ext_modules = [
    Pybind11Extension("wplctools.melsec._device", ["src/cpp/_device.cpp"],
        extra_compile_args=["/utf-8"],
    ),
]

setup(
    ext_modules = ext_modules,
)
