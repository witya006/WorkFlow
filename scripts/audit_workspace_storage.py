"""Read-only storage inventory; distinguish NTFS hard links from new allocation.

No content hashing or deletion. Name/size groups are duplicate candidates only.
"""
import collections,ctypes,json,os,re,time
from pathlib import Path
from compare_client_binaries import WS

def audit():
    started=time.time();groups={};identities={};files=[];errors=[];reparse=[];stack=[WS]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    allocated=kernel.GetCompressedFileSizeW
    allocated.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)]
    allocated.restype=ctypes.c_ulong
    def disk_bytes(path,fallback):
        high=ctypes.c_ulong();ctypes.set_last_error(0)
        low=allocated('\\\\?\\'+str(path),ctypes.byref(high))
        if low==0xffffffff and ctypes.get_last_error():
            errors.append(dict(path=str(path),allocation_error=ctypes.get_last_error()));return fallback
        return (high.value<<32)|low
    while stack:
        folder=stack.pop()
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    try:
                        stat=entry.stat(follow_symlinks=False);path=Path(entry.path)
                        if getattr(stat,'st_file_attributes',0)&0x400:
                            reparse.append(path.relative_to(WS).as_posix());continue
                        if entry.is_dir(follow_symlinks=False):stack.append(path);continue
                        if not entry.is_file(follow_symlinks=False):continue
                        #Windows DirEntry.stat reports zero inode/link fields;
                        #os.stat opens the file for its actual identity.
                        stat=os.stat(path,follow_symlinks=False)
                        relative=path.relative_to(WS);parts=relative.parts;size=stat.st_size
                        identity=(stat.st_dev,stat.st_ino) if stat.st_ino else str(path)
                        if identity not in identities:
                            identities[identity]=dict(bytes=size,allocated_bytes=disk_bytes(path,size),links=stat.st_nlink,paths=[])
                        identities[identity]['paths'].append(relative.as_posix())
                        files.append((relative.as_posix(),size,identity))
                        keys=['total',parts[0],'ext:'+path.suffix.lower()]
                        if len(parts)>2:keys.append('/'.join(parts[:2]))
                        if len(parts)>3:keys.append('/'.join(parts[:3]))
                        if len(parts)>4 and parts[:2]==('work','m9'):
                            keys.append('m9-scenario:'+re.sub(r'[-_]?\d+$','',parts[3]))
                        for key in set(keys):
                            row=groups.setdefault(key,dict(logical_bytes=0,files=0,identities=set()))
                            row['logical_bytes']+=size;row['files']+=1;row['identities'].add(identity)
                    except OSError as error:errors.append(dict(path=entry.path,error=str(error)))
        except OSError as error:errors.append(dict(path=str(folder),error=str(error)))
    for row in groups.values():
        ids=row.pop('identities');row['unique_files']=len(ids)
        row['unique_content_bytes']=sum(identities[x]['bytes'] for x in ids)
        row['allocated_unique_bytes']=sum(identities[x]['allocated_bytes'] for x in ids)
    candidates=collections.defaultdict(list)
    for path,size,identity in files:
        if size>=1024*1024:candidates[(Path(path).name.lower(),size)].append((path,identity))
    duplicate_candidates=[]
    for (name,size),rows in candidates.items():
        unique={identity for _,identity in rows}
        if len(unique)>1:
            duplicate_candidates.append(dict(name=name,bytes_each=size,paths=len(rows),distinct_files=len(unique),candidate_extra_content_bytes=(len(unique)-1)*size,examples=[x[0] for x in rows[:5]],content_equality_verified=False))
    duplicate_candidates.sort(key=lambda x:x['candidate_extra_content_bytes'],reverse=True)
    report=dict(workspace=str(WS),time_local=time.strftime('%Y-%m-%d %H:%M:%S'),elapsed_seconds=round(time.time()-started,2),read_only_scan=True,content_hashed=False,files_deleted=False,
        groups=groups,largest_files=[dict(file=p,bytes=s,links=identities[i]['links'],allocated_bytes=identities[i]['allocated_bytes']) for p,s,i in sorted(files,key=lambda x:x[1],reverse=True)[:40]],
        duplicate_candidates=duplicate_candidates[:35],hardlinked_distinct_files=sum(x['links']>1 for x in identities.values()),hardlinked_paths=sum(len(x['paths']) for x in identities.values() if x['links']>1),
        skipped_reparse_points=reparse,errors=errors,allocation_note='GetCompressedFileSizeW once per file ID within this workspace;directory metadata excluded. Per-group unique allocations overlap across groups. Deleting one hard-link path need not free its allocation.')
    dest=WS/'inventory/workspace-storage-audit.json';dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def compact(key):return dict(group=key,**{k:round(v/2**30,2) if k.endswith('bytes') else v for k,v in groups[key].items()})
    top=sorted((x for x in groups if x!='total' and '/' not in x and ':' not in x),key=lambda x:groups[x]['logical_bytes'],reverse=True)
    major=sorted((x for x in groups if x.startswith('work/') and x.count('/')==1),key=lambda x:groups[x]['logical_bytes'],reverse=True)
    scenarios=sorted((x for x in groups if x.startswith('m9-scenario:')),key=lambda x:groups[x]['logical_bytes'],reverse=True)
    print(json.dumps(dict(unit='GiB',total=compact('total'),top=[compact(x) for x in top[:10]],work=[compact(x) for x in major[:12]],scenarios=[compact(x) for x in scenarios[:12]],errors=len(errors),report=str(dest)),ensure_ascii=False))

if __name__=='__main__':audit()
