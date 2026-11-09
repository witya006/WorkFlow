"""Verify actual file identities, original isolation and mutable-file boundaries."""
import json,os,uuid
from compare_client_binaries import WS
from client455_asset_staging import stage_asset,sha,staging_stats

def main():
    root=WS/'work/storage-staging-validation'/uuid.uuid4().hex[:8];root.mkdir(parents=True)
    #A disposable artifact stands in for a read-only reference installation.
    original=WS/'artifacts/storage-staging-validation'/root.name/'source.spr'
    original.parent.mkdir(parents=True);original.write_bytes(b'RF455 immutable fixture\0')
    digest=sha(original);pool=root/'pool';a,b=root/'a/source.spr',root/'b/source.spr'
    stage_asset(original,a,digest,pool_root=pool);stage_asset(original,b,digest,pool_root=pool)
    assert os.path.samefile(a,b) and not os.path.samefile(original,a)
    assert os.stat(original).st_nlink==1 and sha(original)==digest
    owner=root/'owned/source.spr';owner.parent.mkdir();owner.write_bytes(b'RF455 adopted immutable fixture\0')
    original.write_bytes(owner.read_bytes());other=root/'c/source.spr';stage_asset(original,other,sha(original),owned_immutable=owner,pool_root=pool)
    assert os.path.samefile(owner,other) and not os.path.samefile(original,other)
    ini=original.with_suffix('.ini');ini.write_text('[Sound]\nSound=FALSE\n');left,right=root/'a/config.ini',root/'b/config.ini'
    stage_asset(ini,left,pool_root=pool);stage_asset(ini,right,pool_root=pool);left.write_text('changed private config')
    assert not os.path.samefile(left,right) and right.read_bytes()==ini.read_bytes()
    failures=0
    for target,expected,owner_arg in [(root/'bad/hash.spr','0'*64,None),(WS/'artifacts/storage-staging-validation/outside.spr',None,None),(root/'bad/original.spr',None,original)]:
        try:stage_asset(original,target,expected,owned_immutable=owner_arg,pool_root=root/'other-pool')
        except ValueError:failures+=1
        else:raise AssertionError('Unsafe or changed input accepted')
        assert not target.exists()
    existing=root/'existing.spr';existing.write_bytes(b'preserve changed data')
    try:stage_asset(original,existing,pool_root=pool)
    except ValueError:failures+=1
    else:raise AssertionError('Changed staged file overwritten')
    assert existing.read_bytes()==b'preserve changed data'
    tampered=pool/digest[:2]/digest;tampered.write_bytes(b'changed shared fixture')
    #Restore the independent original to the first pool's expected content.
    original.write_bytes(b'RF455 immutable fixture\0')
    try:stage_asset(original,root/'bad/tampered.spr',digest,pool_root=pool)
    except ValueError:failures+=1
    else:raise AssertionError('Modified shared pool accepted')
    assert sha(original)==digest
    result=dict(status='PASS',run=root.relative_to(WS).as_posix(),shared_file_identity=True,originals_independent=True,adopted_owned_copy=True,mutable_configs_independent=True,rejected_cases=failures,stats=staging_stats(),staging_script_sha256=sha(WS/'scripts/client455_asset_staging.py'),verifier_sha256=sha(__file__),files_deleted=False)
    (WS/'inventory/client455-asset-staging-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
