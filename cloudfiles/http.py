""" See COPYING for license information. """

from httplib   import HTTPConnection, HTTPSConnection
from sys       import version_info
import socket


if version_info >= (2, 6):
    THTTPConnection = HTTPConnection
    THTTPSConnection = HTTPSConnection

else:
    class THTTPConnection(HTTPConnection):
        def __init__(self, host, port, timeout):
            HTTPConnection.__init__(self, host, port)
            self.timeout = timeout

        def connect(self):
            HTTPConnection.connect(self)
            self.sock.settimeout(self.timeout)


    class THTTPSConnection(HTTPSConnection):
        def __init__(self, host, port, timeout):
            HTTPSConnection.__init__(self, host, port)
            self.timeout = timeout

        def connect(self):
            HTTPSConnection.connect(self)
            self.sock.settimeout(self.timeout)


def check_keepalive(keepalive):
    if not keepalive or keepalive is True:
        return keepalive

    keepalive = tuple(keepalive)
    if not 2 <= len(keepalive) <= 3:
        raise ValueError('keepalive must be 2- or 3-tuple')

    return keepalive


def set_keepalive(sock, keepalive):
    if not keepalive:
        return

    supported = False

    if keepalive is True:
        if hasattr(socket, 'SO_KEEPALIVE'):
            # System defaults will be used.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            supported = True

    else:
        if len(keepalive) == 2:
            idle, interval = keepalive
            probes = None
        else:
            idle, interval, probes = keepalive

        if hasattr(socket, 'SIO_KEEPALIVE_VALS'):
            # Windows
            if probes is None:
                sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, idle, interval))
                supported = True

        elif hasattr(socket, 'SO_KEEPALIVE') and \
                hasattr(socket, 'TCP_KEEPIDLE') and \
                hasattr(socket, 'TCP_KEEPINTVL') and \
                hasattr(socket, 'TCP_KEEPCNT'):
            # Linux, maybe others?
            sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, idle)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, interval)
            if probes is not None:
                sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, probes)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            supported = True

    if not supported:
        raise ValueError('Requested keepalive options unsupported')


class CFHTTPConnection(THTTPConnection):
    def __init__(self, host, port, timeout, keepalive = None):
        THTTPConnection.__init__(self, host, port=port, timeout=timeout)
        self.keepalive = check_keepalive(keepalive)

    def connect(self):
        THTTPConnection.connect(self)
        set_keepalive(self.sock, self.keepalive)


class CFHTTPSConnection(THTTPSConnection):
    def __init__(self, host, port, timeout, keepalive = None):
        THTTPSConnection.__init__(self, host, port=port, timeout=timeout)
        self.keepalive = check_keepalive(keepalive)

    def connect(self):
        THTTPSConnection.connect(self)
        set_keepalive(self.sock, self.keepalive)
