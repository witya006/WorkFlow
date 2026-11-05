"""Stage signed Microsoft D3DX headers locally;do not install package runtime DLLs."""
import hashlib,json,os,subprocess,urllib.request,zipfile
from pathlib import Path
from compare_client_binaries import WS

VERSION='9.29.952.8'
URL='https://www.nuget.org/api/v2/package/Microsoft.DXSDK.D3DX/'+VERSION
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'local/dxsdk-d3dx'/VERSION;root.mkdir(parents=True,exist_ok=True);package=root/'Microsoft.DXSDK.D3DX.nupkg';manifest=WS/'inventory/d3dx9-headers.json'
    if not package.exists():
        pending=root/'download.tmp'
        with urllib.request.urlopen(URL,timeout=45) as response,pending.open('wb') as out:
            while chunk:=response.read(1024*1024):out.write(chunk)
        pending.rename(package)
    previous=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else None
    if previous and sha(package)!=previous['package_sha256']:raise ValueError('Changed pinned package;preserving existing headers')
    art=WS/'artifacts/d3dx9-headers';art.mkdir(parents=True,exist_ok=True);env=os.environ.copy();env.update(DOTNET_CLI_HOME=str(WS/'local/dotnet-home'),DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1',DOTNET_NOLOGO='1')
    run=subprocess.run(['dotnet','nuget','verify','--all',str(package)],cwd=WS,env=env,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);(art/'signature.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise ValueError('NuGet signature verification failed:'+str(art/'signature.txt'))
    records=[]
    with zipfile.ZipFile(package) as archive:
        if '.signature.p7s' not in archive.namelist():raise ValueError('Unsigned package')
        for entry in archive.infolist():
            name=entry.filename.replace('\\','/');parts=Path(name).parts
            if '..' in parts or name.startswith('/') or ':' in name:raise ValueError('Unsafe package path')
            header='/include/' in name.lower() and name.lower().endswith(('.h','.inl'))
            notice=name.lower().endswith(('license.txt','notice.txt','.nuspec'))
            if not header and not notice:continue
            destination=root/'extracted'/name
            if not destination.resolve().is_relative_to(root.resolve()):raise ValueError('Extraction escaped package root')
            if entry.file_size>8*1024*1024:raise ValueError('Unexpected header size')
            data=archive.read(entry)
            if destination.exists() and destination.read_bytes()!=data:raise ValueError('Preserving modified SDK file')
            destination.parent.mkdir(parents=True,exist_ok=True)
            if not destination.exists():destination.write_bytes(data)
            records.append({'file':destination.relative_to(WS).as_posix(),'bytes':len(data),'sha256':sha(destination)})
    found=list((root/'extracted').rglob('d3dx9.h'))
    if len(found)!=1:raise ValueError('D3DX9 header not uniquely located')
    report={'package':'Microsoft.DXSDK.D3DX','version':VERSION,'source':URL,'source_page':'https://www.nuget.org/packages/Microsoft.DXSDK.D3DX/'+VERSION,'package_file':package.relative_to(WS).as_posix(),'package_sha256':sha(package),'signature_exit':run.returncode,'signature_log':(art/'signature.txt').relative_to(WS).as_posix(),'signature_log_sha256':sha(art/'signature.txt'),'include':found[0].parent.relative_to(WS).as_posix(),'files':records,'runtime_policy':'Package_43DLLs not extracted/installed;455 continues pinned x86d3dx9_36;imports checked separately','executed_package_targets':False}
    manifest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:signed Microsoft D3DX headers staged:{len(records)}files;include='+report['include'])
if __name__=='__main__':main()
