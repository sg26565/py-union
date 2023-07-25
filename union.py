"""Define C like unions and bitfields."""
from typing import Sequence
from enum import Enum, auto


class Endian(Enum):
    """Enum for die endianes of arrays."""

    LITTLE = auto()
    BIG = auto()


class Union:
    """A union class that mirrors the behavior of C unions."""

    _value: int

    def __init__(self, _value: int = 0, **kwargs):
        """
        Initialize the instance with a compound value or any of its components.

        :param _value: The compound value. If specified, will set the values for all components at once.
        :param kwargs: Values for components.
        :raises AssertionError: If non-existing properties were used in kwargs.
        """
        self._value = _value
        self._members = tuple(s for s in dir(self) if not s.startswith("_"))

        for k, v in kwargs.items():
            assert k in self._members, f'unknown property {k}'
            setattr(self, k, v)

    @staticmethod
    def _mask(size: int, offset: int):
        """Calculate a mask value from size and offset of a bitfield."""
        return (2**size) - 1 << offset

    @staticmethod
    def _size_offset(mask: int):
        """Calculate size and offset form a bitmask."""
        scale = mask & (1 + ~mask)
        offset = scale.bit_length() - 1
        size = (mask >> offset).bit_length()
        assert (mask + scale) & mask == 0, "Non-contiguous mask"
        return (size, offset)

    @staticmethod
    def _bitfield(mask: int | None = None, size: int | None = None, offset: int | None = None):
        """
        Generate a bitfield property.

        Params:
        :mask: The size and offset of the element as a bit mask.
        :size: The bit size of the element.
        :offset: The bit offset from LSB.
        """
        if mask is None and size is not None and offset is not None:
            _mask = Union._mask(size, offset)
            _size = size
            _offset = offset
        elif mask is not None and size is None and offset is None:
            _mask = mask
            _size, _offset = Union._size_offset(mask)
        else:
            raise ValueError('either mask or size and offset are required')

        def getter(self):
            return (self._value & _mask) >> _offset

        def setter(self, newval: int):
            assert newval.bit_length() <= _size, f'{newval} is too large for {_size} bit value'
            self._value &= ~_mask
            self._value |= _mask & (newval << _offset)

        return property(getter, setter)

    @staticmethod
    def _single():
        """Generate a property that retrieves the compound value."""

        def getter(self):
            return self._value

        def setter(self, newval: int):
            self._value = newval

        return property(getter, setter)

    @staticmethod
    def _array(size: int, count: int, endian: Endian = Endian.LITTLE):
        """
        Generate an array property of a given size and count.

        Params:
        size -- The bit size of the array elements
        count -- The number of elements in the array
        """

        def getter(self):
            """Convert the value into an list with count elements for size bits."""
            result = list((self._value & Union._mask(size, offset)) >> offset for offset in range(0, count*size, size))

            if endian == Endian.BIG:
                return list(reversed(result))
            else:
                return result

        def setter(self, newval: Sequence[int]):
            assert issubclass(type(newval), Sequence), f'{type(newval)} is not a subtype of Sequence'
            assert len(newval) == count, f'wrong array size {len(newval)}, expected {count}'

            if endian == Endian.LITTLE:
                val = newval
            else:
                val = list(reversed(newval))

            for i in range(count):
                assert val[i].bit_length() <= size, f'{newval[i]} is too large for {size} bit value'
                offset = i*size
                mask = Union._mask(size, offset)
                self._value &= ~mask
                self._value |= mask & (val[i] << offset)

        return property(getter, setter)

    @staticmethod
    def _string(size: int, offset: int, encoding: str = 'utf-8'):
        """
        Generate a string property.

        Params:
        size -- Size of the string in bytes
        offset -- Offset of the string in bytes
        encoding -- The string encoding
        """
        mask = Union._mask(size=size*8, offset=offset*8)  # byte to bits

        def getter(self):
            val = (self._value & mask) >> offset * 8
            return val.to_bytes(length=size, byteorder='little').decode(encoding=encoding).rstrip('\0')

        def setter(self, newval: str):
            bytes = newval.encode(encoding=encoding)
            assert len(bytes) <= size, f'"{newval}" is too long, expected {size}'

            val = int.from_bytes(bytes=bytes, byteorder='little')
            self._value &= ~mask
            self._value |= val << offset*8

        return property(getter, setter)

    def __repr__(self) -> str:
        """Generate a string representation for this object."""
        return f'{self.__class__.__name__}({", ".join((f"{s}={repr(self.__getattribute__(s))}" for s in self._members))})'
