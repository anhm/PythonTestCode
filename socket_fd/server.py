import os
import time
import multiprocessing
from multiprocessing.reduction import recv_handle, send_handle
import socket


def worker(in_p, out_p):
    out_p.close()
    while True:
        print in_p.__sizeof__()
        fd = recv_handle(in_p)
        print('CHILD: GOT FD', fd)
        s = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        while True:
            msg = s.recv(1024)
            if not msg:
                s.close()
                os.close(fd)
                break
            print('CHILD: RECV {!r}'.format(msg))
            s.send(msg)

def server(address, in_p, out_p, worker_pid):
    in_p.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    s.bind(address)
    s.listen(1)
    while True:
        client, addr = s.accept()
        print('SERVER: Got connection from', addr)
        send_handle(out_p, client.fileno(), 123)
        client.close()

if __name__ == '__main__':
    c1, c2 = multiprocessing.Pipe()
    worker_p = multiprocessing.Process(target=worker, args=(c1,c2))
    worker_p.start()

    server_p = multiprocessing.Process(target=server,
                  args=(('', 50007), c1, c2, worker_p.pid))
    server_p.start()

    c1.close()
    c2.close()
