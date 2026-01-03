import socket
import json
import threading


class SimpleNetSync:
        def __init__(self, server_ip: str, server_port: int):
                self.states: dict[int, str] = {}
                self.local_id: int = -1

                self._server_ip = server_ip
                self._server_port = server_port
                self._local_packet_seq_num = -1

                self._sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self._sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)

                self._sock.sendto(bytes(1), (self._server_ip, self._server_port))
                data, _ = self._sock.recvfrom(65536)
                self.local_id = int.from_bytes(data)

                threading.Thread(target=self._receive_handler).start()
        
        def send(self, data: str):
                self._local_packet_seq_num += 1
                self._sock.sendto(
                        (
                                self._local_packet_seq_num.to_bytes(8) +
                                data.encode("ascii")
                        ),
                        (self._server_ip, self._server_port)
                )


        def _receive_handler(self):
                server_packet_seq_num = -1
                while True:
                        data, _ = self._sock.recvfrom(65536)
                        if int.from_bytes(data[:8]) <= server_packet_seq_num: continue
                        server_packet_seq_num = int.from_bytes(data[:8])
                        self.states = json.loads(data[8:].decode("ascii"))