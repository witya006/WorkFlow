import struct,unittest
from audit_client455_legacy_models import expand,expected,synthetic

class LegacyOracleTests(unittest.TestCase):
    def test_empty(self):
        header,parts=expected(bytes(2));self.assertFalse(parts);self.assertEqual(header[2:4],bytes(2));self.assertEqual(header[24:28],b'\xa5'*4)
    def test_zero_dictionary_skips_physique(self):
        header,parts=expected(dict(synthetic())['compact_zero_dictionary']);self.assertEqual(len(parts),1);self.assertEqual(parts[0][1][2:],[None,None,None])
    def test_names_padding_and_signed_count(self):
        compact=bytearray(80);struct.pack_into('<iiI',compact,0,7,1,0);struct.pack_into('<ii',compact,40,9,-1)
        result=expand(compact,b'Z\0'+b'x'*98);self.assertEqual(result[8:108],b'Z'+bytes(99));self.assertEqual(result[424+8:424+424],b'\xa5'*416)
    def test_oversized_influence(self):
        compact=bytearray(40);struct.pack_into('<i',compact,4,5)
        with self.assertRaises(ValueError):expand(compact,b'x'*100)
    def test_bad_name_index(self):
        compact=bytearray(40);struct.pack_into('<iiI',compact,0,0,1,1)
        with self.assertRaises(ValueError):expand(compact,b'x'*100)
    def test_nan_quieting(self):
        compact=bytearray(40);struct.pack_into('<iiI',compact,0,0,1,0);struct.pack_into('<I',compact,24,0xff800123)
        self.assertEqual(struct.unpack_from('<I',expand(compact,b'x'*100),408)[0],0xffc00123)
if __name__=='__main__':unittest.main()
