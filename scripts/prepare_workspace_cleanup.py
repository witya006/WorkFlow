"""Prepare an explicit cleanup list; archive small unique evidence before deletion."""
import hashlib,json,os,zipfile,time
from pathlib import Path
from compare_client_binaries import WS

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def strings(v):
    if isinstance(v,str):yield v
    elif isinstance(v,dict):
        for k,x in v.items():yield k;yield from strings(x)
    elif isinstance(v,list):
        for x in v:yield from strings(x)

def main():
    root=WS.resolve();m9=root/'work/m9';graphics=root/'work/client-graphics-lab'
    keep_dirs={m9/'102a2443'} # Current verified early startup and live client runtime.
    keep_files={m9/p for p in ['7e1e3ab1/normal001/normal-consumers-probe.exe',
        '7e1e3ab1/normal001/result.json','7e1e3ab1/normal001/real.bbx',
        '0cf67ece/shop-window-001/probe-report.json',
        'def353f4/rvp-runtime-cora-001/rvp-runtime-probe.exe',
        'def353f4/rvp-runtime-cora-001/rvp-runtime-probe.map',
        'be020c26/world-movement-live-taiwan001/debug-events.jsonl',
        'f9d3bd6b/world-base-portal-live-taiwan001/debug-events.jsonl']}
    frame_refs=set()
    for manifest in (root/'inventory').glob('*.json'):
        data=json.loads(manifest.read_text(encoding='utf-8-sig'))
        for s in strings(data):
            s=s.replace('\\','/')
            if s.startswith(('work/m9/','work/client-graphics-lab/')) and '\n' not in s and len(s)<600:
                p=root/s
                if p.suffix.lower() in {'.png','.bmp','.bgra'}:frame_refs.add(p)
                if 'reference' in manifest.name and p.is_file():keep_files.add(p)
    # Preserve any literal runtime inputs in maintained helpers, rather than trusting directory age.
    for p in keep_files:
        if not p.is_file():raise RuntimeError('Required preservation input missing: '+str(p))
    keep_dirs={p.resolve() for p in keep_dirs};keep_files={p.resolve() for p in keep_files}
    def preserved(p):return p in keep_files or any(p==d or p.is_relative_to(d) for d in keep_dirs)
    targets=[]
    def select(folder):
        for p in folder.iterdir():
            if p.is_symlink() or p.is_junction():raise RuntimeError('Unexpected reparse point: '+str(p))
            if preserved(p):continue
            descendants=any(k.is_relative_to(p) for k in keep_files|keep_dirs)
            if p.is_dir() and descendants:select(p)
            else:targets.append(p)
    select(m9);select(graphics)
    store=root/'artifacts/workspace-cleanup-20261113';store.mkdir(exist_ok=True)
    archive=store/'unique-evidence.zip'
    if archive.exists():raise RuntimeError('Preserve previous archive; inspect before rerunning')
    index=[];seen=set();counts=dict(files=0,directories=0,logical_bytes=0,archived_paths=0,archived_unique_bytes=0)
    allowed={'.json','.jsonl','.asm','.md','.cpp','.h','.hpp','.inc','.py','.c','.disasm'}
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
        for target in targets:
            if not target.resolve().is_relative_to(root/'work'):raise RuntimeError('Outside work')
            paths=[target] if target.is_file() else target.rglob('*')
            for p in paths:
                if p.is_symlink() or p.is_junction():raise RuntimeError('Unexpected reparse point: '+str(p))
                if p.is_dir():counts['directories']+=1;continue
                stat=p.stat();counts['files']+=1;counts['logical_bytes']+=stat.st_size
                save=(p.suffix.lower() in allowed and stat.st_size<=16*1024**2) or p in frame_refs
                if not save:continue
                key=digest(p);member='objects/'+key
                if key not in seen:
                    z.write(p,member);seen.add(key);counts['archived_unique_bytes']+=stat.st_size
                index.append(dict(path=p.relative_to(root).as_posix(),sha256=key,bytes=stat.st_size,member=member))
                counts['archived_paths']+=1
            if counts['files'] and counts['files']%10000<100:print('Indexed',counts['files'],'obsolete paths',flush=True)
        z.writestr('index.json',json.dumps(index,separators=(',',':')))
    with zipfile.ZipFile(archive) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('Archive integrity failure: '+bad)
    pins=[]
    for p in sorted(keep_files):pins.append(dict(file=p.relative_to(root).as_posix(),sha256=digest(p)))
    link=json.loads((root/'inventory/client455-normal-link.json').read_text())
    for row in [link['executable'],link['map'],link['link_response']]+link['libraries']:
        p=root/row['file']
        if digest(p)!=row['sha256']:raise RuntimeError('Current build changed: '+str(p))
        pins.append(dict(file=row['file'],sha256=row['sha256']))
    plan=dict(workspace=str(root),created=time.strftime('%Y-%m-%d %H:%M:%S'),
        allowed_roots=[str(m9),str(graphics)],targets=[str(p) for p in targets],
        preserved_directories=[str(p) for p in keep_dirs],preserved_files=pins,
        archive=dict(file=archive.relative_to(root).as_posix(),sha256=digest(archive),bytes=archive.stat().st_size),
        counts=counts,executed=False)
    dest=root/'inventory/workspace-cleanup-plan-20261113.json'
    dest.write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps(dict(plan=str(dest),targets=len(targets),counts=counts,archive_bytes=archive.stat().st_size)))

if __name__=='__main__':main()
