from typing import overload, TypeVar


class ActError(Exception):
    ...


class ActOleError(ActError):
    ...


class ActCommon:
    def Open(self):
        ...
    def Close(self):
        ...
    def ReadDeviceBlock2(self, device: str, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def WriteDeviceBlock2(self, device: str, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def ReadDeviceRandom2(self, device: str, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def WriteDeviceRandom2(self, device: str, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def CheckControl(self):
        ...
    def GetCpuType(self) -> tuple[str, int]:
        ...
    def SetCpuStatus(self, operation: int):
        ...
    def ReadDeviceBlock(self, device: str, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def WriteDeviceBlock(self, device: str, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def ReadDeviceRandom(self, device: str, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def WriteDeviceRandom(self, device: str, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def ReadBuffer(self, startio: int, address: int, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def WriteBuffer(self, startio: int, address: int, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def GetClockData(self) -> tuple[int, int, int, int, int, int, int]:
        ...
    def SetClockData(self, year: int, month: int, day: int, day_of_week: int, hour: int, minute: int, second: int):
        ...
    def SetDevice(self, device: str, data: int):
        ...
    def GetDevice(self, device: str) -> int:
        ...
    def GetDevice2(self, device: str) -> int:
        ...
    def SetDevice2(self, device: str, data: int):
        ...

    def open(self):
        ...
    def close(self):
        ...
    def read_device_block2(self, device: str, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def write_device_block2(self, device: str, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def read_device_random2(self, device: str, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def write_device_random2(self, device: str, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def check_control(self):
        ...
    def get_cpu_type(self) -> tuple[str, int]:
        ...
    def set_cpu_status(self, operation: int):
        ...
    def read_device_block(self, device: str, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def write_device_block(self, device: str, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def read_device_random(self, device: str, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def write_device_random(self, device: str, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def read_buffer(self, startio: int, address: int, size: int, data: bytes | bytearray = None, offset: int = 0) -> bytes | bytearray:
        ...
    def write_buffer(self, startio: int, address: int, size: int, data: bytes | bytearray, offset: int = 0):
        ...
    def get_clock_data(self) -> tuple[int, int, int, int, int, int, int]:
        ...
    def set_clock_data(self, year: int, month: int, day: int, day_of_week: int, hour: int, minute: int, second: int):
        ...
    def set_device(self, device: str, data: int):
        ...
    def get_device(self, device: str) -> int:
        ...
    def get_device2(self, device: str) -> int:
        ...
    def set_device2(self, device: str, data: int):
        ...


class ActProgType(ActCommon):
    ActNetworkNumber: int
    ActStationNumber: int
    ActUnitNumber: int
    ActConnectUnitNumber: int
    ActIONumber: int
    ActCpuType: int
    ActPortNumber: int
    ActBaudRate: int
    ActDataBits: int
    ActParity: int
    ActStopBits: int
    ActControl: int
    ActHostAddress: str
    ActCpuTimeOut: int
    ActTimeOut: int
    ActSumCheck: int
    ActSourceNetworkNumber: int
    ActSourceStationNumber: int
    ActDestinationPortNumber: int
    ActDestinationIONumber: int
    ActMultiDropChannelNumber: int
    ActThroughNetworkType: int
    ActIntelligentPreferenceBit: int
    ActDidPropertyBit: int
    ActDsidPropertyBit: int
    ActPacketType: int
    ActPassword: str
    ActTargetSimulator: int
    ActUnitType: int
    ActProtocolType: int

    network_number: int
    station_number: int
    unit_number: int
    connect_unit_number: int
    io_number: int
    cpu_type: int
    port_number: int
    baud_rate: int
    data_bits: int
    parity: int
    stop_bits: int
    control: int
    host_address: str
    cpu_time_out: int
    time_out: int
    sum_check: int
    source_network_number: int
    source_station_number: int
    destination_port_number: int
    destination_io_number: int
    multi_drop_channel_number: int
    through_network_type: int
    intelligent_preference_bit: int
    did_property_bit: int
    dsid_property_bit: int
    packet_type: int
    password: str
    target_simulator: int
    unit_type: int
    protocol_type: int


class ActUtlType(ActCommon):
    ActLogicalStationNumber: int
    ActPassword: str

    logical_station_number: int
    password: str

    @overload
    def Open(self, stno = -1):
        ...
    @overload
    def open(self, stno = -1):
        ...
