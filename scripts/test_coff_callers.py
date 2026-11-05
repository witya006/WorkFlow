"""Actual source callers and malformed static/relocation boundary checks."""
import struct,unittest
from compare_client_binaries import WS
from verify_client455_animation_timing import calls
from verify_client455_animation_manager import APIS

class CallersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(WS/'work/client-build/build-helper-lab/RF_Online.dir/Release/test_client455_animation_manager.obj').read_bytes()
    def test_actual_static_callers(self):
        selected=calls(self.raw,APIS,include_static=True)
        self.assertEqual({item['target'] for item in selected},set(APIS))
        self.assertTrue(any('collection' in item['caller'] for item in selected))
    def test_existing_external_callers(self):
        raw=(WS/'work/client-build/build-character-diagnostic/RF_Online.dir/Release/cresobject.obj').read_bytes()
        selected=calls(raw,['_RF455_AdvanceAnimationFrameValue','_RF455_InitializeAnimationControl'])
        self.assertEqual(len(selected),3)
        self.assertEqual(sum('CalculateCurrentAnimationFrame' in item['caller'] for item in selected),2)
    def test_invalid_static_function_offset(self):
        raw=bytearray(self.raw);table,count=struct.unpack_from('<II',raw,8);index=0
        while index<count:
            at=table+18*index;section,kind,storage,aux=struct.unpack_from('<hHBB',raw,at+12)
            if section>0 and storage==3 and kind&0x20:
                size=struct.unpack_from('<I',raw,20+40*(section-1)+16)[0];struct.pack_into('<I',raw,at+8,size)
                with self.assertRaises(ValueError):calls(bytes(raw),APIS,include_static=True)
                return
            index+=1+aux
        self.fail('Actual static function symbol missing')
    def test_target_relocation_requires_call_opcode(self):
        raw=bytearray(self.raw);selected=calls(raw,APIS,include_static=True)[0]
        rawAt=struct.unpack_from('<I',raw,20+40*(selected['section']-1)+20)[0]
        raw[rawAt+int(selected['offset'],16)-1]=0x90
        with self.assertRaises(ValueError):calls(bytes(raw),APIS,include_static=True)

if __name__=='__main__':unittest.main()
