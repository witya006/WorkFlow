"""Check defined effect-table reconstruction and keep undefined tails open."""
import hashlib,json,re
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from audit_client455_effect_tables import loaded

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-effect-tables-reference');native=load('client455-effect-tables-native');prep=load('client455-normal-preparation');build=load('client455-normal-build');link=load('client455-normal-link')
    for folder,record in zip(['current','reference-backup'],ref['references']):
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Changed reference')
        for row in record['functions']:
            if hashlib.sha256(read_va(raw,int(row['rva'],16)+0x400000,row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed reader/query body')
        initial=record['initial_pattern_table']
        if hashlib.sha256(loaded(raw,0x400000+int(initial['rva'],16),initial['bytes'])).hexdigest()!=initial['sha256']:raise ValueError('Changed initial table')
    if sha(WS/'scripts/audit_client455_effect_tables.py')!=ref['script_sha256'] or native['reference_sha256']!=sha(WS/'inventory/client455-effect-tables-reference.json'):raise ValueError('Stale table oracle')
    for row in ref['files']:
        if sha(WS/row['copy'])!=row['sha256']:raise ValueError('Changed reference data')
    if sha(WS/ref['golden'])!=ref['golden_sha256']:raise ValueError('Changed independent query oracle')
    for name in ['Character455.h','client455_normal_effect_tables.cpp','client455_effect_tables.cpp','client455_effect_tables.h']:
        if sha(WS/'scripts/native'/name)!=prep['record_inputs'][name]:raise ValueError('Changed table facade/core')
    if build['build_exit'] or build['objects']!=182 or native['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json') or link['normal_build_sha256']!=native['normal_build_sha256']:raise ValueError('Stale/incomplete normal build')
    if sha(WS/native['exe'])!=native['exe_sha256'] or pe((WS/native['exe']).read_bytes())['entry_rva']!=int(native['entry_rva'],16) or sha(WS/native['library'])!=native['library_sha256'] or sha(WS/native['source'])!=native['source_sha256'] or sha(WS/native['output'])!=native['output_sha256'] or sha(WS/native['map'])!=native['map_sha256']:raise ValueError('Changed own test evidence')
    for row in native['fixtures']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed actual run inputs')
    n=native['native']
    if n['status']!='PASS' or [n['pattern_records'],n['item_records'],n['real_selection_cases']]!=[ref['pattern_records'],ref['item_records'],ref['selection_cases']] or not n['synthetic_boundaries'] or not n['normal_facade'] or n['game_dlls_loaded'] or not n['undefined_queries_explicit']:raise ValueError('Incomplete known/unknown cases')
    mapping=(WS/native['map']).read_text(errors='replace')
    for symbol in ['IsHaveMeshEffect','LoadEffectPatternList@EffectPatternList','LoadItemListFile@ItemEffectList','g_PatternList','g_EffectItemList']:
        if not re.search(re.escape(symbol)+r'[^\r\n]+RFClient455Facade:client455_normal_effect_tables\.obj',mapping):raise ValueError('Missing actual normal provider:'+symbol)
        if any(symbol in row['symbol'] for row in link['unresolved']):raise ValueError('Table method/data still unresolved')
    if not link['link_exit'] or link['other_errors'] or not link['unresolved'] or link['legacy_character_linked'] or link['unresolved_forced']:raise ValueError('Inspect new full link state')
    names=['client455-effect-tables-reference','client455-effect-tables-native','client455-normal-preparation','client455-normal-build','client455-normal-link']
    report={'status':'PARTIAL','defined_pattern_item_loading_and_query':'PASS','normal_facade_providers':'PASS','undefined_original_stack_tail':'OPEN','unsupported_queries_reported':n['undefined_queries_explicit'],
        'pattern_records':n['pattern_records'],'item_records':n['item_records'],'full_normal_link':'OPEN','remaining_unresolved':link['unique_unresolved'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},
        'gaps':ref['gaps']+['Applying chosen effect to real material/particle/entity consumers remains open;full455acceptance unproven'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-effect-tables-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:defined real effect table/query cases PASS;undefined tails OPEN;full link'+str(link['unique_unresolved'])+'unresolved;M9OPEN')
if __name__=='__main__':main()
