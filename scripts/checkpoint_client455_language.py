"""Prove scoped language restoration and real own WinMain use,keeping M9 open."""
import hashlib,json,re,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry
from audit_client455_language import decode,encode_with_envelope,records

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-language-reference');cpu=load('client455-language-native');prep=load('client455-normal-preparation');link=load('client455-normal-link');validate_normal_link(link);validated_entry()
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_language.py') or cpu['reference_sha256']!=sha(WS/'inventory/client455-language-reference.json'):raise ValueError('Stale language oracle')
    for folder,record in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=record['sha256']:raise ValueError('Changed455pin')
        for row in record['functions']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed language function')
        for row in record['codepages']:
            if struct.unpack('<I',read_va(raw,0x400000+int(row['vtable_rva'],16)+row['slot_offset'],4))[0]!=0x400000+int(row['method_rva'],16):raise ValueError('Changed virtual codepage method')
    total=0
    for row in ref['files']:
        raw=(WS/row['copy']).read_bytes();plain=(WS/row['decoded']).read_bytes();items,end=records(plain)
        if sha(WS/row['copy'])!=row['sha256'] or sha(WS/row['decoded'])!=row['decoded_sha256'] or decode(raw)!=plain or encode_with_envelope(raw,plain)!=raw or len(items)!=row['records'] or end!=row['consumed']:raise ValueError('Changed real language fixture/roundtrip')
        total+=len(items)
    for name,digest in cpu['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed tested source')
    for name in ['client455_language.cpp','client455_language.h','client455_nation_paths.cpp']:
        if sha(WS/'scripts/native'/name)!=prep['record_inputs'][name]:raise ValueError('Normal client used different language source')
    if sha(WS/cpu['exe'])!=cpu['exe_sha256'] or sha(WS/cpu['output'])!=cpu['output_sha256']:raise ValueError('Changed native evidence')
    n=cpu['native']
    if n['status']!='PASS' or n['files']!=len(ref['files']) or n['records']!=total or n['country_locales']!=11 or not all(n[k] for k in ['byte_roundtrip','indexed_lookup','dbcs_boundaries','release','bounded_malformed_inputs']):raise ValueError('Incomplete language cases')
    executions=[]
    for name,nation,cp in [('client455-create-startup-native','ko-kr',949),('client455-startup-russia-native','ru-ru',1251)]:
        run=load(name);events_path=WS/run['events']['file'];helper=run['debugger'];expected=next(row for row in ref['files'] if row['folder']==nation)
        if run['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or run['own_entry_sha256']!=sha(WS/'inventory/client455-own-entry.json') or sha(events_path)!=run['events']['sha256'] or sha(WS/run['staged_executable'])!=link['executable']['sha256']:raise ValueError('Stale actual language startup')
        if sha(WS/helper['file'])!=helper['sha256'] or sha(WS/helper['source'])!=helper['source_sha256'] or run['debugger_exit']:raise ValueError('Changed/failed owned debugger')
        events=[json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines()];summary=next(e for e in events if e['kind']=='summary');logs=[e['value'] for e in events if e['kind']=='debug_string'];inputs=run.get('lab_inputs',run.get('inputs',[]))
        for row in inputs:
            if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed own lab input')
        pack=next(row for row in inputs if row['file'].replace('\\','/').endswith(f'/DataTable/{nation}/NDLanguage.edf'))
        if pack['sha256']!=expected['sha256'] or f'.\\DataTable\\{nation}' not in logs or f'RF455 NDLanguage:{cp}:{expected["records"]}' not in logs:raise ValueError('Actual production language init absent')
        if summary!=run['summary'] or not summary['main_reached'] or not summary['exit_observed'] or not(summary.get('after_sound_reached') or summary.get('final_checkpoint_reached')) or next(e['code'] for e in events if e['kind']=='exit')!='0xe0434200' or any(e['kind'].endswith('_error') or e['kind'] in ['timeout','termination_timeout'] or e['kind']=='exception' and not e['first_chance'] for e in events):raise ValueError('Actual startup incomplete')
        executions.append({'folder':nation,'codepage':cp,'records':expected['records'],'source':name,'status':'PASS'})
    mapping=(WS/link['map']['file']).read_text()
    if not re.search(r'\?RF455_InitializeLanguageData@@[^\r\n]+RFClient455Facade:client455_language\.obj',mapping):raise ValueError('Wrong normal language provider')
    names=['client455-language-reference','client455-language-native','client455-create-startup-native','client455-startup-russia-native','client455-normal-link']
    report={'status':'PARTIAL','edf_decode_real_byte_roundtrip':'PASS','real_ndlanguage_indexed_lookup':'PASS','stored_codepage_dbcs_boundaries':'PASS','country_crt_codepage_agreement':'PASS','actual_own_winmain_languages':executions,'files':len(ref['files']),'records':total,'executable':link['executable'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':ref['gaps']+['Normal text/UI consumers and actual font/text rendering not yet ported/accepted','Modern CRT agreement on this machine is not complete old-CRT behavior certification','Own bounded parser/reload resource cleanup does not certify unsafe original domains','Existing whole client feature registry and M6/M6F/M7/M9 acceptance remain open'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-language-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:realEDF/NDLanguage/DBCS/CRT and exact own Korean/Russian startup PASS;font/UI/full455 OPEN')
if __name__=='__main__':main()
