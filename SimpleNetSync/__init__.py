import socket
import json
import threading
import time
from collections.abc import Callable # For type annotation


TIMEOUT = 10.0
KEEPALIVE_INTERVAL = 1.0


class SimpleNetSync:
        def __init__(self, server_ip: str, server_port: int, on_disconnect: Callable = None):
                self.states: dict[int, str] = {}
                self.local_id: int = -1

                self._server_ip = server_ip
                self._server_port = server_port
                self._on_disconnect = on_disconnect
                self._disconnected = False
                self._local_packet_seq_num = -1

                self._sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self._sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                self._sock.setblocking(False)

                # Resend ID request packet until receive ID
                while True:
                        self._sock.sendto(
                                (-1).to_bytes(8, "little", signed=True),
                                (self._server_ip, self._server_port)
                        )
                        try: data, _ = self._sock.recvfrom(65536)
                        except BlockingIOError: # Nothing received:
                                time.sleep(0.2)
                                continue
                        if int.from_bytes(data[:8], "little", signed=True) == -1:
                                self.local_id = int.from_bytes(data[8:], "little", signed=True)
                                break
                        time.sleep(0.2)

                threading.Thread(target=self._receive_handler).start()
                threading.Thread(target=self._keep_alive).start()
        
        def send(self, data: str):
                if (self._disconnected): return

                self._local_packet_seq_num += 1
                self._sock.sendto(
                        (
                                self._local_packet_seq_num.to_bytes(8, "little", signed=True) +
                                data.encode("ascii")
                        ),
                        (self._server_ip, self._server_port)
                )


        def _receive_handler(self):
                server_packet_seq_num = -1
                last_server_packet_receive_time = time.monotonic()
                while True:
                        try: data, _ = self._sock.recvfrom(65536)
                        except BlockingIOError: # Nothing received:
                                if (time.monotonic() - last_server_packet_receive_time) > TIMEOUT:
                                        self._disconnected = True
                                        if (self._on_disconnect): self._on_disconnect()
                                        return
                                time.sleep(0.001)
                                continue

                        last_server_packet_receive_time = time.monotonic()

                        if int.from_bytes(data[:8], "little", signed=True) <= server_packet_seq_num: continue
                        server_packet_seq_num = int.from_bytes(data[:8], "little", signed=True)
                        self.states = json.loads(data[8:].decode("ascii"))
        
        def _keep_alive(self):
                while True:
                        if (self._disconnected): return

                        time.sleep(KEEPALIVE_INTERVAL)
                        self._sock.sendto(
                                (0).to_bytes(8, "little", signed=True),
                                (self._server_ip, self._server_port)
                        )