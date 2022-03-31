

def recvall(sock, n):
    """ Function which helps socket receive.
    :param sock: socket to receive.
    :param n: amount of bytes to fetch from socket
    :return: received data
    """
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
