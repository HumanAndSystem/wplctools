import asyncio
import logging

from .act5 import ActProgType, MCRepeater


logger = logging.getLogger(__package__)


class EchoServerProtocol:
    def __init__(self, on_con_lost):
        self.transport = None
        self.on_con_lost = on_con_lost
        self.act = ActProgType()
        self.act.open_simulator2()
        self.repeater = MCRepeater(self.act)

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self.transport.sendto(self.repeater.process(data), addr)

    def connection_lost(self, exc):
        # The socket has been closed
        self.on_con_lost.set_result(True)


async def mainloop(ip: str, port: int):
    print("Starting UDP MC to GX Simulator linker")

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    # One protocol instance will be created to serve all
    # client requests.
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(on_con_lost),
        local_addr=("192.168.0.4", 1025))

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()


def main(args: list[str] = None):
    asyncio.run(mainloop("", 0))
