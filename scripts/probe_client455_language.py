"""Exercise production EDF/NDLanguage code with real packs and independent bytes."""
import hashlib,json,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ref=json.loads((WS/'inventory/client455-language-reference.json').read_text());root=WS/'work/client455-port/language';root.mkdir(parents=True,exist_ok=True);native=WS/'scripts/native';info=json.loads((WS/'inventory/msvc-verification.json').read_text());dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';exe=root/'language-probe.exe';batch=root/'build.cmd';log=root/'build.txt';source=[native/name for name in ['client455_language.cpp','client455_nation_paths.cpp','client455_font_settings.cpp','client455_character_rfs.cpp','test_client455_language.cpp']]
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /D_CRT_SECURE_NO_WARNINGS /I"{native}" '+' '.join('"'+str(p)+'"' for p in source)+f' user32.lib /Fe"{exe}" /link /MAP:"{root/"language-probe.map"}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    build=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW)
    if build.returncode:raise ValueError('Language build:'+str(log))
    fixture=WS/ref['fixture']
    if sha(fixture)!=ref['fixture_sha256']:raise ValueError('Changed real pack fixture')
    targets = {7, 8}
    for row in ref['files']:
        if row['nation'] not in targets:
            continue
        if sha(WS/row['copy'])!=row['sha256'] or sha(WS/row['decoded'])!=row['decoded_sha256']:raise ValueError('Changed real pack/plain fixture')
    codepages = [row for row in ref['references'][0]['codepages'] if row['nation'] in targets]
    countries=root/'codepages-target.txt';countries.write_text('\n'.join(f'{row["nation"]} {row["codepage"]}' for row in codepages)+'\n',encoding='ascii')
    focused = root/'files-target.tsv'
    pages = {str(row['codepage']) for row in codepages}
    focused.write_text('\n'.join(line for line in fixture.read_text().splitlines() if line.split('\t', 1)[0] in pages)+'\n',encoding='ascii')
    result=subprocess.run([str(exe),str(focused),str(countries)],cwd=root,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);output=root/'result.json';output.write_bytes(result.stdout)
    if result.returncode:raise ValueError('Language runtime:'+str(result.returncode)+':'+result.stderr.decode(errors='replace'))
    headers = [native/name for name in ('client455_language.h', 'client455_edf_input.h', 'client455_character_rfs.h')]
    report={'scope':'Actual production EDF/NDLanguage/index/DBCS/countryCRT routines on real files;not UI/font/full455acceptance','native':json.loads(result.stdout),'source_sha256':{p.name:sha(p) for p in source+headers},'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'reference_sha256':sha(WS/'inventory/client455-language-reference.json'),'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-language-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['native']))
if __name__=='__main__':main()
