from dynamixel_sdk import *

port = PortHandler('/dev/ttyACM1')
packet = PacketHandler(1.0)

port.openPort()
port.setBaudRate(1000000)

for dxl_id in range(1, 11):
    model, comm, err = packet.ping(port, dxl_id)

    if comm == COMM_SUCCESS:
        print("Found:", dxl_id)