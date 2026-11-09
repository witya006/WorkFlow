"""Bounded analysis parser boundaries;does not certify unsafe native error paths."""
import unittest,struct,json
from compare_client_binaries import WS
from prepare_client455_special_shaders import parse_init


class BinaryListTests(unittest.TestCase):
    def setUp(self):
        r=json.loads((WS/'inventory/client455-special-shaders-inputs.json').read_text());self.raw=(WS/r['inputs'][0]['file']).read_bytes()
    def test_real_list(self):
        r=parse_init(self.raw);self.assertEqual(len(r['stages']),4);self.assertEqual(r['effects'],[]);self.assertEqual(r['objects'],[]);self.assertEqual(r['bytes'],1424)
    def test_truncated_boundaries(self):
        for end in [0,255,256,259,260,263,519,551,1127,1420,1423]:
            with self.subTest(end=end),self.assertRaises(ValueError):parse_init(self.raw[:end])
    def test_capacity_and_termination(self):
        for n in [-1,129,0x7fffffff]:
            damaged=self.raw[:256]+struct.pack('<i',n)+self.raw[260:]
            with self.subTest(n=n),self.assertRaises(ValueError):parse_init(damaged)
        with self.assertRaises(ValueError):parse_init(b'X'*256+self.raw[256:])
        with self.assertRaises(ValueError):parse_init(self.raw+b'X')
    def test_parameter_row_size(self):
        base=self.raw[:-4]+struct.pack('<i',1)+struct.pack('<iii',1,0,1)
        self.assertEqual(parse_init(base+bytes(range(196)))['objects'][0]['parameters'],[bytes(range(196)).hex()])
        with self.assertRaises(ValueError):parse_init(base+bytes(195))


if __name__=='__main__':
    result=unittest.main(exit=False).result
    from audit_client455_item_payloads import record
    output=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,script=record(WS/'scripts/test_client455_special_shader_list.py'),parser=record(WS/'scripts/prepare_client455_special_shaders.py'),scope='Bounded analysis parser only;native malformed-input equivalence remains open')
    (WS/'inventory/client455-special-shaders-parser-tests.json').write_text(json.dumps(output,indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
