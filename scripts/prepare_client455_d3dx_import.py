"""Retarget the signed SDK's x86 import names to the pinned455D3DX runtime."""
import hashlib,json,re,zipfile
from compare_client_binaries import WS

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text(encoding='utf-8'));package=WS/sdk['package_file']
    if sdk['signature_exit'] or sha(package.read_bytes())!=sdk['package_sha256']:raise ValueError('Verified SDK package required')
    with zipfile.ZipFile(package) as archive:
        names=[n for n in archive.namelist() if n.lower().replace('\\','/').endswith('/release/lib/x86/d3dx9.lib')]
        if len(names)!=1:raise ValueError('Unique x86D3DX import archive required')
        original=archive.read(names[0])
    raw,count=re.subn(rb'd3dx9_43',lambda m:m[0][:-2]+b'36',original,flags=re.I)
    if not count or not raw.startswith(b'!<arch>\n') or len(raw)!=len(original):raise ValueError('Unexpected import descriptor structure')
    root=WS/'work/client455-port/dependencies';root.mkdir(parents=True,exist_ok=True);path=root/'d3dx9_36.lib'
    if path.exists() and path.read_bytes()!=raw:raise ValueError('Preserve differing import library')
    if not path.exists():path.write_bytes(raw)
    report={'scope':'Import archive only;noD3DX runtime code replaced','package_sha256':sdk['package_sha256'],'member':names[0],'original_sha256':sha(original),'library':path.relative_to(WS).as_posix(),'library_sha256':sha(raw),'descriptor_replacements':count,'runtime':'d3dx9_36.dll','runtime_sha256':'c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935','limits':['Unused header exports may be newer than36;final PE importednames must bechecked against actualpinned exports','D3DX_SDK_VERSION inpackageheaders is43;no automatic CheckVersion compatibility claim']}
    (WS/'inventory/client455-d3dx-import.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:x86import archive targets36;{count}same-length descriptor changes')
if __name__=='__main__':main()
