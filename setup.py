from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension


ext_modules = [
    Pybind11Extension("wplctools.melsec._device", ["src/cpp/_device.cpp"],
        extra_compile_args=["/utf-8"],
    ),
    # Pybind11Extension("_act5",
    #     ["src/act5/main.cpp"],
    #     # Example: passing in the version to the compiled code
    #     # define_macros = [('VERSION_INFO', __version__)],
    #     ),
    # Pybind11Extension("_binaryio",
    #     ["src/_binaryio/lib.cpp"],
    #     extra_compile_args=["/utf-8", "/std:c++17"]
    #     ),
]

setup(
    ext_modules = ext_modules,
)
