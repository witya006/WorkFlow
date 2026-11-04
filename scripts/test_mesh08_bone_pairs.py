"""Boundaries of the plain-BN fixture-name extraction, not a complete BN loader."""
import struct,unittest
from audit_mesh08_bone_pairs import basename,plain_names

def fixture(name=b'ROOT',compact=False):
    head=bytearray(693);head[:len(name)]=name
    struct.pack_into('<I',head,642,int(compact))
    return b'\x01\0'+head+(b'\0'*4 if compact else b'')

class PairNameTests(unittest.TestCase):
    def test_empty_and_tail(self):
        self.assertEqual(plain_names(b'\0\0'),[])
        with self.assertRaises(ValueError):plain_names(b'\0\0x')
    def test_single_plain_and_compact(self):
        self.assertEqual(plain_names(fixture()),[b'ROOT'])
        self.assertEqual(plain_names(fixture(compact=True)),[b'ROOT'])
    def test_all_truncations(self):
        raw=fixture()
        for length in range(len(raw)):
            with self.subTest(length=length),self.assertRaises(ValueError):plain_names(raw[:length])
    def test_counts_and_geometry(self):
        raw=bytearray(fixture());raw[:2]=b'\x02\0'
        with self.assertRaises(ValueError):plain_names(raw)
        raw=bytearray(fixture());struct.pack_into('<H',raw,2+392,1)
        with self.assertRaises(ValueError):plain_names(raw)
    def test_ascii_basename_keeps_case_and_extension(self):
        for raw in [b'C:\\folder\\Bip01.Head.bn\0',b'folder/Bip01.Head.bn\0']:
            self.assertEqual(basename(raw),b'Bip01.Head.bn')
        self.assertEqual(basename(b'\0'),b'')
    def test_unterminated_and_locale(self):
        with self.assertRaises(ValueError):plain_names(fixture(b'A'*100))
        with self.assertRaises(ValueError):plain_names(fixture(b'\xff'))

if __name__=='__main__':unittest.main()
