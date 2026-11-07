"""Pin the actual effect archive owner and lazy entity/particle cache contracts."""
import hashlib
import json
from pathlib import Path

from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require, sha
from compare_client_binaries import WS, pe
from rpk455 import Rpk


def main():
    path = WS/'artifacts/client455-progress/effect105-reference.json'
    raw = json.loads(path.read_text())
    functions = [row['fn'] for row in raw['ranges']['result']]
    require(len(functions) == 14 and all(functions)
            and all(row['cursor']['done'] for row in raw['functions']+raw['assembly']), 'Complete coverage')
    require(sum(row['instruction_count'] for row in raw['assembly']) == 1315, 'Instruction coverage')
    pins = json.loads((WS/'config/client-target.json').read_text())
    references = []
    for folder, key in [('current', 'behavior_reference'), ('reference-backup', 'secondary_reference')]:
        binary = WS/f'work/client-reference/{folder}/RF_Online.bin'
        data = binary.read_bytes()
        require(sha(binary) == pins[key]['sha256'] and pe(data)['architecture'] == 'x86', 'Pinned input')
        ranges = [dict(rva=hex(int(fn['addr'], 16)-0x400000), bytes=int(fn['size'], 16),
                       sha256=hashlib.sha256(read_va(data, int(fn['addr'], 16), int(fn['size'], 16))).hexdigest())
                  for fn in functions]
        initializer = dict(rva='0x689590', bytes=41,
                           sha256=hashlib.sha256(read_va(data, 0xa89590, 41)).hexdigest())
        references.append(dict(sha256=sha(binary), architecture='x86', image_base='0x400000',
                               ranges=ranges, initializer=initializer))
    require(references[0]['ranges'] == references[1]['ranges']
            and references[0]['initializer'] == references[1]['initializer'], 'Reference ranges differ')
    client = Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    archive = client/'Effect/EffectEntity59.rpk'
    rpk = Rpk(archive.read_bytes())
    members = [dict(member=key.decode('ascii'), bytes=len(rpk.read(key)),
                    sha256=hashlib.sha256(rpk.read(key)).hexdigest())
               for key in sorted(rpk.files) if key.startswith(b'weapon_1\\nuclear\\c\\')]
    require(len(members) == 24 and sum(row['member'].endswith('.spt') for row in members) == 6,
            'Real aiming dependency closure')
    inputs = [dict(file=str(p), sha256=sha(p), original=str(p)) for p in
              [archive, client/'Effect/EffectEntityList.spt', client/'Effect/MagicSptList.spt']]
    report = dict(status='CONFIRMED_SELECTED',
                  scope='Client-owned effect RPK group bootstrap/release/selection and actual lazy entity/particle cache; full effect world runtime open',
                  script_sha256=sha(Path(__file__)), rpk_reader_sha256=sha(WS/'scripts/rpk455.py'),
                  raw_evidence=record(path), references=references, functions=14, instructions=1315,
                  inputs=inputs, actual_nuclear_members=members,
                  contracts=[
                      'Global effect group268 bytes is zero-initialized; static destructor releases indexes',
                      'LoadEffectEntityList opens loose table first, frees prior table, allocates 768x100, releases old group and scans .\\effect\\ before records',
                      'ReleaseEffectEntityList releases group indexes before empty-count return and before cached entities',
                      'StartMagicEffect matrix selects effect group before archive existence and parser; selection remains active',
                      'Lazy entity212 load and first particle1296 template load select effect group; cache hits do not reselect it',
                      'Particle clones share template recipe/entity pointers, copy1296, clear translation, InitParticle/START; caller owns clone shell',
                      'Particle NO_LOOP/END bits cleared only in finite branch then NO_LOOP set; always-live/emission-time branch preserves flags',
                      'SetResourceGroup returns the new group, not the previous one; callers must save GetResourceGroup explicitly'],
                  gaps=[
                      'Full effect FrameMove/matrices/entity/particle/render/axis/blur/parabola/multi dispatch and device reset remain unaccepted',
                      'Nuclear owner pending/position/cancel/tagged sound/messageC1A and hover truepredicate remain unported',
                      'Group enumeration order/first FindFirst omission/unsafe names/over255 archives/OOM are inherited bounded-contract gaps',
                      'Reinitializing a table with cached entities preserves target table-only-free leak; zero-record table/failed reads/global shutdown need broader acceptance',
                      'Six legacy R3T release warnings observed; GPU handles do release, but target warning parity is unverified. Global texture tables9728 bytes need separate process-owner teardown, performed explicitly by the lab',
                      'Other caches/resource groups/private ABI/EffectInfo tail semantics and all previous client-acceptance gaps remain mandatory'],
                  input_exe_executed=False, server_modified=False, M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS/'inventory/client455-effect-resources-reference.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(functions=14, instructions=1315, equal_ranges=14, aiming_members=len(members))))


if __name__ == '__main__':
    main()
