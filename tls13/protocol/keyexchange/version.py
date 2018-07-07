
# B.3.1.1.  Version Extension
# https://tools.ietf.org/html/draft-ietf-tls-tls13-26#appendix-B.3.1.1

import textwrap
from ..handshake import HandshakeType
from ...utils.type import Uint8, Uint16
from ...utils.codec import Reader

class SupportedVersions:
    """
    struct {
      select (Handshake.msg_type) {
        case client_hello:
          ProtocolVersion versions<2..254>;
        case server_hello: /* and HelloRetryRequest */
          ProtocolVersion selected_version;
      };
    } SupportedVersions;
    """
    def __init__(self, msg_type, versions=[], selected_version=None):
        self.msg_type = msg_type
        if self.msg_type == HandshakeType.client_hello:
            self.versions = versions
            assert type(self.versions) == list
            assert selected_version is None
        elif self.msg_type == HandshakeType.server_hello:
            self.selected_version = selected_version
            assert type(selected_version) == Uint16
        else:
            raise RuntimeError("Unkown message type: %s" % msg_type)

    def __repr__(self):
        if self.msg_type == HandshakeType.client_hello:
            label = 'versions'
            versions = self.versions
        elif self.msg_type == HandshakeType.server_hello:
            label = 'selected_version'
            versions = self.selected_version
        else:
            raise RuntimeError("Unkown message type: %s" % msg_type)

        return textwrap.dedent("""\
            %s:
            |%s: %s""" % \
            (self.__class__.__name__, label, versions))

    def __len__(self):
        if self.msg_type == HandshakeType.client_hello:
            return 1 + sum(map(len, self.versions))
        elif self.msg_type == HandshakeType.server_hello:
            return len(self.selected_version)
        else:
            raise RuntimeError("Unkown message type: %s" % msg_type)

    def to_bytes(self):
        if self.msg_type == HandshakeType.client_hello:
            byte_str = bytearray(0)
            byte_str += Uint8(sum(map(len, self.versions))).to_bytes()
            byte_str += b''.join(x.to_bytes() for x in self.versions)
            return byte_str
        elif self.msg_type == HandshakeType.server_hello:
            return self.selected_version.to_bytes()
        else:
            raise RuntimeError("Unkown message type: %s" % msg_type)

    @classmethod
    def from_bytes(cls, data, msg_type):
        reader = Reader(data)
        if msg_type == HandshakeType.client_hello:
            versions = [Uint16(x) for x in reader.get_var_list(elem_length=2, length_length=1)]
            return cls(msg_type=msg_type, versions=versions)
        elif msg_type == HandshakeType.server_hello:
            selected_version = Uint16(reader.get(2))
            return cls(msg_type=msg_type, selected_version=selected_version)
        else:
            raise RuntimeError("Unkown message type: %s" % msg_type)
