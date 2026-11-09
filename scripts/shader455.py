"""Pinned137-byte repeating XOR for supplied .sho source containers."""
import json
from pathlib import Path
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS


def key():
    pins=json.loads((WS/'config/client-target.json').read_text());result=None
    for folder,name in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';require(sha(path)==pins[name]['sha256'],'Pinned shader key input');value=read_va(path.read_bytes(),0xb39918,134)+bytes(3)
        require(result is None or result==value,'Both455 shader keys agree');result=value
    return result


def xor(data,mask):
    require(len(mask)==137,'Actual key domain');return bytes(value^mask[i%137] for i,value in enumerate(data))


def main():
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);mask=key();root=WS/'artifacts/client455-progress/special-shader134';root.mkdir(parents=True,exist_ok=True)
    for name in ['vFraction','vPlazma','pFraction','pPlazma']:
        file=client/'System/Shader'/(name+'.sho');decoded=xor(file.read_bytes(),mask);require(xor(decoded,mask)==file.read_bytes(),'Actual encrypted source roundtrip');(root/(name+'.hlsl')).write_bytes(decoded)
        print(name+':'+str(len(decoded))+'bytes;'+decoded[:90].decode('ascii',errors='backslashreplace'))


if __name__=='__main__':main()
