"""Exercise real compiler calls/data and malformed COFF bounds."""
import struct,unittest
from compare_client_binaries import WS
from coff_references import parse

class References(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=(WS/'work/client-build/build-character-diagnostic/RF_Online.dir/Release/cresobject.obj').read_bytes()
        cls.engine=(WS/'work/client-build/build-character-diagnostic/R3EngineClientMT.dir/Release/multilayer.obj').read_bytes()
    def test_real_calls_and_addresses(self):
        calls=[r for r in parse(self.client)['references'] if r['symbol'].startswith('?FrameMove@CRender@@')]
        self.assertEqual(len(calls),2);self.assertTrue(all(r['form']=='call' and 'Animation@CResObject@@' in r['caller']['name'] for r in calls))
        values=[r for r in parse(self.engine)['references'] if r['symbol']=='?stTime@@3MA']
        self.assertEqual(len(values),7);self.assertTrue(all(r['relocation']==6 and r['form']=='other' for r in values))
    def test_instruction_change_is_not_counted_as_call(self):
        value=parse(self.client);chosen=next(r for r in value['references'] if r['form']=='call');raw=bytearray(self.client);start=value['sections'][chosen['section']-1]['raw'];raw[start+chosen['offset']-1]=0xe9
        updated=next(r for r in parse(raw)['references'] if r['section']==chosen['section'] and r['offset']==chosen['offset']);self.assertEqual(updated['form'],'tailcall')
    def test_reference_symbol_bounds(self):
        raw=bytearray(self.client);count=struct.unpack_from('<H',raw,2)[0]
        for i in range(count):
            at=20+40*i;reloc=struct.unpack_from('<I',raw,at+24)[0];n=struct.unpack_from('<H',raw,at+32)[0]
            if n:struct.pack_into('<I',raw,reloc+4,0xffffffff);break
        with self.assertRaises(ValueError):parse(raw)
    def test_truncation_and_string_bounds(self):
        for size in [0,19,59,len(self.client)-1]:
            with self.assertRaises(ValueError):parse(self.client[:size])
        raw=bytearray(self.client);table,n=struct.unpack_from('<II',raw,8);index=0
        while index<n:
            at=table+18*index
            if raw[at:at+4]==bytes(4):struct.pack_into('<I',raw,at+4,0xffffffff);break
            index+=1+raw[at+17]
        with self.assertRaises(ValueError):parse(raw)
if __name__=='__main__':unittest.main()
