from ._mx5 import ActError, ActProgType as _ActProgType, ActUtlType as _ActUtlType
from . import ActDefine as Act


__all__ = ["ActError", "ActProgType", "ActUtlType", "Act"]


class ActProgType(_ActProgType):
    def open_simulator2(self, target=0):
        # ActTargetSimulator 0 (0x00) Refer to the property [ActTargetSimulator].
        # Page 183 Details of Control Properties
        # ActUnitType 0x13 (UNIT_QNCPU) UNIT_SIMULATOR2 (0x30)

        self.ActUnitType = Act.UNIT_SIMULATOR2
        self.ActTargetSimulator = target
        self.open()

    def open_simulator3(self, target=0):
        # ActUnitType 0x13 (UNIT_QNCPU) UNIT_SIMULATOR3 (0x31)
        # ActProtocolType 0x04 (PROTOCOL_SERIAL) PROTOCOL_TCPIP (0x05)
        # ActCpuType 34 (CPU_Q02CPU) CPU type corresponding to the target station
        # ActDidPropertyBit 1 (0x01) 0 (0x00)
        # ActDsidPropertyBit 1 (0x01) 0 (0x00)
        # ActPassword Empty 0 (0x00)
        # ActTimeOut 10000 Any value specified by user in ms units
        # ActTargetSimulator 0 (0x00) PLC number corresponding to target station

        # ActHostAddress 1.1.1.1 Loopback address(127.0.0.1)
        # ActPortNumber 1 (PORT_1) 0 (0x00)
        # ActNetworkNumber 0 (0x00) Fixed to 0 (0x00)
        # ActStationNumber 255 (0xFF) System number corresponding to target station
        # ActIONumber 1023 (0x3FF) 0 (0x00)
        # ActDestinationPortNumber 0 (0x00) Fixed to 0 (0x00)
        # ActThroughNetworkType 0 (0x00) Fixed to 0 (0x00)

        # ActBaudRate 19200 (BAUDRATE_19200) 0 (0x00)
        # ActDataBits 8 (DATABIT_8) 0 (0x00)
        # ActParity 1 (ODD_PARITY) 0 (0x00)
        # ActStopBits 0 (STOPBIT_ONE) Fixed to 0 (0x00)
        # ActControl 8 (TRC_DTR_OR_RTS) 0 (0x00)
        # ActSumCheck 0 (NO_SUM_CHECK) Fixed to 0 (0x00)
        # ActPacketType 0x01 (PACKET_PLC1) PACKET_PLC1

        self.ActUnitType = Act.UNIT_SIMULATOR3
        self.ActProtocolType = Act.PROTOCOL_TCPIP
        self.ActTargetSimulator = target
        self.open()

    def open_qcpu_udp(self, host_address: str):
        # ActCpuType 34 (CPU_Q02CPU) CPU type corresponding to the target station
        # ActDestinationIONumber 0 (0x00) Fixed to 0 (0x00) Fixed to 0 (0x00) Target station side
        # ■For single CPU
        # • Fixed to 1023
        # (0x3FF)
        # ■For multiple CPUs
        # • Connected CPU:
        # 1023 (0x3FF)
        # • No. 1: 992 (0x3E0)
        # • No. 2: 993 (0x3E1)
        # • No. 3: 994 (0x3E2)
        # • No. 4: 995 (0x3E3)
        # Target station side
        # ■For single CPU
        # • Fixed to 1023
        # (0x3FF)
        # ■For multiple CPUs
        # • Connected CPU:
        # 1023 (0x3FF)
        # • No. 1: 992 (0x3E0)
        # • No. 2: 993 (0x3E1)
        # • No. 3: 994 (0x3E2)
        # • No. 4: 995 (0x3E3)
        # ■For redundant CPU
        # • Control system: 976
        # (0x3D0)
        # • No specification:
        # 1023 (0x3FF)
        # ActDestinationPortNumber 0 (0x00) • For communication with IP address specified: 5006
        # • For direct communication without IP address specified: Unused
        # ActDidPropertyBit 1 (0x01) Fixed to 1 (0x01) Fixed to 1 (0x01) Fixed to 0 (0x00) Fixed to 0 (0x00)
        # ActDsidPropertyBit 1 (0x01) Fixed to 1 (0x01) Fixed to 1 (0x01) Fixed to 0 (0x00) Fixed to 0 (0x00)
        # ActHostAddress 1.1.1.1 For communication with IP address specified: Host name or IP address of the connected station side
        # For direct communication without specified IP address: The specification is invalid.
        # ActIntelligentPreferenceBit 0 (0x00) Fixed to 0 (0x00) Fixed to 0 (0x00) Target station
        # • QCPU (Q mode),
        # LCPU: 1 (0x01)
        # • Other than the
        # above: 0 (0x00)
        # Target station
        # • QCPU (Q mode),
        # QCCPU, LCPU: 1
        # (0x01)
        # • Other than the
        # above: 0 (0x00)
        # ActIONumber*1 1023 (0x3FF) Target station side
        # ■For single CPU
        # • Fixed to 1023
        # (0x3FF)
        # ■For multiple CPUs
        # • Connected CPU:
        # 1023 (0x3FF)
        # • No. 1: 992 (0x3E0)
        # • No. 2: 993 (0x3E1)
        # • No. 3: 994 (0x3E2)
        # • No. 4: 995 (0x3E3)
        # Target station side
        # ■For single CPU
        # • Fixed to 1023
        # (0x3FF)
        # ■For multiple CPUs
        # • Connected CPU:
        # 1023 (0x3FF)
        # • No. 1: 992 (0x3E0)
        # • No. 2: 993 (0x3E1)
        # • No. 3: 994 (0x3E2)
        # • No. 4: 995 (0x3E3)
        # ■For redundant CPU
        # • Control system: 976
        # (0x3D0)
        # • No specification:
        # 1023 (0x3FF)
        # Connected station side
        # relayed module I/O
        # address
        # Connected station side
        # relayed module I/O
        # address
        # ActMultiDropChannelNumber
        # *2
        # 0 (0x00) Fixed to 0 (0x00) Fixed to 0 (0x00) Multi-drop channel
        # number
        # Fixed to 0 (0x00)
        # ActNetworkNumber*3 0 (0x00) Fixed to 0 (0x00) Target station side
        # module network
        # number
        # Fixed to 0 (0x00) Fixed to 0 (0x00)
        # ActPassword Empty Password set to the connected station side
        # ActProtocolType 0x04
        # (PROTOCOL_SERI
        # AL)
        # PROTOCOL_UDPIP (0x08)
        # ActStationNumber*3 255 (0xFF) Fixed to 255 (0xFF) Target station side
        # module station number
        # Fixed to 255 (0xFF) Fixed to 255 (0xFF)
        # ActThroughNetworkType 0 (0x00) • MELSECNET/10 is not included.: 0 (0x00)
        # • MELSECNET/10 is included.: 1 (0x01)
        # ActTimeOut 10000 Any value specified by user in ms units
        # ActUnitNumber 0 (0x00) Fixed to 0 (0x00) Fixed to 0 (0x00) Target station side
        # module station number
        # Target station side
        # module station number
        # ActUnitType 0x13
        # (UNIT_QNCPU)
        # • For communication with specified IP address: UNIT_QNETHER (0x2C)
        # • For direct communication without specified IP address: UNIT_QNETHER_DIRECT (0x2D)

        self.ActUnitType = Act.UNIT_QNETHER
        self.ActProtocolType = Act.PROTOCOL_UDPIP
        self.ActIONumber = 0x3ff
        self.ActHostAddress = host_address
        self.open()

    def open_e71_udp(self, host: str, port: int, netno: int, stno: int):
        self.ActUnitType = Act.UNIT_QJ71E71
        self.ActProtocolType = Act.PROTOCOL_UDPIP

        self.ActIONumber = 0x3ff
        self.ActHostAddress = host
        self.ActPortNumber = port
        self.ActNetworkNumber = netno
        self.ActStationNumber = stno

        self.ActSourceNetworkNumber = 0
        self.ActSourceStationNumber = 0

        self.ActDestinationIONumber = 0
        self.ActDestinationPortNumber = 5001
        self.ActUnitNumber = 0
        self.ActConnectUnitNumber = 0
        self.ActMultiDropChannelNumber = 0

        self.open()


class ActUtlType(_ActUtlType):
    def open(self, stno: int = -1):
        if stno >= 0:
            self.ActLogicalStationNumber = stno
        self.Open()
