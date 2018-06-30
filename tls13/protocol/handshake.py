
# B.3.  Handshake Protocol
# https://tools.ietf.org/html/draft-ietf-tls-tls13-26#appendix-B.3

import textwrap
from ..utils.type import Uint8, Uint16, Uint24, Uint32

class HandshakeType:
    """
    enum { ... } HandshakeType
    """
    hello_request_RESERVED = Uint8(0)
    client_hello = Uint8(1)
    server_hello = Uint8(2)
    hello_verify_request_RESERVED = Uint8(3)
    new_session_ticket = Uint8(4)
    end_of_early_data = Uint8(5)
    hello_retry_request_RESERVED = Uint8(6)
    encrypted_extensions = Uint8(8)
    certificate = Uint8(11)
    server_key_exchange_RESERVED = Uint8(12)
    certificate_request = Uint8(13)
    server_hello_done_RESERVED = Uint8(14)
    certificate_verify = Uint8(15)
    client_key_exchange_RESERVED = Uint8(16)
    finished = Uint8(20)
    key_update = Uint8(24)
    message_hash = Uint8(254)
    _size = 1 # byte

# inverted dict
# usage: HandshakeType.labels[Uint8(1)] # => 'client_hello'
HandshakeType.labels = dict( (v,k) for k,v in HandshakeType.__dict__.items() )


class Handshake:
    """
    struct {
      HandshakeType msg_type;    /* handshake type */
      uint24 length;             /* bytes in message */
      select (Handshake.msg_type) {
        case client_hello:          ClientHello;
        case server_hello:          ServerHello;
        case end_of_early_data:     EndOfEarlyData;
        case encrypted_extensions:  EncryptedExtensions;
        case certificate_request:   CertificateRequest;
        case certificate:           Certificate;
        case certificate_verify:    CertificateVerify;
        case finished:              Finished;
        case new_session_ticket:    NewSessionTicket;
        case key_update:            KeyUpdate;
      };
    } Handshake;
    """
    def __init__(self, msg_type, length, msg):
        self.msg_type = msg_type # HandshakeType
        self.length = Uint24(length)
        self.msg = msg

    def __repr__(self):
        return textwrap.dedent("""\
            %s:
            |msg_type: %s == %s
            |length: %s
            |%s:
            """ % (
            self.__class__.__name__,
            self.msg_type, HandshakeType.labels[self.msg_type],
            self.length,
            HandshakeType.labels[self.msg_type])) \
            + textwrap.indent(repr(self.msg), prefix="    ")

    def __len__(self):
        return len(self.msg_type) + len(self.length) + len(self.msg)

    def to_bytes(self):
        byte_str = bytearray(0)
        byte_str += self.msg_type.to_bytes()
        byte_str += self.length.to_bytes()
        byte_str += self.msg.to_bytes()
        return byte_str
