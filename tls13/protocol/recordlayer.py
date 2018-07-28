
# B.1.  Record Layer
# https://tools.ietf.org/html/draft-ietf-tls-tls13-26#appendix-B.1

__all__ = [
    'ContentType', 'TLSPlaintext', 'TLSInnerPlaintext', 'TLSCiphertext'
]

import collections

from .keyexchange.version import ProtocolVersion
from ..utils.type import Uint8, Uint16, Uint24, Uint32, Type
from ..utils.codec import Reader
from ..utils.repr import make_format
from ..utils.struct import Struct, Members, Member, Listof

@Type.add_labels_and_values
class ContentType(Type):
    """
    enum { ... } ContentType
    """
    invalid = Uint8(0)
    change_cipher_spec = Uint8(20)
    alert = Uint8(21)
    handshake = Uint8(22)
    application_data = Uint8(23)
    _size = 1 # byte


class TLSPlaintext(Struct):
    """
    struct {
      ContentType type;
      ProtocolVersion legacy_record_version;
      uint16 length;
      opaque fragment[TLSPlaintext.length];
    } TLSPlaintext;
    """
    def __init__(self, _type, fragment, length=None):
        self.type = _type
        self.legacy_record_version = Uint16(0x0303)
        self.length = length or Uint16(len(fragment))
        self.fragment = fragment
        assert self.type in ContentType.values
        assert type(self.length) == Uint16

        self.struct = Members(self, [
            Member(ContentType, 'type'),
            Member(ProtocolVersion, 'legacy_record_version'),
            Member(Uint16, 'length'),
            Member(Struct, 'fragment'),
        ])

    def __getattr__(self, name):
        """
        self.fragment.msg の指名された属性の値を返す．
        このクラスでは self はrecord層，self.fragment はhandshake層を表していて，
        record層とhandshake層は通信の種類を区別するために必要だが，
        鍵共有等で使うデータ群は全てhandshake層より上の ClientHello や ServerHello にあるので，
        self.fragment.msg.foobar とする代わりに self.foobar で簡単にアクセスできるようにする．
        """
        if self.fragment is None or self.fragment.msg is None:
            raise AttributeError("'%s' object has no attribute '%s'" % \
                  (self.__class__.__name__, name))
        return getattr(self.fragment.msg, name)

    @classmethod
    def from_bytes(cls, data):
        from .handshake import Handshake
        reader = Reader(data)
        _type                 = reader.get(Uint8)
        legacy_record_version = reader.get(Uint16)
        length                = reader.get(Uint16)
        fragment              = reader.get_rest()

        assert length.value == len(fragment)

        if _type == ContentType.handshake:
            return cls(_type=_type, fragment=Handshake.from_bytes(fragment))
        else:
            raise NotImplementedError()


class TLSInnerPlaintext(Struct):
    """
    struct {
      opaque content[TLSPlaintext.length];
      ContentType type;
      uint8 zeros[length_of_padding];
    } TLSInnerPlaintext;
    """
    def __init__(self, content, _type, length_of_padding):
        self.content = content # TLSPlaintext.fragment
        self.type = _type
        self.zeros = b'\x00' * length_of_padding
        self._length_of_padding = length_of_padding


class TLSCiphertext(Struct):
    """
    struct {
      ContentType opaque_type = application_data; /* 23 */
      ProtocolVersion legacy_record_version = 0x0303; /* TLS v1.2 */
      uint16 length;
      opaque encrypted_record[TLSCiphertext.length];
    } TLSCiphertext;
    """
    def __init__(self, length, encrypted_record):
        self.opaque_type = 23
        self.legacy_record_version = Uint16(0x0303)
        self.length = length
        self.encrypted_record = encrypted_record
