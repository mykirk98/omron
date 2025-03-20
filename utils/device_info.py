import stapipy as st

def print_info(device) -> None:
    """
    Print device information.

    :param st_device: Device object.
    """
    print(f"Device Model Name : {device.info.model}")
    print(f"Device ID : {device.info.device_id}")
    print(f"Device Serial Number : {device.info.serial_number}")
    # print(f"Device Vendor Name : {device.info.vendor_name}")
    print(f"Device TL Type : {device.info.tl_type}")
    print(f"Device Access Status : {device.info.access_status}")
    print(f"Device Display Name : {device.info.display_name}")
    # print(f"Device User Defined Name : {device.info.user_defined_name}")
    # print(f"Device GenTL Producer Name : {device.info.tl_type}")
    # print(f"Device GenTL Producer Version : {device.info.tl_version}")
    # print(f"Device GenTL Producer File Name : {device.info.tl_file_name}")
    # print(f"Device GenTL Producer File Version : {device.info.tl_file_version}")
    # print(f"Device GenTL Producer ID : {device.info.tl_id}")
    # print(f"Device GenTL Producer Vendor : {device.info.tl_vendor}")
    # print(f"Device GenTL Producer Model : {device.info.tl_model}")
    # print(f"Device GenTL Producer TL Type : {device.info.tl_type}")
    # print(f"Device GenTL Producer Path : {device.info.tl_path}")
    # print(f"Device GenTL Producer Display Name : {device.info.tl_display_name}")
    # print(f"Device GenTL Producer GenTL Version : {device.info.tl_gen_tl_version}")
    # print(f"Device GenTL Producer GenTL File Name : {device.info.tl_gen_tl_file_name}")
    # print(f"Device GenTL Producer GenTL File Version : {device.info.tl_gen_tl_file_version}")
    # print(f"Device GenTL Producer GenTL ID : {device.info.tl_gen_tl_id}")
    # print(f"Device GenTL Producer GenTL Vendor : {device.info.tl_gen_tl_vendor}")
    # print(f"Device GenTL Producer GenTL Model : {device.info.tl_gen_tl_model}")
    # print(f"Device GenTL Producer GenTL TL Type : {device.info.tl_gen_tl_type}")