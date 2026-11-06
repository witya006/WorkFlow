"""Pin recovered455font/GDI/Unicode/cache and explicitly retain FreeType gaps."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    ranges=[(0x8c5a80,0x47),(0x8c5ae0,0x175),(0x8c5c60,0x2ba),(0x8c5f20,0x70),(0x9057f0,0x1a),(0x905810,0xa),(0x905820,0xbd),(0x905920,0x8b),(0x9059b0,0x153),(0x905b10,0x3e),(0x905b50,0x1f),(0x905b70,0x117),(0x905cf0,0x103),(0x9067e0,0x251),(0x906a40,0x3c),(0x906a80,0x14a),(0x906bd0,0x3f),(0x906c10,0x1be),(0x906dd0,0x18d),(0x906f60,0x627),(0x907710,0x3a0)]
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        rows=[{'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for at,n in ranges]
        if previous is not None and rows!=previous:raise ValueError('Font bodies differ between pins')
        previous=rows;refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':rows})
    report={'scope':'Confirmed GDI/Unicode font/cache/draw route;fullFreeType/ANSI/completeUI acceptance remains open','references':refs,'script_sha256':sha(Path(__file__).read_bytes()),'facts':['8C5A80 strncpy250 twice into256byte names;points9/height12/charset selected by country','905920 D3DXCreateTexture format26/managed,not legacy directCreateTexture','9067E0 DIBheight=-3*points;CreateFontA quality0/pitch0/selectedcharset;measure w for cellWidth/Height','Unicode row cache checks both measured pixel width and character capacity;906DD0 ExtTextOutW +alpha4 upload','907710 truncates by character capacity,emits shadow/outline/bold passes and leaves ALPHABLEND disabled','DrawPrimitiveUP TRIANGLELIST stride28/FVF324;clipping maps texture interval and resulting quad dimensions','8C5AE0 loads3fonts:normal by memory threshold,16point1024x128,24point1024x512;AddFontResource010TTF','8C5C60 implements a distinct optional FreeType route with configfont/locale;it is not replaced by a claimed successful stub'],'gaps':['Full FreeType/configuredfont path,ANSI-specific cache and all othertext methods','Complete original private2040byte layout and oldCRT/x87/allfloatingpoint environments','WholeUI layout/wordwrap/IME/input/reset/gameplay acceptance','Source uses RAII rows and frees overwritten unused stateblocks;original allocation/leak/OOM/unsafe domains not equivalent','GDI glyph output depends on actual Windows installedfonts/fontlinking/DPI;not proof of original455frame parity'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-font-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:21font/bootstrap/cache/draw ranges equal both455PEs;FreeType/wholeUI gaps explicit')
if __name__=='__main__':main()
