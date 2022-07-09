from typing import overload, TypeVar


BYTES = TypeVar("BYTES", bytes, bytearray)


class ActError(Exception):
    ...


class ActOleError(ActError):
    ...


class ActCommon:
    def Open(self):
        ...
    def Close(self):
        ...
    def ReadDeviceBlock2(self, device: str, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def WriteDeviceBlock2(self, device: str, size: int, data: BYTES, offset: int = 0):
        ...
    def ReadDeviceRandom2(self, device: str, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def WriteDeviceRandom2(self, device: str, size: int, data: BYTES, offset: int = 0):
        ...
    def CheckControl(self):
        ...
    def GetCpuType(self) -> tuple[str, int]:
        ...
    def SetCpuStatus(operation: int):
        ...
    def ReadDeviceBlock(device: str, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def WriteDeviceBlock(device: str, size: int, data: BYTES, offset: int = 0):
        ...
    def ReadDeviceRandom(device: str, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def WriteDeviceRandom(device: str, size: int, data: BYTES, offset: int = 0):
        ...
    def ReadBuffer(startio: int, address: int, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def WriteBuffer(startio: int, address: int, size: int, data: BYTES, offset: int = 0):
        ...
    def GetClockData() -> tuple[int, int, int, int, int, int, int]:
        ...
    def SetClockData(year: int, month: int, day: int, day_of_week: int, hour: int, minute: int, second: int):
        ...
    def SetDevice(device: str, data: int):
        ...
    def GetDevice(device: str) -> int:
        ...
    def GetDevice2(device: str) -> int:
        ...
    def SetDevice2(device: str, data: int):
        ...

    def open(self):
        ...
    def close(self):
        ...
    def read_device_block2(self, device: str, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def write_device_block2(self, device: str, size: int, data: BYTES, offset: int = 0):
        ...
    def read_device_random2(self, device: str, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def write_device_random2(self, device: str, size: int, data: BYTES, offset: int = 0):
        ...
    def check_control(self):
        ...
    def get_cpu_type(self) -> tuple[str, int]:
        ...
    def set_cpu_status(operation: int):
        ...
    def read_device_block(device: str, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def write_device_block(device: str, size: int, data: BYTES, offset: int = 0):
        ...
    def read_device_random(device: str, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def write_device_random(device: str, size: int, data: BYTES, offset: int = 0):
        ...
    def read_buffer(startio: int, address: int, size: int, data: BYTES = None, offset: int = 0) -> BYTES | bytearray:
        ...
    def write_buffer(startio: int, address: int, size: int, data: BYTES, offset: int = 0):
        ...
    def get_clock_data() -> tuple[int, int, int, int, int, int, int]:
        ...
    def set_clock_data(year: int, month: int, day: int, day_of_week: int, hour: int, minute: int, second: int):
        ...
    def set_device(device: str, data: int):
        ...
    def get_device(device: str) -> int:
        ...
    def get_device2(device: str) -> int:
        ...
    def set_device2(device: str, data: int):
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
