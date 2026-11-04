import unittest
from character_ctor_oracle import CtorOracleError,interpret

class ConstructorOracleTests(unittest.TestCase):
    def test_minimal_state(self):
        data=interpret(['mov eax, ecx','retn'],lambda _:0)
        self.assertEqual(data,b'\xa5'*1188)
    def test_outside_object(self):
        with self.assertRaises(CtorOracleError):interpret(['mov dword ptr [ecx+4A4h], 0'],lambda _:0)
    def test_argument_stack_underflow(self):
        with self.assertRaises(CtorOracleError):interpret(['pop eax'],lambda _:0)
    def test_fp_underflow(self):
        with self.assertRaises(CtorOracleError):interpret(['fstp dword ptr [ecx]'],lambda _:0)
    def test_unknown_opcode(self):
        with self.assertRaises(CtorOracleError):interpret(['nop'],lambda _:0)
    def test_bad_helper(self):
        with self.assertRaises(CtorOracleError):interpret(['call arbitrary'],lambda _:0)
    def test_return_requires_balanced_state(self):
        with self.assertRaises(CtorOracleError):interpret(['mov eax, ecx','fld1','retn'],lambda _:0)
    def test_missing_return(self):
        with self.assertRaises(CtorOracleError):interpret(['mov eax, ecx'],lambda _:0)
    def test_after_return(self):
        with self.assertRaises(CtorOracleError):interpret(['mov eax, ecx','retn','push eax'],lambda _:0)
if __name__=='__main__':unittest.main()
