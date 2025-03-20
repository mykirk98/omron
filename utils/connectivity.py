import stapipy as st

def node_callback(node=None, st_device=None) -> None:
    """
    Callback to handle events from GenICam node.

    Args:
        node: node that triggered the callback.
        st_device: PyStDevice object passed on at callback registration.
    """
    
    if node.is_available:
        if st_device.is_device_lost:
            print(f"OnNodeEvent: {node.display_name}: DeviceLost")
        else:
            print(f"OnNodeEvent: {node.display_name}: Invalidated")

