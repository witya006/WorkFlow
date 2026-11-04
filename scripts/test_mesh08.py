import struct,unittest
from dataclasses import replace
from mesh08 import decode,Mesh08Error,HEADER_BYTES,INDEX_LIMIT,Mesh08Part,Mesh08

def fixture(indices=(0,1,2),vertices_count=3,bones=1,trailing=b''):
    header=bytearray(HEADER_BYTES);header[:5]=b'ROOT\0';header[100:107]=b'Parent\0';header[398:408]=b'ABC.DDS\0\0\0'
    vertices=bytes((i*17+3)%256 for i in range(64*vertices_count));bone=struct.pack('<I',2)+b'A\0'+bytes(98)+b'B\0'+bytes(298)
    assert len(bone)==404
    return b'MESH08\x01\x00'+header+struct.pack('<H',vertices_count)+vertices+struct.pack('<H',len(indices))+struct.pack('<'+'H'*len(indices),*indices)+struct.pack('<H',bones)+bone*bones+trailing

class Mesh08Tests(unittest.TestCase):
    def test_empty_and_trailing(self):
        for tail in [b'',b'extra\0\xff']:
            data=b'MESH08\0\0'+tail;model=decode(data);self.assertEqual(model.consumed,8);self.assertEqual(model.trailing,tail);self.assertEqual(model.encode(),data)
    def test_payload_offsets_and_lossless(self):
        raw=fixture(trailing=b'future');model=decode(raw);part=model.parts[0]
        self.assertEqual((part.offset,part.vertex_offset,part.index_offset,part.bone_offset),(8,703,897,905))
        self.assertEqual((part.name,part.parent_name,part.primary_texture),(b'ROOT',b'Parent',b'ABC.DDS'))
        self.assertEqual((part.vertex_count,part.index_count,part.bone_count),(3,3,1));self.assertEqual(model.encode(),raw)
    def test_every_truncation(self):
        raw=fixture()
        for n in range(len(raw)):
            with self.subTest(size=n),self.assertRaises(Mesh08Error):decode(raw[:n])
    def test_magic_and_count(self):
        for raw in [b'mesh08\0\0',b'MESH09\0\0',b'MESH08\xff\xff']:
            with self.assertRaises(Mesh08Error):decode(raw)
    def test_limit_and_nontriangle_indices(self):
        self.assertEqual(decode(fixture(indices=(0,)*INDEX_LIMIT,vertices_count=1,bones=0)).parts[0].index_count,INDEX_LIMIT)
        raw=fixture(indices=(0,)*(INDEX_LIMIT+1),vertices_count=1,bones=0)
        with self.assertRaises(Mesh08Error):decode(raw)
        self.assertEqual(decode(raw,enforce_index_limit=False).encode(),raw)
    def test_opaque_float_bits_and_unchecked_index_values(self):
        raw=bytearray(fixture(indices=(65535,0,1)))
        raw[703:711]=bytes.fromhex('0100807f00000080') # NaN payload and negative zero remain bytes.
        model=decode(raw);self.assertEqual(model.encode(),raw)
        self.assertEqual(model.parts[0].indices[:2],b'\xff\xff') # Format reader does not invent a clamp.
    def test_encoder_rejects_inconsistent_payload(self):
        part=decode(fixture()).parts[0]
        with self.assertRaises(Mesh08Error):replace(part,vertex_count=2).encode()

if __name__=='__main__':unittest.main()
