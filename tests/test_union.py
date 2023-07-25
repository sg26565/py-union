import unittest
import sys

sys.path.insert(0, '.')
from union import Union, Endian


class TestUnion(unittest.TestCase):
    def test_value_init(self):
        union = Union(12345678)
        self.assertEqual(union._value, 12345678)

    def test_kwargs_init(self):
        class X(Union):
            foo = Union._single()

        x = X(foo=5)

        self.assertEqual(x._value, 5)
        self.assertEqual(x.foo, 5)
        self.assertTupleEqual(x._members, ('foo',))

        with self.assertRaises(AssertionError):
            X(foo=5, bar=7)  # invalid property

    def test_mask(self):
        self.assertEqual(Union._mask(size=8, offset=0), 0xff)
        self.assertEqual(Union._mask(size=8, offset=8), 0xff00)
        self.assertEqual(Union._mask(size=4, offset=2), 0x3c)
        self.assertEqual(Union._mask(size=8, offset=4), 0xff0)
        self.assertEqual(Union._mask(size=32, offset=32), 0xffffffff00000000)

        with self.assertRaises(ValueError):
            Union._mask(size=8, offset=-1)  # negative offset

        with self.assertRaises(TypeError):
            Union._mask(size=-1, offset=0)  # negative size

        with self.assertRaises(TypeError):
            Union._mask(offset=0)  # missing size

        with self.assertRaises(TypeError):
            Union._mask(size=0)  # missing offset

        with self.assertRaises(TypeError):
            Union._mask()  # no arguments

    def test_size_offset(self):
        self.assertTupleEqual(Union._size_offset(0xff), (8, 0))
        self.assertTupleEqual(Union._size_offset(0xff00), (8, 8))
        self.assertTupleEqual(Union._size_offset(0x3c), (4, 2))
        self.assertTupleEqual(Union._size_offset(0xff0), (8, 4))
        self.assertTupleEqual(Union._size_offset(0xffffffff00000000), (32, 32))

        with self.assertRaises(AssertionError):
            Union._size_offset(0xf0f0)  # non-contiguous mask

    def test_bitfield(self):
        class X(Union):
            f1 = Union._bitfield(size=2, offset=0)
            f2 = Union._bitfield(mask=0x3c)
            f3 = Union._bitfield(size=6, offset=6)
            f4 = Union._bitfield(size=8, offset=12)
            f5 = Union._bitfield(size=16, offset=20)

        x = X()

        self.assertEqual(x._value, 0)
        self.assertTupleEqual(x._members, ('f1', 'f2', 'f3', 'f4', 'f5'))
        self.assertEqual(x.f1, 0)
        self.assertEqual(x.f2, 0)
        self.assertEqual(x.f3, 0)
        self.assertEqual(x.f4, 0)
        self.assertEqual(x.f5, 0)

        x.f1 = 2
        expected = 2
        self.assertEqual(x._value, expected)
        self.assertEqual(x.f1, 2)
        self.assertEqual(x.f2, 0)
        self.assertEqual(x.f3, 0)
        self.assertEqual(x.f4, 0)
        self.assertEqual(x.f5, 0)

        x.f2 = 6
        expected += (6 << 2)
        self.assertEqual(x._value, expected)
        self.assertEqual(x.f1, 2)
        self.assertEqual(x.f2, 6)
        self.assertEqual(x.f3, 0)
        self.assertEqual(x.f4, 0)
        self.assertEqual(x.f5, 0)

        x.f3 = 17
        expected += (17 << 6)
        self.assertEqual(x._value, expected)
        self.assertEqual(x.f1, 2)
        self.assertEqual(x.f2, 6)
        self.assertEqual(x.f3, 17)
        self.assertEqual(x.f4, 0)
        self.assertEqual(x.f5, 0)

        x.f4 = 218
        expected += (218 << 12)
        self.assertEqual(x._value, expected)
        self.assertEqual(x.f1, 2)
        self.assertEqual(x.f2, 6)
        self.assertEqual(x.f3, 17)
        self.assertEqual(x.f4, 218)
        self.assertEqual(x.f5, 0)

        x.f5 = 51529
        expected += (51529 << 20)
        self.assertEqual(x._value, expected)
        self.assertEqual(x.f1, 2)
        self.assertEqual(x.f2, 6)
        self.assertEqual(x.f3, 17)
        self.assertEqual(x.f4, 218)
        self.assertEqual(x.f5, 51529)

        x = X(f1=2, f2=6, f3=17, f4=218, f5=51529)
        self.assertEqual(x._value, expected)
        self.assertEqual(x.f1, 2)
        self.assertEqual(x.f2, 6)
        self.assertEqual(x.f3, 17)
        self.assertEqual(x.f4, 218)
        self.assertEqual(x.f5, 51529)

        with self.assertRaises(ValueError):
            Union._bitfield()  # no arguments

        with self.assertRaises(ValueError):
            Union._bitfield(size=5, offset=3, mask=0xf0)  # too many arguments

        with self.assertRaises(ValueError):
            Union._bitfield(size=5)  # missing offset

        with self.assertRaises(ValueError):
            Union._bitfield(offset=3)  # missing size

        with self.assertRaises(AssertionError):
            Union._bitfield(mask=0xf0f0)  # non-contiguous mask

    def test_single(self):
        class X(Union):
            foo = Union._single()

        x = X(foo=5)
        self.assertEqual(x._value, 5)
        self.assertEqual(x.foo, 5)

        x.foo = 17
        self.assertEqual(x._value, 17)
        self.assertEqual(x.foo, 17)

    def test_array(self):
        class X(Union):
            a1 = Union._array(32, 1)
            a2 = Union._array(16, 2, endian=Endian.LITTLE)
            a3 = Union._array(8, 4)
            a4 = Union._array(4, 8, endian=Endian.LITTLE)
            a5 = Union._array(32, 1, endian=Endian.BIG)
            a6 = Union._array(16, 2, endian=Endian.BIG)
            a7 = Union._array(8, 4, endian=Endian.BIG)
            a8 = Union._array(4, 8, endian=Endian.BIG)

        x = X(0xfa42d034)

        self.assertEqual(x._value, 0xfa42d034)
        self.assertListEqual(x.a1, [0xfa42d034])
        self.assertListEqual(x.a2, [0xd034, 0xfa42])
        self.assertListEqual(x.a3, [0x34, 0xd0, 0x42, 0xfa])
        self.assertListEqual(x.a4, [4, 3, 0, 13, 2, 4, 10, 15])

        self.assertListEqual(x.a5, [0xfa42d034])
        self.assertListEqual(x.a6, [0xfa42, 0xd034])
        self.assertListEqual(x.a7, [0xfa, 0x42, 0xd0, 0x34])
        self.assertListEqual(x.a8, [15, 10, 4, 2, 13, 0, 3, 4])

        x.a4 = [1, 2, 3, 0, 0, 0, 0, 0]
        self.assertEqual(x._value, 0x321)
        self.assertListEqual(x.a1, [0x321])
        self.assertListEqual(x.a2, [0x321, 0x0])
        self.assertListEqual(x.a3, [0x21, 0x3, 0x0, 0x0])
        self.assertListEqual(x.a4, [1, 2, 3, 0, 0, 0, 0, 0])

        self.assertListEqual(x.a5, [0x321])
        self.assertListEqual(x.a6, [0x0, 0x321])
        self.assertListEqual(x.a7, [0x0, 0x0, 0x3, 0x21])
        self.assertListEqual(x.a8, [0, 0, 0, 0, 0, 3, 2, 1])

        x.a3 = [0x12, 0x34, 0x56, 0x78]
        self.assertEqual(x._value, 0x78563412)
        self.assertListEqual(x.a1, [0x78563412])
        self.assertListEqual(x.a2, [0x3412, 0x7856])
        self.assertListEqual(x.a3, [0x12, 0x34, 0x56, 0x78])
        self.assertListEqual(x.a4, [2, 1, 4, 3, 6, 5, 8, 7])

        self.assertListEqual(x.a5, [0x78563412])
        self.assertListEqual(x.a6, [0x7856, 0x3412])
        self.assertListEqual(x.a7, [0x78, 0x56, 0x34, 0x12])
        self.assertListEqual(x.a8, [7, 8, 5, 6, 3, 4, 1, 2])

        x.a8 = [1, 2, 3, 4, 5, 6, 7, 8]
        self.assertEqual(x._value, 0x12345678)
        self.assertListEqual(x.a1, [0x12345678])
        self.assertListEqual(x.a2, [0x5678, 0x1234])
        self.assertListEqual(x.a3, [0x78, 0x56, 0x34, 0x12])
        self.assertListEqual(x.a4, [8, 7, 6, 5, 4, 3, 2, 1])

        self.assertListEqual(x.a5, [0x12345678])
        self.assertListEqual(x.a6, [0x1234, 0x5678])
        self.assertListEqual(x.a7, [0x12, 0x34, 0x56, 0x78])
        self.assertListEqual(x.a8, [1, 2, 3, 4, 5, 6, 7, 8])

        with self.assertRaises(TypeError):
            Union._array()  # missing parameters

        with self.assertRaises(AssertionError):
            x.a4 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 14, 15]  # array too long

        with self.assertRaises(AssertionError):
            x.a4 = [8, 9, 10, 11, 12, 14, 14, 16]  # value too large

    def test_string(self):
        class X(Union):
            foo = Union._string(8, 0)
            bar = Union._string(8, 8, 'ascii')
            data = Union._array(8, 16)

        x = X(foo='foo', bar='bar')

        bytes = b'foo'.ljust(8, b'\0') + b'bar'.ljust(8, b'\0')
        self.assertEqual(x._value, int.from_bytes(bytes, byteorder='little'))
        self.assertEqual(x.foo, 'foo')
        self.assertEqual(x.bar, 'bar')
        self.assertEqual(x.data, [102, 111, 111, 0, 0, 0, 0, 0, 98, 97, 114, 0, 0, 0, 0, 0])

        x.foo = '12345678'
        x.bar = 'other'
        bytes = b'12345678other'.ljust(16, b'\0')
        self.assertEqual(x._value, int.from_bytes(bytes, byteorder='little'))
        self.assertEqual(x.foo, '12345678')
        self.assertEqual(x.bar, 'other')
        self.assertEqual(x.data, [49, 50, 51, 52, 53, 54, 55, 56, 111, 116, 104, 101, 114, 0, 0, 0])

        with self.assertRaises(AssertionError):
            x.foo = '123456789'  # string too long

        with self.assertRaises(UnicodeDecodeError):
            x._value = 2**(16*8) - 1
            print(x.foo)  # decode error

    def test_repr(self):
        class X(Union):
            b1 = Union._bitfield(mask=0x0f)
            b2 = Union._bitfield(mask=0xf0)
            a1 = Union._array(size=8, count=1)
            foo = Union._string(8, 1)
            bar = Union._string(8, 9)

        x = X(b1=5, b2=7, foo='foo', bar='bar')

        self.assertTupleEqual(x._members, ('a1', 'b1', 'b2', 'bar', 'foo'))
        self.assertEqual(x.b1, 5)
        self.assertEqual(x.b2, 7)
        self.assertEqual(x.a1, [0x75])
        self.assertEqual(x.foo, 'foo')
        self.assertEqual(x.bar, 'bar')
        self.assertEqual(repr(x), "X(a1=[117], b1=5, b2=7, bar='bar', foo='foo')")


if __name__ == '__main__':
    unittest.main()
