"""Check the exact direct FILE flag access seen in Character against modern /MT.

The test reads only its own stream/fixture. No game executable or DLL is executed.
"""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from export_character_analysis import coff_function_records, WS
from recover_character_layouts import operand


def main():
    source = WS/'work/character-reverse/member_03.obj'
    record = coff_function_records(source.read_bytes())['?LoadEffectFileList@EffectList@@QAEXPAD@Z']
    offset = operand(record, 0x31, bytes.fromhex('8a46'), 1)
    mask = operand(record, 0x38, bytes.fromhex('a8'), 1)
    if (offset, mask) != (12, 16):
        raise ValueError('Old FILE flag evidence changed')
    work = WS/'work/client-dependencies/crt-probe'
    work.mkdir(parents=True, exist_ok=True)
    fixture = work/'fixture.txt'
    fixture.write_bytes(b'x')
    cpp = f'''#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <windows.h>
static unsigned old_flags(void* f) {{ unsigned n; std::memcpy(&n, reinterpret_cast<unsigned char*>(f)+{offset}, sizeof(n)); return n; }}
template<class T> T load(HMODULE m, const char* name) {{
    FARPROC p=GetProcAddress(m,name); if(!p) std::exit(6);
    T f; static_assert(sizeof(f)==sizeof(p), "Win32 function pointer size");
    std::memcpy(&f,&p,sizeof(f)); return f;
}}
int main() {{
    FILE* f=std::fopen("fixture.txt","rb"); if(!f) return 2;
    if(std::fgetc(f)!='x' || std::fgetc(f)!=EOF) return 3;
    unsigned eof_flags=old_flags(f); int eof=!!std::feof(f);
    std::clearerr(f);
    if(std::fputc('z',f)!=EOF) return 4;
    unsigned error_flags=old_flags(f); int error=!!std::ferror(f);
    std::fclose(f);
    HMODULE m=LoadLibraryExW(L"msvcrt.dll",nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32); if(!m) return 5;
    auto open=load<void*(__cdecl*)(const char*,const char*)>(m,"fopen");
    auto get=load<int(__cdecl*)(void*)>(m,"fgetc");
    auto end=load<int(__cdecl*)(void*)>(m,"feof");
    auto close=load<int(__cdecl*)(void*)>(m,"fclose");
    void* old=open("fixture.txt","rb"); if(!old) return 7;
    if(get(old)!='x' || get(old)!=EOF) return 8;
    unsigned classic_flags=old_flags(old); int classic_eof=!!end(old); close(old);
    char module[MAX_PATH]; if(!GetModuleFileNameA(m,module,MAX_PATH)) return 9;
    for(char* p=module;*p;p++) if(*p=='\\\\') *p='/';
    auto dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(m);
    auto nt=reinterpret_cast<const IMAGE_NT_HEADERS*>(reinterpret_cast<const unsigned char*>(m)+dos->e_lfanew);
    std::printf("{{\\"public_file_size\\":%u,\\"eof_reported\\":%d,\\"flags_at_old_offset_after_eof\\":%u,\\"error_reported\\":%d,\\"flags_at_old_offset_after_error\\":%u,\\"classic_eof_reported\\":%d,\\"classic_flags_at_old_offset\\":%u,\\"classic_module\\":\\"%s\\",\\"classic_image_timestamp\\":%lu,\\"classic_image_size\\":%lu}}\\n", (unsigned)sizeof(FILE),eof,eof_flags,error,error_flags,classic_eof,classic_flags,module,nt->FileHeader.TimeDateStamp,nt->OptionalHeader.SizeOfImage);
    FreeLibrary(m);
    return 0;
}}
'''
    (work/'probe.cpp').write_text(cpp, encoding='ascii')
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dev = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    log = WS/'artifacts/vc6-stdio-build.txt'
    batch = work/'probe.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /EHsc /W4 /WX /D_CRT_SECURE_NO_WARNINGS probe.cpp /Feprobe.exe > "{log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    result = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    if result.returncode:
        raise RuntimeError(f'Own CRT probe build failed: {log}')
    data = (work/'probe.exe').read_bytes()
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    if struct.unpack_from('<H', data, pe+4)[0] != 0x14c:
        raise ValueError('Expected x86 CRT probe')
    observed = json.loads(subprocess.check_output([str(work/'probe.exe')], cwd=work))
    if fixture.read_bytes() != b'x':
        raise ValueError('Read-only fixture changed')
    observed['legacy_direct_eof'] = bool(observed['flags_at_old_offset_after_eof'] & mask)
    classic = Path(observed['classic_module'])
    # GetModuleFileName may report System32 inside a 32-bit process. Hash the actual
    # x86 disk image, not the x64 image seen there by this 64-bit audit interpreter.
    disk = classic.read_bytes()
    classic_pe = struct.unpack_from('<I', disk, 0x3c)[0]
    if struct.unpack_from('<H', disk, classic_pe+4)[0] != 0x14c:
        classic = classic.parent.parent/'SysWOW64'/classic.name
        disk = classic.read_bytes()
        classic_pe = struct.unpack_from('<I', disk, 0x3c)[0]
    if (struct.unpack_from('<H', disk, classic_pe+4)[0] != 0x14c or
        struct.unpack_from('<I', disk, classic_pe+8)[0] != observed['classic_image_timestamp'] or
        struct.unpack_from('<I', disk, classic_pe+24+56)[0] != observed['classic_image_size']):
        raise ValueError('Classic CRT disk image does not match loaded x86 image metadata')
    report = {'target': 'Modern MSVC x86 /MT vs observed VC6 Character FILE access',
        'source_object_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'function': '?LoadEffectFileList@EffectList@@QAEXPAD@Z', 'coff_function_offsets': ['0x31', '0x38'],
        'rva': None, 'legacy_offset': offset, 'legacy_eof_mask': mask, 'observed': observed,
        'eof_access_compatible': bool(observed['eof_reported']) == observed['legacy_direct_eof'],
        'classic_eof_access_compatible': bool(observed['classic_eof_reported']) == bool(observed['classic_flags_at_old_offset'] & mask),
        'classic_module_sha256': hashlib.sha256(classic.read_bytes()).hexdigest(),
        'classic_hash_file': str(classic),
        'probe_exe_sha256': hashlib.sha256(data).hexdigest(), 'input_game_exe_execution': False,
        'limit': 'One concrete FILE EOF access tested; no general CRT/STL compatibility inferred.'}
    (WS/'inventory/vc6-stdio-probe.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
