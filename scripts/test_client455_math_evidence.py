import struct
import unittest
from compare_client_binaries import WS
from export_character_analysis import coff_function_records
from build_client455_x87_math import object_relocations


class MathEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(WS/'work/recovered/client455/x87-math/x87-math.obj').read_bytes()
        cls.record=coff_function_records(cls.raw)['_RF455_MatrixInvert']

    def test_real_relocation_and_extent(self):
        self.assertEqual(object_relocations(self.raw,self.record,485),
            [{'offset':33,'type':6,'symbol':'_RF455_AffineEpsilon'}])
        transform=coff_function_records(self.raw)['_RF455_Vector3fTransform']
        self.assertEqual(object_relocations(self.raw,transform,132),[])
        with self.assertRaises(ValueError): object_relocations(self.raw,self.record,1000000)

    def test_truncated_tables(self):
        for raw in (b'',self.raw[:19],self.raw[:-1]):
            with self.subTest(size=len(raw)),self.assertRaises(ValueError):
                object_relocations(raw,self.record,485)

    def test_bad_relocation_table_and_symbol(self):
        section=20+40*(self.record['section']-1)
        for mode in ('table','symbol','name'):
            raw=bytearray(self.raw)
            if mode=='table': struct.pack_into('<I',raw,section+24,len(raw)-1)
            else:
                reloc=struct.unpack_from('<I',raw,section+24)[0]
                if mode=='symbol': struct.pack_into('<I',raw,reloc+4,0xffffffff)
                else:
                    index=struct.unpack_from('<I',raw,reloc+4)[0]
                    symbols=struct.unpack_from('<I',raw,8)[0]
                    struct.pack_into('<II',raw,symbols+18*index,0,0xffffffff)
            with self.subTest(mode=mode),self.assertRaises(ValueError):
                object_relocations(raw,self.record,485)


if __name__=='__main__': unittest.main()
