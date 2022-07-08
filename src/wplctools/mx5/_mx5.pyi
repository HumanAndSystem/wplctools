from typing import overload


class ActError(Exception):
    ...


class ActOleError(ActError):
    ...


class ActCommon:
    def Open(self):
        ...
    def Close(self):
        ...
    def GetCpuType(self) -> tuple[str, int]:
        ...

    def open(self):
        ...
    def close(self):
        ...
    def get_cpu_type(self) -> tuple[str, int]:
        ...


class ActProgType(ActCommon):
    def OpenSimulator2(self, target=0):
        ...

    def open_simulator2(self, target=0):
        ...


class ActUtlType(ActCommon):
    @overload
    def Open(self, stno = -1):
        ...
