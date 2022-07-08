import io


def def_property(class_name, property_list):
    for snake_case, pascal_case in property_list:
        print(f"        .def_property(\"Act{pascal_case}\", &{class_name}::get_Act{pascal_case}, &{class_name}::put_Act{pascal_case})")
    print()
    for snake_case, pascal_case in property_list:
        print(f"        .def_property(\"{snake_case}\", &{class_name}::get_Act{pascal_case}, &{class_name}::put_Act{pascal_case})")
    print()


def_property("ActUtlType", [
    ("logical_station_number", "LogicalStationNumber"),
    ("password", "Password"),
])

def_property("ActProgType", [
    ("network_number", "NetworkNumber"),
    ("station_number", "StationNumber"),
    ("unit_number", "UnitNumber"),
    ("connect_unit_number", "ConnectUnitNumber"),
    ("io_number", "IONumber"),
    ("cpu_type", "CpuType"),
    ("port_number", "PortNumber"),
    ("baud_rate", "BaudRate"),
    ("data_bits", "DataBits"),
    ("parity", "Parity"),
    ("stop_bits", "StopBits"),
    ("control", "Control"),
    ("host_address", "HostAddress"),
    ("cpu_time_out", "CpuTimeOut"),
    ("time_out", "TimeOut"),
    ("sum_check", "SumCheck"),
    ("source_network_number", "SourceNetworkNumber"),
    ("source_station_number", "SourceStationNumber"),
    ("destination_port_number", "DestinationPortNumber"),
    ("destination_io_number", "DestinationIONumber"),
    ("multi_drop_channel_number", "MultiDropChannelNumber"),
    ("through_network_type", "ThroughNetworkType"),
    ("intelligent_preference_bit", "IntelligentPreferenceBit"),
    ("did_property_bit", "DidPropertyBit"),
    ("dsid_property_bit", "DsidPropertyBit"),
    ("packet_type", "PacketType"),
    ("password", "Password"),
    ("target_simulator", "TargetSimulator"),
    ("unit_type", "UnitType"),
    ("protocol_type", "ProtocolType"),
])
