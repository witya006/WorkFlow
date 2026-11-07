"""Pin the status producer and nuclear aiming dependency on both 455 binaries."""
import hashlib,json
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe


def main():
    raw_path=WS/'artifacts/client455-progress/player-status102-reference.json'
    raw=json.loads(raw_path.read_text());functions=[row['fn'] for row in raw['ranges']['result']]
    require(len(functions)==17 and all(functions),'Canonical coverage')
    require(all(row['cursor']['done'] for row in raw['functions']+raw['assembly']),'Complete queries')
    require(sum(row['instruction_count'] for row in raw['assembly'])==2036,'Assembly count')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned input')
        ranges=[dict(rva=hex(int(fn['addr'],16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(fn['addr'],16),int(fn['size'],16))).hexdigest()) for fn in functions]
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges))
    require(references[0]['ranges']==references[1]['ranges'],'Selected reference ranges differ')
    exploration=WS/'artifacts/client455-progress/player-status102-exploration.json'
    require(any(row.get('code') and 'Not Nuclear Posion' in row['code'] for row in json.loads(exploration.read_text())['functions']),'Related diagnostic')
    for pin,folder in zip(references,['current','reference-backup']):
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        pin['diagnostic_range']=dict(rva='0x12a890',bytes=159,sha256=hashlib.sha256(read_va(data,0x52a890,159)).hexdigest())
    require(references[0]['diagnostic_range']==references[1]['diagnostic_range'],'Diagnostic range differs')
    report=dict(status='CONFIRMED_SELECTED',script_sha256=sha(Path(__file__)),raw_evidence=record(raw_path),exploration=record(exploration),functions=17,instructions=2036,references=references,
                scope='CPlayer status DWORD producer/getter and hover predicate; nuclear aiming owner still requires restoration',
                contracts=['CPlayer+0x452c is DWORD;getter41E290 andsetter44F090;52B810 compares onlylowBYTE to2/6/10, nullAvatar false',
                           '44DEE0 takes64bitflags:bit16→10;elsebit17 thenfirstsetbit33..40→2..9, no subtype preservesoldvalue;elsebit42→1;else0',
                           '44A750 hasno initialization of thisstatusDWORD;ownsource explicitlyrefuses unknown beforefirstproducer',
                           '52AD70 constructs STLcontainer andinlineaimingowner+12;52AAF0 initializes effecthandle/pending/position0',
                           '52AB50 zeroesposition,stopsaimingeffectandloopingsound277034 ifhandleexists,thenpending0;4FE020 emitslocalizedC1A',
                           '52AC40 starts effect1358041136 atworldcursor andsound277034;52AB90 updates itsposition;52A890 contains Nuclear Posion diagnostic'],
                gaps=['Status code human-readable rank names remain unconfirmed;not legacy attack mode',
                      'Other44DEE0status effects andfull64bit455network receivers notported;sourceSetServerStatusFlag retainslegacy sideeffects',
                      'Nuclear map/aiming producer/pending/effect/sound/message lifecycle notyetported;truepredicate remains explicitrefusal',
                      'Allprevious fullclient andGUI/board/handlers/bootstrap gaps remain mandatory'],
                input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-status-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=17,instructions=2036,equal_ranges=17)))


if __name__=='__main__':main()
