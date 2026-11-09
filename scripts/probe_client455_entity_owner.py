"""Check automatic EBP flag transfer and actual BSP-selected fixed/LitGrass draws."""
import argparse,json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,require,sha
from compare_client_binaries import WS
from inventory_client455_entity_flags import entities
from probe_client455_nuclear_registry import main as scenario


def verify(run,native):
    input=next(x for x in native['inputs'] if x['file'].lower().endswith('/neutralb/neutralb.ebp'));data=(WS/input['file']).read_bytes();original=entities(data);rows=[json.loads(x) for x in (run/'entity-owner.jsonl').read_text().splitlines()];owners=[x for x in rows if x['kind']=='owner'];draws=[x for x in rows if x['kind']=='draw']
    require(len(owners)==len(original)*2 and len(draws)==4,'Two real map loads and4actual BSP draws');lit=[]
    for allowed in [0,1]:
        selected=[r for r in owners if r['allowed']==allowed];require(len(selected)==len(original),'Complete actual map owner table')
        for row,source in zip(selected,original):
            require(row['id']==source['index'] and row['particle']==source['particle'] and row['record_flag']==source['flag'] and row['shader']==(source['shader'] if allowed else 0),'Exact pinned EBP record and shader fallback')
            if not row['particle']:
                wanted=0x20|(2 if allowed and source['shader'] else 0)|(0x40 if row['exists'] and source['flag']&0x40 else 0)
                require(row['entity_flag']==wanted,'Only lighting bit copied after successful load')
        missing=[r for r in selected if not r['particle'] and not r['exists']]
        require(len(missing)==1 and original[missing[0]['id']]['name'].lower().endswith('\\trade_bel\\trade_bel.r3e'),'Only the known missing original entity')
        client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);require(not (client/'Map/Entity/e_neutrala/trade_bel/trade_bel.r3e').exists(),'Original missing resource not substituted')
        count=sum(not r['particle'] and r['exists'] and bool(r['entity_flag']&0x40) for r in selected);require(count==20,'20 actual loaded lit owners;one pinned original missing');lit.append(count)
    for index,row in enumerate(draws):
        shader=bool(row['allowed'] and row['source_shader']);require(row['entity_flag']&0x40 and row['draws']>0 and row['pixels']>100 and row['stride']==36 and row['color_op']==4,'Actual visible automatically lit entity submission')
        require(row['shader_bytes']==(300 if shader else 0),'Actual BSP route fixed or LitGrass')
        if shader:require((run/f'draw-shader-{index}.bin').read_bytes()==(run/'System/Shader/LitGrass1.vso').read_bytes(),'Pinned actual LitGrass shader')
    return dict(map='neutralB',entries_per_load=len(original),loads=2,lit_owners=lit,actual_BSP_draws=4,GPU_frames=4,explicit_entity_flag_assignment=False,shader_enabled_and_disabled=True,full_gameplay=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-existing',action='store_true');a=parser.parse_args();file=WS/'inventory/client455-entity-owner-native.json'
    r=load('client455-entity-owner-native') if a.verify_existing else scenario('client455_entity_owner_probe.cpp','entity-owner','client455-entity-owner-native','client455-sky-lighting-inputs',['System/Shader/grass1.vso','System/Shader/LitGrass1.vso'],expected_frames=4)
    require(not r['natural_exit'] and r['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current completed automatic owner probe');run=(WS/r['exe']['file']).parent
    r.update(status='PASS_SELECTED',scope='Actual CLand/CLevel EBP20 load transfers record flag40 and CBsp RenderOneEntityRender chooses fixed/LitGrass;full map/gameplay open',driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_lighting_consumers_probe.cpp'),world_source=record(WS/'scripts/native/client455_world_probe.cpp'),material_source=record(WS/'scripts/native/client455_sky_material_probe.cpp'),
             input_parser=record(WS/'scripts/inventory_client455_entity_flags.py'),trace=record(run/'entity-owner.jsonl'),verdict=verify(run,r))
    file.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
