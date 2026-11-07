"""Pin the magic64 layout/parser/selector and archived aiming cue."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe
from rpk455 import Rpk


def main():
    path=WS/'artifacts/client455-progress/magic104-reference.json';raw=json.loads(path.read_text());functions=[row['fn'] for row in raw['ranges']['result']]
    require(len(functions)==19 and all(functions) and all(row['cursor']['done'] for row in raw['functions']+raw['assembly']),'Complete canonical coverage')
    require(sum(row['instruction_count'] for row in raw['assembly'])==2988,'Instruction coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';data=binary.read_bytes()
        require(sha(binary)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned input')
        ranges=[dict(rva=hex(int(fn['addr'],16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(fn['addr'],16),int(fn['size'],16))).hexdigest()) for fn in functions]
        init=dict(rva='0x689250',bytes=41,sha256=hashlib.sha256(read_va(data,0xa89250,41)).hexdigest())
        references.append(dict(sha256=sha(binary),architecture='x86',image_base='0x400000',ranges=ranges,array_initializer=init))
    require(references[0]['ranges']==references[1]['ranges'] and references[0]['array_initializer']==references[1]['array_initializer'],'Reference ranges differ')
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);archive=client/'Effect/EffectEntity59.rpk';rpk=Rpk(archive.read_bytes());member=b'weapon_1\\nuclear\\c\\nuclear_land_mag02.spt';content=rpk.read(member)
    require(hashlib.sha256(content).hexdigest()=='7459ef920bf277c92041c57d2dbe1876641d740bded34325bf8268de14b52b84' and len(re.findall(rb'(?m)^time\s',content))==6,'Actual six-track cue')
    output=WS/'work/client-reference/magic455/nuclear_land_mag02.spt';output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():require(output.read_bytes()==content,'Preserving existing extracted cue')
    else:output.write_bytes(content)
    inputs=[dict(file=str(p),sha256=sha(p),original=str(p)) for p in [archive,client/'Effect/EffectEntityList.spt',client/'Effect/MagicSptList.spt']]
    report=dict(status='CONFIRMED_SELECTED',scope='Client CProcessMagic64/layout3004,EffectInfo56/runtime456,parser/selector/control andordinary cache using realRPKcue;fullrender/nuclearowner remainopen',script_sha256=sha(Path(__file__)),rpk_reader_sha256=sha(WS/'scripts/rpk455.py'),raw_evidence=record(path),references=references,functions=19,instructions=2988,inputs=inputs,
                cue=dict(**record(output),member=member.decode('ascii'),archive=inputs[0],tracks=6,wire_entity_ids=[90061,90063,90062,90066,90065,90064]),
                contracts=['CProcessMagic3004:stateDWORD4/createBYTE8/axis9+10/loadedDWORD12/tracksDWORD16/speed20/position24/control24bytesat36/tracks64x46at60',
                           'Parser markerMagicTrack casesensitive;bodylowercases andstopsatend;resource-awareFILE retainsarchiveEOF butend preventssiblingparse',
                           'Time clears46bytes/defaultscale1/colorFFFFFFFF;ctrl0..2 use reserved61..63 andoverlappingRand1/Rand2 fields;billboard sets40and800',
                           'Axis/blur/parabola/multi fields restored;curve28byte linkednodes;integercast target comparison andtail insertion/overwrite;multiBYTE/unsigneddelayclamp1000',
                           'GetEntityIDs dividesframesby30,oldinclusive/newexclusive;emptyclearslowBYTEstate;unordered finalcomparison gives-2',
                           'EffectInfo56:commonprefix48,unknownDWORD48 zero,unknownDWORD52 FFFFFFFF;ctorzeroeswhole56 then6DWORDsFF andrangebytes0/FF',
                           'CMagicList456 containsEffectInfo56 at388;arrayinitializer256x456 callsctor7DBA80→5E35C0;StartMatrix copies56 andrefuseszerotracks',
                           'DestroyMagicTrack7D5870 isempty;automaticcurvefree isnotinvented;nativefixture explicitlyreleases itsgeneratedtestnodes'],
                gaps=['Fullworldeffect FrameMove/matrix/entity/particle/render/axis/blur/parabola/multi dispatch anddevice lifecycle notyetrestored/accepted',
                      'EffectInfo tail meanings/producers andallgame/queue consumers remainunknown/unmigrated;onlylayout/ctor/commonsetter partialwrites confirmed',
                      'Ordinary effectRPK group/bootstrap notrestored;lab setsactualgroup manually;target explicitlyselectsEffectgroup beforeexistence/start',
                      'Othermagiccache/policy/zero-input/failure/OOM/unsafe/concurrency/FP/RNG/legacyRand1-Rand2alias andcontrolnode lifetime domains remainopen',
                      'Own65thtrack explicitrefusal/RAIIclose differsfromtargetunchecked overflow;engineextensionlegacy16/EffectInfo48 definitions remainunlinked forselectedclientmethods,notfullprivateABI acceptance',
                      'Nuclear pending/cancel/messageC1A/hover truepredicate andallpreviousclientacceptance gaps remainmandatory'],
                input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-magic-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(functions=19,instructions=2988,equal_ranges=19,cue_bytes=len(content),cue_tracks=6)))


if __name__=='__main__':main()
