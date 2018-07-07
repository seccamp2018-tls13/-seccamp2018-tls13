
from struct import pack

class Uint8:
    """
    an unsigned byte
    """
    def __init__(self, value):
        assert type(value) is int
        self.value = value

    def __repr__(self):
        return "{}(0x{:0{width}x})" \
               .format(self.__class__.__name__, self.value, width=len(self)*2)

    def __len__(self):
        return 1

    # HACK:
    # このクラスのインスタンスは以下の2つの場面で使われる：
    #   - 定数からラベル名の取得：ContentType.labels[Uint8(22)]  #=> 'handshake'
    #   - 定数との比較：ContentType.handshake == Uint8(22)     #=> True
    # 2番目のために __eq__ メソッドを実装すると，1番目で辞書使用時の型エラーの
    # 「TypeError: unhashable type: Uint8」
    # が発生するので，__hash__ メソッドを作ってエラーを回避する．
    # より厳密に書きたい場合は，Uint8 のインスタンスの属性 .value を直接変更しては
    # いけないという制約が必要で，self.value を書き換え不可能（immutable）にする必要がある．
    # https://qiita.com/yoichi22/items/ebf6ab3c6de26ddcc09a
    # https://stackoverflow.com/questions/4996815/ways-to-make-a-class-immutable-in-python
    def __hash__(self):
        return hash((self.value,))

    def __eq__(self, other):
        return self.value == other.value

    def to_bytes(self):
        return pack('>B', self.value)


class Uint16(Uint8):
    """
    uint8 uint24[3];
    """
    def __len__(self):
        return 2

    def to_bytes(self):
        return pack('>H', self.value)


class Uint24(Uint8):
    """
    uint8 uint24[3];
    """
    def __len__(self):
        return 3

    def to_bytes(self):
        return pack('>BH', self.value >> 16, self.value & 0xffff)


class Uint32(Uint8):
    """
    uint8 uint32[4];
    """
    def __len__(self):
        return 4

    def to_bytes(self):
        return pack('>I', self.value)


class Uint:
    @staticmethod
    def get_type(size):
        if size == 1: return Uint8
        if size == 2: return Uint16
        if size == 3: return Uint24
        if size == 4: return Uint32
        raise NotImplementedError()


class Type:
    @staticmethod
    def add_labels_and_values(cls):
        UintN = Uint.get_type(cls._size)
        # add labels (inverted dict) to class
        # usage: HandshakeType.labels[Uint16(1)] # => 'client_hello'
        cls.labels = dict( (v,k) for k,v in cls.__dict__.items() )
        # add values to class
        # usage: assert self.msg_type in HandshakeType.values
        cls.values = set( v for k,v in cls.__dict__.items() if type(v) == UintN )
        return cls
