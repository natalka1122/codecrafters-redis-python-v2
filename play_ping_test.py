import socket
import time

PING = b"*1\r\n$4\r\nPING\r\n"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 6379))
data_list = [
    PING,
    PING + PING,
    PING[:3],
    PING[3:],
    PING + PING[:4],
    PING[4:],
    PING[:1],
    PING[1:5],
    PING[5:],
]
for data in data_list:
    s.sendall(data)
    print(f"I have sent {data!r}")
    time.sleep(1)
    print("and slept")

print(s.recv(1024))
s.close()

# Looking for 200ms
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 6379))
start_time = time.time()
s.sendall(PING)
print(s.recv(1024))
elapsed_ms = (time.time() - start_time) * 1000
print(f"{elapsed_ms:.2f} ms")
s.close()
