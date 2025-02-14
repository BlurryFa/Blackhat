import sys
import socket
import threading


def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    # connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # receive data from the remote end if necessary
    if receive_first:

        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)

        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[==>] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)

            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):

            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)

            client_socket.send(remote_buffer)

            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")

            break

# this is a pretty hex dumping function taken from
# the comments here:
# http://code.activestate.com/recipes/142812-hex-dumper/
# 测试一下功能
# ord()函数返回字符的ASCII或者unicode编码
def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = ' '.join(["%0*X"%(digits, ord(x)) for x in s])
        text = ''.join([x if 0x20<= ord(x) < 0x7F else '.' for x in s])
        result.append("%04X  %-*s  %s"% (i, length*(digits+1), hexa, text))

    print('\n'.join(result))

def receive_from(connection):

    buffer = ''

    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)

            if not data:
                break
            buffer += data
    except:
        pass

    return buffer

def request_handler(buffer):
    # perform packet modification
    return buffer

def response_handler(buffer):
    # perform packet modification
    return buffer





def server_loop(local_host, local_port, remote_host, remote_port, receive_fisrt):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%d" % (local_host,local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
    print("[*] Listening on %s:%d" % (local_host,local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print("[==>] Received incoming connection from %s:%d" % (addr[0],addr[1]))

        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_fisrt))

        proxy_thread.start()

