"""Record source renderer ownership proof without claiming normal client parity."""
import hashlib,json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    ref=load('client455-renderer-owner-reference');build=load('client455-renderer-owner-build');gpu=load('client455-renderer-owner-gpu');client=load('client455-renderer-owner-client');link=load('client455-renderer-owner-link');mt=load('client-mt-variant');api=load('client455-normal-character-api');snapshots=load('client-first-build')
    if sha(WS/ref['golden'])!=ref['golden_sha256'] or sha(WS/'scripts/audit_client455_renderer_owner.py')!=ref['script_sha256']:raise ValueError('Changed owner oracle')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed owner source')
    for item in build['dependencies']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed owner dependency')
    for name,key in [('library','library_sha256'),('object','object_sha256')]:
        if sha(WS/build[name])!=build[key]:raise ValueError('Changed owner compiler artifact')
    for report in [gpu,client]:
        if report['build_report_sha256']!=sha(WS/'inventory/client455-renderer-owner-build.json') or report['reference_report_sha256']!=sha(WS/'inventory/client455-renderer-owner-reference.json') or sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed owner run')
        if report['native']['status']!='PASS' or report['native']['constructor_seeds']!=2 or report['native']['caps_cases']!=5 or report['native']['real_model_draws']!=92 or report['native']['heap_com_balance']:raise ValueError('Incomplete owner run')
        for frame in report['frames']:
            if sha(WS/frame['file'])!=frame['sha256'] or sha(WS/frame['preview'])!=frame['preview_sha256']:raise ValueError('Changed frame evidence')
    if gpu['native']!=client['native'] or [r['sha256'] for r in gpu['frames']]!=[r['sha256'] for r in client['frames']] or client['dmalloc_balance'] or client['exe_sha256']!=link['lab']['exe_sha256'] or client['link_report_sha256']!=sha(WS/'inventory/client455-renderer-owner-link.json'):raise ValueError('Component/fullclient difference')
    if len(link['lab']['functions'])!=5 or link['normal']['functions'] or sum(r['objects_verified'] for r in mt['targets'])!=293:raise ValueError('Wrong source selection')
    normal=WS/'work/client-build/build-character-diagnostic/Release/RF_Online.bin';previous=WS/snapshots['character455-frustum']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or sha(normal)!=api['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(previous.read_bytes())[0]:raise ValueError('Unexpected normal runtime change')
    names=['client455-renderer-owner-reference','client455-renderer-owner-build','client455-renderer-owner-gpu','client455-renderer-owner-client','client455-renderer-owner-link','client-mt-variant','client455-normal-character-api']
    report={'status':'PASS','scope':'Source455owner construction/device/sharedshader gate/destruction andtyped load-draw adapters;normal integration andM6/M6F/M7/M9 remainOPEN','normal':link['normal'],'lab':link['lab'],'native':client['native'],'normal_equal_previous_excluding_timestamps':True,'evidence_sha256':{n:sha(WS/f'inventory/{n}.json') for n in names},'gaps':['Normaltypedmodel-animation-ChInterface facade andD3D9engine device port;normal39SDKfunctions stillselected','Opaque methods/constructorunwind/exception-OOM anddevice-reset/state-block behavior','Shaderinit failure loggingcallback notfull original errorUI/logger lifecycle','ModernMTtrig provider notoriginal staticCRT bitparity;no originalgame frames compared'],'input_exe_executed':False,'server_modified':False}
    (WS/'inventory/client455-renderer-owner-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:sourceowner/realmodel/sharedshader/lifetime;normal unchanged excepttimestamps;M6/M9 OPEN')
if __name__=='__main__':main()
