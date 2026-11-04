import struct,unittest
from ani455 import decode,AniError
from audit_client455_animation import synthetic

class AniTests(unittest.TestCase):
    def test_empty_onebyte(self):
        a=decode(b'\0');self.assertEqual(a.consumed,2);self.assertEqual(a.encode(),b'\0')
    def test_high_byte_ignored(self):
        a=decode(b'\0\xffTRAIL');self.assertFalse(a.tracks);self.assertEqual(a.trailing,b'TRAIL');self.assertEqual(a.encode(),b'\0\xffTRAIL')
    def test_channels_and_disabled_max(self):
        raw=dict(synthetic())['channels'];a=decode(raw);self.assertEqual(a.maximum,65535);self.assertEqual(a.tracks[0].counts,(2,1,0,2));self.assertFalse(a.tracks[1].enabled);self.assertEqual(a.encode(),raw)
    def test_all_prefix_truncations(self):
        raw=dict(synthetic())['channels']
        for n in range(len(raw)):
            with self.subTest(n=n),self.assertRaises(AniError):decode(raw[:n])
    def test_huge_channel_count(self):
        raw=bytearray(dict(synthetic())['channels']);struct.pack_into('<H',raw,142,65535)
        with self.assertRaises(AniError):decode(raw)
    def test_trailing_roundtrip(self):
        raw=dict(synthetic())['duplicate']+b'EXTRA';self.assertEqual(decode(raw).encode(),raw);self.assertEqual(decode(raw).trailing,b'EXTRA')
if __name__=='__main__':unittest.main()
