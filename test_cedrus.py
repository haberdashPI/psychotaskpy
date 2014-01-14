import pyxid

# get a list of all attached XID devices
devices = pyxid.get_xid_devices()
pyxid.use_response_pad_timer = True

dev = devices[0] # get the first device to use
if dev.is_response_device():
    dev.reset_base_timer()
    dev.reset_rt_timer()

    while True:
        dev.poll_for_response()
        if dev.response_queue_size() > 0:
            response = dev.get_next_response()
            print response
