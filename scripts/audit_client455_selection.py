"""Pin selection packet/input bodies without claiming full stage/avatar handoff."""
import json
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from checkpoint_client455_rvp_effects import sha


def record(path):
    path=Path(path);return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))


def main():
    raw=WS/'artifacts/client455-progress/selection158-reference/session.json';proof=verify_regions(raw)
    assert proof['full_functions']==6 and proof['full_instructions']==592
    default_raw=WS/'artifacts/client455-progress/selection158-reference/defaults.json';defaults=verify_regions(default_raw)
    assert defaults['full_functions']==3 and defaults['full_instructions']==97
    report=dict(status='STATIC_CONFIRMED_PARTIAL',scope='1/14 selection request,1/15 reply22 andrecorded input callbacks;full callback/transition not ported',
        raw=record(raw),**proof,default_copy_proof=dict(raw=record(default_raw),**defaults),script=record(__file__),
        sources=[record(WS/path) for path in ['scripts/native/client455_selection.h','scripts/native/client455_selection.inc','scripts/client455_selection_port.py','scripts/prepare_client455_normal.py','scripts/native/client455_equipment_object.h','scripts/native/client455_equipment_object.cpp']],
        facts=['56B920 sends group1/op14/oneBYTE slot;success marks pending',
               '56B9D0 copies22bytes:WORDresult0,DWORDserial2,int64dalant6,int64gold14',
               'Only lowBYTE result isstored;serial andmoney writesevenonerror beforeReceiveResponse',
               'Main avatar skipTutorial==1 chooses main;other DWORDvalues choose selected dummy',
               '562F50 actualcase15 calls56B9D0',
               '7AA5A0 routes WM_KEYDOWN13 through same7BB470 as mouse callback7AA360',
               '7BB470 requires Loginstate12/existing character;calls equipment board1virtual176,thenbranches onselected skipTutorial',
               'SkipTutorial0 has a distinct fullAvatar/gear handoff;nonzero sendsselection andsetsstate15',
               '419F50 accepts defaultpart<6 andnonnullsource,then46C130 clears,copies base640 andretains payload',
               'Ordinary post-selection Avatar transfer now uses6typed default wrappers/11typed worn slots andcopies skipTutorial'],
        gaps=['Full7BB470 equipment-board selection sideeffect/tutorial branch andcomplete53D0F0 state/camera/UI handoff remainunported',
              'Retained self-copy/unsafe rawvptr/private-padding/all pointeralias lifecycle domains remainunaccepted',
              'Old0.7Login state/factory/UI/camera policies remainpartial',
              'Bounded22-byte decoder rejects unsafe short frames;target uncheckedcopy isnot accepted equivalence',
              'Fullworld/control/gameplay/FP/clone/remaining clientacceptance open'],
        prior_runtime=record(WS/'artifacts/client455-progress/before158/manifest.json'),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-selection-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('STATIC_CONFIRMED_PARTIAL:6+3functions/689instructions,both455pins;selection/transition gaps explicit')


if __name__=='__main__':main()
