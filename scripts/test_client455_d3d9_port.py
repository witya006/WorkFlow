"""Guard source rewrites against nested expressions,comments and lost bases."""
import unittest
from client455_d3d9_port import migrate,pointer_calls

class Migration(unittest.TestCase):
    def test_real_nested_calls(self):
        text=b'if(FAILED(GetD3dDevice()->CreateVertexBuffer(size(1,2), flags, fvf, D3DPOOL_MANAGED, &buffer))) return FALSE;'
        changed,_=migrate(text);self.assertIn(b'&buffer, NULL)',changed);self.assertEqual(changed.count(b'NULL'),1)
    def test_comments_and_strings(self):
        text=b'// p->SetStreamSource(0,v,16)\r\nconst char* s="p->SetStreamSource(0,v,16)";\r\np->SetStreamSource(0,v,16);'
        changed,_=migrate(text);self.assertEqual(changed,text[:text.rindex(b'p->')]+b'p->SetStreamSource(0, v, 0, 16);')
    def test_comment_at_argument_boundary(self):
        text=b'p->CreateVertexBuffer(size, flags\r\n// old default-pool argument\r\n, fvf, D3DPOOL_MANAGED, &buffer);'
        changed,_=migrate(text);self.assertIn(b'// old default-pool argument\r\n, fvf',changed);self.assertIn(b'&buffer, NULL)',changed)
    def test_sampler_and_fixed_function(self):
        changed,_=migrate(b'GetD3dDevice()->SetTextureStageState(0,D3DTSS_MINFILTER, D3DTEXF_LINEAR); p->SetVertexShader(D3DFVF_R3VERTEX_TEX2);')
        self.assertIn(b'SetSamplerState(0, D3DSAMP_MINFILTER, D3DTEXF_LINEAR)',changed);self.assertIn(b'RF455_SetFixedVertexFormat(p, D3DFVF_R3VERTEX_TEX2)',changed)
    def test_indices_base_and_malformed(self):
        changed,_=migrate(b'p->SetIndices(ib,0);p->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,n,0,k);');self.assertIn(b'DrawIndexedPrimitive(D3DPT_TRIANGLELIST, 0, 0, n, 0, k)',changed)
        with self.assertRaises(ValueError):migrate(b'p->SetIndices(ib,4);')
        with self.assertRaises(ValueError):pointer_calls(b'p->SetTexture(0,t;')
if __name__=='__main__':unittest.main()
