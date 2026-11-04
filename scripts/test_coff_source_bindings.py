"""Check real COFF substitution boundaries, instruction preservation and routing."""
import json,struct,unittest
from compare_client_binaries import WS
from coff_source_bindings import BINDINGS,source_bindings
from export_character_analysis import coff_function_records
from build_client455_x87_math import object_relocations

class SourceBindingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        report=json.loads((WS/'inventory/character-stdio-adapter.json').read_text(encoding='utf-8'))
        cls.raw=[(WS/x['object']).read_bytes() for x in report['objects']]
    def test_ten_real_objects(self):
        total=0
        for raw in self.raw:
            output,changes=source_bindings(raw);total+=len(changes)
            before=coff_function_records(raw);after=coff_function_records(output)
            for name,f in before.items():self.assertEqual(f['bytes'],after[BINDINGS.get(name,name)]['bytes'])
            if not changes:self.assertEqual(raw,output)
        self.assertEqual(total,8)
    def test_actual_init_callers(self):
        raw=self.raw[6];output,changes=source_bindings(raw)
        init=coff_function_records(raw)['?InitVertex@@YAXPAVObjectData@@PAVCHARACTEROBJECT@@1PAVTextureManager@@_N@Z']
        callers=[x for c in changes for x in c['redirected_callers'] if x['section']==init['section'] and init['section_offset']<=int(x['offset'],16)<init['section_offset']+init['size']]
        self.assertEqual(len(callers),0) # Retained comparison group stays independent.
        after=coff_function_records(output)[BINDINGS['?InitVertex@@YAXPAVObjectData@@PAVCHARACTEROBJECT@@1PAVTextureManager@@_N@Z']]
        references=object_relocations(output,after,after['size'])
        actual={r['symbol'] for r in references}
        for name in BINDINGS.values():
            if name not in ['_RFCharacterOriginal_InitVertex','_RFCharacterOriginal_RematchParents','_RFCharacterOriginal_FindByName']:self.assertIn(name,actual)
    def test_truncated_tables(self):
        raw=self.raw[6]
        for n in [0,19,20,100,len(raw)-1]:
            with self.subTest(size=n),self.assertRaises(ValueError):source_bindings(raw[:n])
    def test_bad_relocations(self):
        raw=bytearray(self.raw[6]);sections=struct.unpack_from('<H',raw,2)[0]
        header=next(20+40*s for s in range(sections) if struct.unpack_from('<H',raw,20+40*s+32)[0])
        struct.pack_into('<I',raw,header+24,len(raw)+100)
        with self.assertRaises(ValueError):source_bindings(bytes(raw))

if __name__=='__main__':unittest.main()
