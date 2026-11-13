"""Stage immutable lab assets once, without linking to original installations.

Configs, executables and generated fixtures remain independent writable files.
The content-addressed pool adopts verified owned copies before copying originals.
"""
import hashlib,json,os,shutil
from pathlib import Path
from compare_client_binaries import WS

ASSET_SUFFIXES={'.rpk','.rfs','.r3t','.bsp','.spr','.edf','.dds','.sho','.shr','.vsh','.vso','.ttf','.wav','.mp3','.avi','.wmv','.jpg','.png','.m3d','.asi','.dll','.spt','.r3o','.r3s','.bn','.bbx','.ani','.msh'}
#NTFS permits1024links perfile. Identical small assets can reach that limit
#across many paths,evenwithin one run. Keep bounded owned pool replicas.
MAX_POOL_LINKS=900
_owned=None
_stats=dict(assets=0,linked_bytes=0,new_pool_bytes=0,adopted_bytes=0,private_files=0)

def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda:handle.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def _inside_work(path):
    return Path(path).resolve().is_relative_to((WS/'work').resolve())

def _owned_copies():
    global _owned
    if _owned is not None:return _owned
    _owned={}
    def visit(value):
        if isinstance(value,dict):
            if all(isinstance(value.get(k),str) for k in ['original','file','sha256']):
                source=Path(value['original']);candidate=WS/value['file']
                if source.is_absolute() and candidate.absolute().is_relative_to((WS/'work').absolute()):
                    _owned.setdefault((os.path.normcase(os.path.abspath(source)),value['sha256']),[]).append(candidate)
            for item in value.values():visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    for manifest in (WS/'inventory').glob('*.json'):
        try:visit(json.loads(manifest.read_text(encoding='utf-8-sig')))
        except (OSError,ValueError):continue
    return _owned

def stage_asset(source,target,expected=None,owned_immutable=None,pool_root=None):
    source,target=Path(source),Path(target)
    if not _inside_work(target):raise ValueError('Asset staging destination must remain under work/')
    target.parent.mkdir(parents=True,exist_ok=True)
    digest=sha(source)
    if expected and digest!=expected:raise ValueError('Changed pinned staging input: '+str(source))
    if target.exists():
        if sha(target)!=digest:raise ValueError('Preserve changed existing staged input: '+str(target))
        return
    if source.suffix.lower() not in ASSET_SUFFIXES:
        shutil.copyfile(source,target);_stats['private_files']+=1;return
    pool_root=Path(pool_root) if pool_root else WS/'work/shared-runtime-inputs'
    if not _inside_work(pool_root):raise ValueError('Asset pool must remain under work/')
    primary=pool_root/digest[:2]/digest;pooled=primary;replica=0
    while pooled.exists() and pooled.stat().st_nlink>=MAX_POOL_LINKS:
        if sha(pooled)!=digest:raise ValueError('Shared asset was modified: '+str(pooled))
        replica+=1;pooled=primary.with_name(primary.name+'.'+str(replica))
    if not pooled.exists():
        pooled.parent.mkdir(parents=True,exist_ok=True)
        candidates=[Path(owned_immutable)] if owned_immutable is not None else []
        #Pinned private reference inputs can be adopted directly. Generated
        #build outputs and arbitrary run files are never inferred immutable.
        if _inside_work(source) and source.is_relative_to(WS/'work/client-reference'):candidates.append(source)
        candidates+=_owned_copies().get((os.path.normcase(os.path.abspath(source)),digest),[])
        adopted=None
        for candidate in dict.fromkeys(candidates):
            if not _inside_work(candidate):raise ValueError('Cannot adopt a hard link to an original installation')
            if candidate.is_file() and candidate.stat().st_nlink<MAX_POOL_LINKS-1 and sha(candidate)==digest:
                if not _inside_work(source) and os.path.samefile(candidate,source):continue
                adopted=candidate;break
        if adopted is not None:
            os.link(adopted,pooled);_stats['adopted_bytes']+=source.stat().st_size
        else:
            #The first source copy is owned independently;never link originals.
            temporary=pooled.with_name(pooled.name+'.new-'+str(os.getpid()))
            with source.open('rb') as src,temporary.open('xb') as dst:shutil.copyfileobj(src,dst)
            if sha(temporary)!=digest:raise ValueError('Input changed during pool creation')
            os.replace(temporary,pooled);_stats['new_pool_bytes']+=source.stat().st_size
    if sha(pooled)!=digest:raise ValueError('Shared asset was modified: '+str(pooled))
    os.link(pooled,target) #Fail clearly if sharing is unavailable;no silent bulk copy.
    _stats['assets']+=1;_stats['linked_bytes']+=source.stat().st_size

def staging_stats():return dict(_stats)
