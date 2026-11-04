"""Check selected pose library source providers and actual lab call sites."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
from probe_client455_pose import inputs

APIS=['_RF455_'+n for n in ['SelectPoseKeys','ApplyPoseScale','ApplyPoseRotation','ApplyPoseTranslation','UpdateCharacterPose']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';proof,_,_,_,_,_=inputs();summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_POSE')!='ON' or sha(Path(summary['build_settings']['RF_CLIENT_455_POSE_LIBRARY']))!=proof['library_sha256']:raise ValueError('Pose-enabled source build required')
    obj=WS/proof['object']
    if sha(obj)!=proof['object_sha256'] or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Wrong pose source object/MT')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))};selected=[]
    for symbol in APIS:
        if symbol not in symbols:
            if args.lab:raise ValueError('Missing pose API:'+symbol)
            continue
        va,line=symbols[symbol];provider='RFClient455Pose:pose.obj'
        if provider not in line:raise ValueError('Wrong pose provider:'+symbol)
        selected.append({'symbol':symbol,'rva':hex(va-0x400000),'provider':provider})
    if args.lab:
        info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dump=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');table=subprocess.check_output([str(dump),'/symbols',str(build/'RF_Online.dir/Release/test_client455_pose.obj')]).decode('utf-8',errors='replace')
        for symbol in APIS:
            if not any('UNDEF' in line and re.search(r'\|\s*'+re.escape(symbol)+r'(?:\s+\(.*\))?\s*$',line) for line in table.splitlines()):raise ValueError('Actual pose caller missing:'+symbol)
    exe=build/'Release/RF_Online.bin';path=WS/'inventory/client455-pose-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':selected,'library_sha256':proof['library_sha256'],'scope':'Selected pose phases;normal consumers/secondary motion/profiling/animateddraw remain open'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} source pose;{len(selected)}C APIs linked')
if __name__=='__main__':main()
