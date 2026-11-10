"""Verify inventory/pack/equipment view bodies against both pinned455 PEs."""
import json
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from audit_client455_sprites import sprite
from checkpoint_client455_rvp_effects import sha,require

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    raw=WS/'artifacts/client455-progress/inventory165-reference/inventory.json';proof=verify_regions(raw)
    require(proof['full_functions']==52 and proof['full_instructions']==4375,'Complete inventory view/dependency capture')
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);skins=[]
    for folder in ['Common','ko-kr','zh-tw','ru-ru']:
        path=client/'SpriteImage'/folder/'inventory.spr';shape=sprite(path.read_bytes())
        require(shape['frames'][2]==11,'Actual stock pack-mode frame domain')
        skins.append(dict(file=str(path),sha256=sha(path),**shape))
    files=['scripts/client455_inventory_port.py','scripts/native/client455_inventory.inc','scripts/prepare_client455_normal.py']
    report=dict(status='STATIC_CONFIRMED_PARTIAL',raw=record(raw),**proof,script=record(Path(__file__)),helpers=[record(WS/'scripts/client455_reference_regions.py'),record(WS/'scripts/audit_client455_sprites.py')],sources=[record(WS/name) for name in files],stock_inventory_skins=skins,
        facts=['Inventory uses actual sprite6/action0/frame0 and common1/action4/frame0 header with left help andright close','Three race currency names come from positional language10/11/12;title47B,gold3C7 andpack title483','Ordinary inventory view14children plus borrowed equipment;five pack controls at41pixel intervals','Equipment view has16slots,firsteight64pixel andremaining32pixel domains;natural empty images and extra positions14/15 verified','Each pack has20icons in5x4 grid,83children and34pixel overlays;empty equipment alpha70 andwindow alphaD8','Trade/unused masks use actual sprite44 SocketState.spr action0/2,not ItemLock.spr,andretain initialized geometry when state changes','Money setters retain signed64bits,use existing measured x87 money kernel andalign to wider label','Pack mode controls9/10/11;stock action2 hasonly11frames0..10,original setter stores inactive pressed descriptor11 while resolving current state;no replacementframe is fabricated','Opened pack icons depend on encoded race/2;single mode affects free packs as well as docked packs','Public equipment GetItem returns null for empty owners aswell as out-of-range slots;fixture inspects actual owned array separately','Help1204 uses window ID;ordinary pack-open uses existing windowID/packed LPARAM message route'],
        gaps=['Full item payload receivers/actions,trade/use/equip/pick/tooltip andown selected/ready cue behavior are not accepted by an empty-window probe','UI has16equipment slots while legacy ordinary board capacity is15;full455 equipment mapping/producer contract remains open,do not fabricate the sixteenth backend entry','Target equipment Init writes basefield+332=1;meaning/consumers are not yet reconstructed in own CGUIItemWindow','Target pack has additional arrays/state notrepresented by old source fields;full owner/lifecycle/settings equivalence remains open','Full root Open recursive child-visibility predicate is represented by admitted equipment leaf visibility only;arbitrary nested equipment-window domains unaccepted','Inventory settings serialization677DD0 andhighlight item/serial3325/3326 producers are notyet ported','Legacy RemovePack andremaining interaction methods retain oldsource adapters;they are not claimed equivalent455 behavior','Missing stock pressed frame11 is retained;full pressed rendering/error behavior remains unaccepted;Common inventory hasonly14equipment skin frames whilelocalized admitted sets have15','Full mouse mask/hittest andunbound-pointer/invalid-index/nonfinite/OOM/reentry/destruction domains remain open','Native three-race checks use Taiwan language/assets;not acceptance of all eleven locales','All previous455UI/actor/Animus/network/world/gameplay and M9 requirements remain mandatory'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    report['facts'].append('Both pack/equipment vtables inherit65EA40:ordinary window draw returns1 even hidden;old special Draw overrides removed and actual owned child list renders selection/ready objects')
    (WS/'inventory/client455-inventory-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(functions=52,instructions=4375,status=report['status'])))
if __name__=='__main__':main()
