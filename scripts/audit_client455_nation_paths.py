"""Pin country/path choices directly to both455PEs;fonts/locales are metadata only."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def literal(raw,at):return read_va(raw,at,96).split(b'\0',1)[0]
def main():
    # Addresses resolved from mapper7D29C0 and selector7CFB10, not from port code.
    names=[0xaed7c8,0xaed7c0,0xaed7b8,0xaed7b0,0xaed7a4,0xaed79c,0xaed790,0xaed788,0xaed780,0xaed77c,0xaed770]
    folders=[0xaed38c,0xaed36c,0xaed348,0xaed328,0xaed308,0xaed2ec,0xaed2c8,0xaed2a4,0xaed27c,0xaed25c,0xaed254]
    locales=[0xaed37c,0xaed358,0xaed338,0xaed310,0xaed2f4,0xaed2dc,0xaed2b4,0xaed294,0xaed26c,0xaed310,0xaed244]
    fonts=[0xaed374,0xaed350,0xaed330,0xaed350,0xaed350,0xaed2d0,0xaed2ac,0xaed284,0xaed264,0xaed350,0xaed2ac]
    charsets=[129,1,134,1,1,128,1,204,136,1,222]
    ranges=[('mapper',0x7d29c0,0x179),('profile_reader',0x7d2880,0xda),('selector',0x7cfb10,0x571),('root_accessor',0x5e5b70,0x1b),('font_settings',0x8c5a80,0x47)]
    pins=json.loads((WS/'config/client-target.json').read_text());references=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455binary')
        rows=[{'id':i,'setting':literal(raw,names[i]).decode('ascii'),'folder':literal(raw,folders[i]).decode('ascii'),'crt_locale':literal(raw,locales[i]).decode('ascii'),'font_hex':literal(raw,fonts[i]).hex(),'charset':charsets[i],'literal_rvas':[hex(v-0x400000) for v in [names[i],folders[i],locales[i],fonts[i]]]} for i in range(11)]
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for name,at,size in ranges]
        if literal(raw,0xaed218)!=b'.\\DataTable\\%s':raise ValueError('Changed data-root format')
        common={'rows':rows,'ranges':bodies}
        if previous is not None and common!=previous:raise ValueError('Country/path contracts differ between pins')
        previous=common;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000',**common})
    fixture=WS/'work/client455-port/nation-paths';fixture.mkdir(parents=True,exist_ok=True);data=fixture/'reference.tsv'
    data.write_text('\n'.join('\t'.join(str(row[k]) for k in ['id','setting','folder','crt_locale','font_hex','charset']) for row in rows)+'\n',encoding='ascii')
    report={'scope':'Case-sensitive country mapping and data-root selection;CRT/font records are confirmed metadata,not applied locale acceptance','references':references,'fixture':data.relative_to(WS).as_posix(),'fixture_sha256':sha(data.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'facts':['7D29C0 compares11 country names with _mbscmp;unknown returnsWORDffff','7D2880 reads128bytes Setup/Language from .\\R3Engine.ini;WORD>11 rejected','Country11 cannot be produced by mapper;selector default is Korea','7CFB10 constructs .\\DataTable\\<folder>;USA uses UK CRT locale','7CFB10 setlocale category1 is LC_COLLATE,not LC_CTYPE','Font setter records9x12 and charset;it does not itself render text'],'gaps':['ETCAction country factory/providers and launcher policies','Actual CRT locale/codepage agreement/font application/NDLanguage pack loading','Whole reference bootstrap/network/Create/UI/gameplay and M9'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-nation-paths-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:11country/folder/locale/font records and5function bodies pinned both455PEs')
if __name__=='__main__':main()
