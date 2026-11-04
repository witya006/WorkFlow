"""Small boundary fixtures for resource inspection; no game binaries executed."""
import struct
import unittest
from map455 import MapFile, inspect_r3t
from rpk455 import Rpk


def archive():
    nodes=[(b'.\\',0,2,1,3),(b'dir',0,3,2,1),
           (b'a.spt',3,5,0,0),(b'b.spt',0xfffffffc,5,0,0)]
    return (struct.pack('<II4I4i',0x3f800000,4,0,2,3,1,-1,-1,0,3)
            +b''.join(struct.pack('<52sIHHI',*node) for node in nodes)+b'oneTWO')


def mutate(data,offset,fmt,value):
    result=bytearray(data);struct.pack_into(fmt,result,offset,value);return bytes(result)


class RpkTests(unittest.TestCase):
    def test_rebuild_and_broken_size(self):
        data=archive();parsed=Rpk(data)
        self.assertEqual(parsed.to_bytes(),data)
        self.assertEqual(parsed.read(b'DIR/A.SPT'),b'one')
        self.assertEqual(parsed.read(b'dir\\b.spt'),b'TWO')
        self.assertEqual(parsed.size_mismatches,[3])

    def test_header_tables(self):
        for data in (b'',archive()[:8],mutate(archive(),0,'I',0),mutate(archive(),8,'I',2)):
            with self.subTest(size=len(data)),self.assertRaises(ValueError):Rpk(data)

    def test_tree_and_names(self):
        # Directory child -> itself; out-of-range root children; unsafe filename.
        for data in (mutate(archive(),40+60,'I',0),mutate(archive(),40+60,'I',4),
                     mutate(archive(),40+64*2,'52s',b'..'),
                     mutate(archive(),40+64*3,'52s',b'A.SPT')):
            with self.subTest(data=data[:12]),self.assertRaises(ValueError):Rpk(data)

    def test_bad_payload_offset(self):
        for offset in (-2,7):
            with self.subTest(offset=offset),self.assertRaises(ValueError):Rpk(mutate(archive(),32,'i',offset))


class MapTests(unittest.TestCase):
    def test_empty_header_roundtrip(self):
        for kind,version,n in [('bsp',39,85),('ebp',20,48),('r3e',113,10)]:
            data=struct.pack('<I',version)+(bytes(4) if kind=='r3e' else b'')+bytes(n*8)
            parsed=MapFile(data,kind)
            self.assertEqual(parsed.to_bytes(),data)
            self.assertEqual(parsed.sequential_end(),len(data))

    def test_bounded_lumps(self):
        base=struct.pack('<I',39)+bytes(85*8)
        for data in (base[:683],mutate(base,0,'I',40),
                     base[:4]+struct.pack('<II',684,12)+base[12:],
                     base[:4]+struct.pack('<II',4,12)+base[12:]+bytes(12),
                     base[:4]+struct.pack('<II',684,11)+base[12:]+bytes(11)):
            with self.subTest(size=len(data)),self.assertRaises(ValueError):MapFile(data,'bsp')

    def test_overlap_is_explicit_and_offsets_preserved(self):
        data=struct.pack('<I4I',39,684,12,684,4)+bytes(83*8)+bytes(16)
        parsed=MapFile(data,'bsp')
        self.assertEqual(parsed.declared_overlaps,[('CFaceId','CPlanes')])
        self.assertEqual(parsed.sequential_offset_mismatches(),[{'name':'CFaceId','declared':684,'sequential':696}])
        self.assertEqual(parsed.to_bytes(),data)

    def test_r3t_masked_and_plain(self):
        dds=bytearray(128);dds[:4]=b'DDS ';struct.pack_into('<I',dds,4,124)
        struct.pack_into('<II',dds,12,16,32);dds[84:88]=b'DXT1'
        mask=bytes(range(128))
        for encrypted in (False,True):
            header=bytes(a^b for a,b in zip(dds,mask)) if encrypted else bytes(dds)
            data=struct.pack('<II',0x3f99999a,1)+bytes(128)+struct.pack('<I',384)+header+bytes(256)
            result=inspect_r3t(data,mask)['textures'][0]
            self.assertEqual((result['width'],result['height'],result['masked_header']),(32,16,encrypted))
            for bad in (data[:7],data[:-1],data+b'X',mutate(data,0,'I',0),mutate(data,136,'I',0xffffffff)):
                with self.subTest(encrypted=encrypted,size=len(bad)),self.assertRaises(ValueError):inspect_r3t(bad,mask)
            if encrypted:
                with self.assertRaises(ValueError):inspect_r3t(data)


if __name__=='__main__':unittest.main()
