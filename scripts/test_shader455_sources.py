import unittest,json,hashlib
from audit_client455_shaders import sections
from compare_client_binaries import WS
class ShaderSourcesTests(unittest.TestCase):
    def test_real_sections(self):
        ref=json.loads((WS/'inventory/client455-shaders-reference.json').read_text(encoding='utf-8'))
        for item in ref['programs']:
            actual=sections((WS/item['decoded']).read_bytes())
            for label,data in zip(['vertex','pixel'],actual):self.assertEqual(None if data is None else hashlib.sha256(data).hexdigest(),item[label+'_sha256'])
    def test_reversed_and_crlf_sections(self):
        self.assertEqual(sections(b'ignored\n[pixel shader]\r\nP\r\n[vertex shader]\nV'),[b'V',b'P\r\n'])
    def test_empty_truncated_and_embedded_nul(self):
        for raw in [b'',b'[vertex shader',b'\0[vertex shader]V']:
            self.assertEqual(sections(raw),[None,None])
        self.assertEqual(sections(b'[vertex shader]'),[b'',None])
    def test_case_sensitive_markers(self):
        self.assertEqual(sections(b'[VERTEX SHADER]wrong\n[pixel shader]P'),[None,b'P'])
if __name__=='__main__':unittest.main()
