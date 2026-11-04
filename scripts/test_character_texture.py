import dataclasses,struct,unittest
from character_texture import CharacterTextureError,parse_rfs,make_rfs,prepare_dds,synthetic_dds

class CharacterTextureTests(unittest.TestCase):
    def test_rfs_lossless_padding_and_duplicate(self):
        raw=make_rfs([(b'A.RFT',b'abcd'),(b'A.RFT',b'xyz')])+b'tail';parsed=parse_rfs(raw)
        self.assertEqual(parsed.encode(),raw);self.assertEqual(parsed.member(0),b'abcd');self.assertEqual(parsed.member(1),b'xyz')
    def test_rfs_index_truncations(self):
        raw=make_rfs([(b'A.RFT',b'payload')])
        for n in range(68):
            with self.subTest(n=n),self.assertRaises(CharacterTextureError):parse_rfs(raw[:n])
    def test_rfs_unterminated_and_extent(self):
        raw=bytearray(make_rfs([(b'A',b'payload')]));raw[4:60]=b'x'*56
        with self.assertRaises(CharacterTextureError):parse_rfs(raw)
        raw=bytearray(make_rfs([(b'A',b'payload')]));struct.pack_into('<I',raw,60,0xffffffff)
        parsed=parse_rfs(raw);self.assertEqual(parsed.encode(),raw)
        with self.assertRaises(CharacterTextureError):parsed.member(0)
    def test_rfs_empty_and_writer_name(self):
        self.assertEqual(parse_rfs(b'\0'*4+b'tail').encode(),b'\0'*4+b'tail')
        with self.assertRaises(CharacterTextureError):make_rfs([(b'A'*56,b'')])
        item=parse_rfs(make_rfs([(b'A',b'')]))
        with self.assertRaises(CharacterTextureError):dataclasses.replace(item,entries=(dataclasses.replace(item.entries[0],raw_name=b'x'*56),)).encode()
    def test_dds_mask_and_tail(self):
        raw=synthetic_dds()+b'tail';key=bytes(range(128));masked=bytes(a^b for a,b in zip(raw,key))+raw[128:]
        self.assertEqual(prepare_dds(raw,key)['bytes'],raw);self.assertEqual(prepare_dds(masked,key)['bytes'],raw)
    def test_dds_invalid_and_all_short_headers(self):
        for n in range(128):
            with self.subTest(n=n),self.assertRaises(CharacterTextureError):prepare_dds(bytes(n),bytes(128))
        with self.assertRaises(CharacterTextureError):prepare_dds(bytes(128),bytes(128))
    def test_mip_break_quirk_and_guard(self):
        raw=synthetic_dds(4,8,3);p=prepare_dds(raw,bytes(128),1)
        self.assertEqual((p['skip'],p['width'],p['height']),(16,4,4));self.assertEqual(struct.unpack_from('<I',p['bytes'],28)[0],3)
        self.assertEqual(prepare_dds(raw,bytes(128),1,max_width=255)['skip'],0)
    def test_header_repairs(self):
        raw=bytearray(synthetic_dds());struct.pack_into('<I',raw,80,5);self.assertEqual(struct.unpack_from('<I',prepare_dds(raw,bytes(128))['bytes'],80)[0],4)
        struct.pack_into('<I',raw,76,0);self.assertEqual(struct.unpack_from('<II',prepare_dds(raw,bytes(128))['bytes'],76),(32,4))
    def test_cube_and_overskip(self):
        self.assertTrue(prepare_dds(synthetic_dds(cube=True),bytes(128))['cube'])
        raw=bytearray(synthetic_dds());struct.pack_into('<I',raw,20,0xffffffff)
        with self.assertRaises(CharacterTextureError):prepare_dds(raw,bytes(128),1)

if __name__=='__main__':unittest.main()
