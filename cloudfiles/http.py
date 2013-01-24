""" See COPYING for license information. """

from httplib   import HTTPConnection, HTTPSConnection
from sys       import version_info


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
