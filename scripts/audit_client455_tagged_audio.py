"""Confirm the native tagged audio dependency before wiring nuclear aiming."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe


def main():
    path=WS/'artifacts/client455-progress/tagged-audio103-reference.json';raw=json.loads(path.read_text())
    functions=[row['fn'] for row in raw['ranges']['result']]
    require(len(functions)==18 and all(functions) and all(row['cursor']['done'] for row in raw['assembly']+raw['functions']),'Complete canonical coverage')
    require(sum(row['instruction_count'] for row in raw['assembly'])==1520,'Instruction coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        original=WS/f'work/client-reference/{folder}/RF_Online.bin';data=original.read_bytes()
        require(sha(original)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pin identity')
        ranges=[dict(rva=hex(int(fn['addr'],16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(fn['addr'],16),int(fn['size'],16))).hexdigest()) for fn in functions]
        references.append(dict(sha256=sha(original),architecture='x86',image_base='0x400000',ranges=ranges))
    require(references[0]['ranges']==references[1]['ranges'],'Selected ranges differ')
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);table=client/'Snd/WaveList.spt';cue=client/'Snd/Character/Newclear/Radar_00.wav'
    require(re.search(rb'^277034\s+\.\\Snd\\Character\\Newclear\\Radar_00.wav',table.read_bytes(),re.M),'Radar mapping')
    inputs=[dict(file=str(p),sha256=sha(p),original=str(p)) for p in [table,cue,client/'MSS32.DLL',client/'Snd/msssoft.m3d',client/'Snd/msseax.m3d',client/'Snd/mssmp3.asi']]
    rows=re.findall(rb'^\s*(?:[1-9][0-9]*|0[xX][0-9a-fA-F]+)\s+\.\\[^\s]+',table.read_bytes(),re.M)
    require(len(rows)==7932,'Stock simple relative-path row count')
    report=dict(status='CONFIRMED_SELECTED',scope='Tagged3D-wave dependency of nuclear aiming;actual service in ordinary CMainApp;fullnuclear/effects/audio remainopen',script_sha256=sha(Path(__file__)),raw_evidence=record(path),functions=18,instructions=1520,references=references,inputs=inputs,stock_simple_relative_path_rows=len(rows),
                contracts=['64cache entries/280byte records,30samplehandles+30tags;HitCache1new/0victim/-1old promotesbeforetag suppression',
                           'Nonzero tag checksall30 tags evennew/reusedrecord;stale tag can suppress beforeoldpayload release',
                           'Stop8BD590 endsfirstmatching tagged3Dsample;doesnotcleartag/handle;Collect8BCD60 releasesdone samples andmayretainstaletags',
                           'Collect empty accumulator isinitializedonce acrosswholecache walk,notperecord',
                           'Play8BD080 zeroesactive beforeload/reuse;newloadsets150/40distances;oldreuse allocatesnewhandle withoutthatsetter;loop1 setsactualMilesloop0',
                           'Coordinates relative tolistener:position0.1*X/0/0.1*Z;normalizes3Dreversevector thenflattensorientationY;zero-vector producesNaNs',
                           'Provider preference CreativeLabsEAX2 thenMilesFast2D;listenerorigin/forwardZ/upY/room0;redistdirectory mustbepreparedbeforestartup',
                           'WAV type1 reused;ADPCMtype2/ASItype13 decoded;cache usesactual PCM andMiles sample handles'],
                gaps=['Nuclear aiming owner/cancel/messageC1A/effect pipeline notyetwired;oldmagic16tracks/record layout differsfrom45564tracks',
                      'Legacy untagged2D consumers remain separate;sharedfullaudio owner/startup timing/errorMessageBoxes andallAPIs parity notaccepted',
                      'ADPCM/ASI branches,roomchanges/listenerupdates/fullcachefailure/unsafe/OOM/concurrency/numericx87 parity andallshutdownquirks notfullyvalidated',
                      'Full manifest tokenizer/comments/invalidnames andalias parity notaccepted;7969 runtime registrations include tokensoutside7932 simple relative-path rows',
                      'Owned Close releasesall3Dhandles;target ReleaseWaveList clearskindinsidechannel loop,soexactbugcompatibility remainsopen',
                      'Allprevious GUI/board/handlers/bootstrap/client acceptance gaps remain mandatory'],
                input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-tagged-audio-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=18,instructions=1520,equal_ranges=18,radar_bytes=cue.stat().st_size)))


if __name__=='__main__':main()
