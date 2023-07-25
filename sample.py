"""Union sample."""
from union import Union

class Some(Union):
    """Sample subclass of Union."""

    x = Union._bitfield(mask=0xff00)
    y = Union._bitfield(size=8, offset=0)

    foo = Union._single()
    bar = Union._array(size=8, count=4)
    baz = Union._array(size=4, count=8)

    string = Union._string(size=4, offset=0)


if __name__ == '__main__':
    x = Some(1024)
    print(x)

    x.y = 64
    print(x)

    x.x = 3
    print(x)

    x.foo = 2048
    print(x)

    y = Some(x=4, y=64)
    print(y)

    y.bar = (120, 86, 52, 18)
    print(y)

    y.foo = 0x12345678
    print(y)

    y.string = 'Test'
    print(y)
