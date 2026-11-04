"""Small synthetic PE32 import/delay tables, including malformed boundaries."""
import struct
import unittest
from probe_client_helpers import import_names


def fixture():
    raw=bytearray(1024)
    raw[:2]=b'MZ'
    struct.pack_into('<I',raw,0x3c,0x80)
    raw[0x80:0x84]=b'PE\0\0'
    struct.pack_into('<HH',raw,0x84,0x14c,1)
    struct.pack_into('<H',raw,0x94,224)
    struct.pack_into('<H',raw,0x98,0x10b)
    struct.pack_into('<I',raw,0x98+28,0x400000)
    section=0x98+224
    raw[section:section+8]=b'.rdata\0\0'
    struct.pack_into('<IIII',raw,section+8,512,0x1000,512,512)
    struct.pack_into('<II',raw,0x98+96+8,0x1000,40)
    struct.pack_into('<II',raw,0x98+96+13*8,0x1040,64)
    struct.pack_into('<I',raw,0x200+12,0x1100)
    struct.pack_into('<II',raw,0x240,1,0x1120)
    raw[0x300:0x30d]=b'KERNEL32.dll\0'
    raw[0x320:0x329]=b'PDLL.dll\0'
    return raw


class ImportTests(unittest.TestCase):
    def test_real_layouts(self):
        raw=fixture()
        self.assertEqual(import_names(raw,1),['kernel32.dll'])
        self.assertEqual(import_names(raw,13),['pdll.dll'])

    def test_absent_tables(self):
        raw=fixture()
        struct.pack_into('<II',raw,0x98+96+8,0,0)
        self.assertEqual(import_names(raw,1),[])

    def test_truncated_and_invalid_ranges(self):
        for pointer,size in [(0x1000,19),(0x11f0,40),(0x9999,40)]:
            raw=fixture()
            struct.pack_into('<II',raw,0x98+96+8,pointer,size)
            with self.subTest(pointer=pointer,size=size),self.assertRaises(ValueError):
                import_names(raw,1)
        with self.assertRaises(ValueError): import_names(fixture()[:-1],1)

    def test_invalid_names_and_delay_attributes(self):
        for mode in ('pointer','terminator','attribute'):
            raw=fixture()
            if mode=='pointer': struct.pack_into('<I',raw,0x20c,0x9999)
            elif mode=='terminator':
                struct.pack_into('<I',raw,0x20c,0x11fd)
                raw[-3:]=b'ABC'
            else: struct.pack_into('<I',raw,0x240,0)
            with self.subTest(mode=mode),self.assertRaises(ValueError):
                import_names(raw,13 if mode=='attribute' else 1)


if __name__=='__main__': unittest.main()
