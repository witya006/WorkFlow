"""Bound workspace growth before a supported build or asset staging operation."""
import json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
_checked=False

def inspect():
    policy=json.loads((ROOT/'config/workspace-policy.json').read_text())
    files=logical=run_files=0;stack=[ROOT];errors=[]
    runs=ROOT/'work/m9'
    while stack:
        folder=stack.pop()
        try:
            with os.scandir(folder) as entries:
                for e in entries:
                    if e.is_symlink() or e.is_junction():continue
                    if e.is_dir(follow_symlinks=False):stack.append(Path(e.path));continue
                    if e.is_file(follow_symlinks=False):
                        files+=1;logical+=e.stat(follow_symlinks=False).st_size
                        if Path(e.path).is_relative_to(runs):run_files+=1
        except OSError as error:errors.append(str(error))
    hashes=sum(p.is_dir() for p in runs.iterdir()) if runs.exists() else 0
    exceeded=[]
    for label,value,limit in [('workspace bytes',logical,policy['workspace_logical_gib_limit']*2**30),
        ('workspace files',files,policy['workspace_file_limit']),('run files',run_files,policy['run_file_limit']),
        ('run hash directories',hashes,policy['run_hash_directory_limit'])]:
        if value>limit:exceeded.append(dict(metric=label,value=value,limit=limit))
    return dict(files=files,logical_bytes=logical,run_files=run_files,run_hash_directories=hashes,
                errors=errors,exceeded=exceeded,passed=not errors and not exceeded)

def require_budget():
    global _checked
    if _checked:return
    result=inspect()
    if not result['passed']:raise RuntimeError('Workspace budget: stop and review retention: '+json.dumps(result))
    _checked=True

if __name__=='__main__':
    result=inspect();print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
