"""Compile production lobby HLSL with installed D3DX9_36; no game/account needed."""
import ctypes as c
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def raw_shader(path):
    text=path.read_text(encoding='utf-8')
    return text.split('R"HLSL(',1)[1].split(')HLSL"',1)[0]

def method(obj,index,restype,*types):
    table=c.cast(obj,c.POINTER(c.POINTER(c.c_void_p))).contents
    return c.WINFUNCTYPE(restype,c.c_void_p,*types)(table[index])

def buffer(obj):
    if not obj:return b''
    address=method(obj,3,c.c_void_p)(obj)
    size=method(obj,4,c.c_ulong)(obj)
    return c.string_at(address,size)

def main():
    dll=c.WinDLL('d3dx9_36.dll')
    compile=dll.D3DXCompileShader
    compile.argtypes=[c.c_char_p,c.c_uint,c.c_void_p,c.c_void_p,c.c_char_p,c.c_char_p,c.c_ulong,c.POINTER(c.c_void_p),c.POINTER(c.c_void_p),c.c_void_p]
    compile.restype=c.c_long
    native=ROOT/'scripts/native'
    shaders={'orbit':(raw_shader(native/'client455_lobby_orbit_shader.inc'),0),
             'station-material':(raw_shader(native/'client455_lobby_lighting_shader.h')+raw_shader(native/'client455_lobby_material.inc'),1<<15)}
    results=[]
    for name,(shader,flags) in shaders.items():
        for entry,profile in [(b'VS',b'vs_3_0'),(b'PS',b'ps_3_0')]:
            code,error=c.c_void_p(),c.c_void_p();source=shader.encode('ascii')
            hr=compile(source,len(source),None,None,entry,profile,flags,c.byref(code),c.byref(error),None)
            message=buffer(error).rstrip(b'\0').decode('ascii',errors='replace')
            row=dict(shader=name,profile=profile.decode(),hresult=hr,bytes=len(buffer(code)),message=message)
            for obj in [code,error]:
                if obj:method(obj,2,c.c_ulong)(obj)
            results.append(row)
            if hr<0:raise RuntimeError(json.dumps(row))
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
