import unittest
from prepare_client455_normal import section

class ProductionSplitTests(unittest.TestCase):
    def test_nested_and_noncode_braces(self):
        raw=b'// first() {\nfirst(){f("}");/* } */if(1){g();}}\nlast(){if(1){g();}}\nafter();'
        start,end=section(raw,b'first()',b'last()')
        self.assertEqual(raw[start:end],b'first(){f("}");/* } */if(1){g();}}\nlast(){if(1){g();}}')
        self.assertEqual(raw[end:],b'\nafter();')
    def test_missing_marker(self):
        with self.assertRaises(ValueError):section(b'first(){}',b'first()',b'absent()')
    def test_unterminated_body(self):
        with self.assertRaises(ValueError):section(b'first(){}last(){if(1){}',b'first()',b'last()')

if __name__=='__main__':unittest.main()
