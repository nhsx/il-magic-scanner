from asyncio import open_unix_connection
import toml
import time

class StraightSender:
    async def send(self, sock, string):
        sock.write(string.encode())
        await sock.drain()

class DelaySender:
    def __init__(self, key_delay_ms=100):
        self.key_delay_ms = key_delay_ms
        self.sender = StraightSender()

    def delay(self):
        time.sleep(self.key_delay_ms/1000)

    async def send(self, sock, string):
        split_string = list(string)
        for character in split_string:
            self.delay()
            await self.sender.send(sock, character)

class KeebdOutput:
    @classmethod
    def fake(cls):
        return FakeOutput()

    def __init__(self, key_delay_ms=0):
        self.socket_path = toml.load("/etc/keebd.conf")['socket_path']
        if key_delay_ms == 0:
            self.sender = StraightSender()
        else:
            self.sender = DelaySender(key_delay_ms)

    async def send(self, name, number):
        _, sock = await open_unix_connection(path=self.socket_path)

        given_name, family_name, *_ = [*name.split(" ", 1), '']
        string_to_send = f"{given_name}\t{family_name}\t{number}\t"
        
        await self.sender.send(sock, string_to_send)
        sock.close()
        await sock.wait_closed()

class FakeOutput:
    async def send(self, name, number):
        given_name, family_name, *_ = [*name.split(" ", 1), '']
        data_to_send = f"{given_name}\t{family_name}\t{number}".encode()
        print("Would have sent: ", data_to_send)


