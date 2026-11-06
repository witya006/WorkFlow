"""Pin BSP world ownership/destruction and independent real-map record counts."""
import hashlib,json
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe
from map455 import MapFile
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    path=WS/'artifacts/client455-progress/world074.json';body=json.loads(path.read_text());target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        source=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=source.read_bytes()
        if sha(source)!=target[key]['sha256'] or pe(raw)['architecture']!='x86':raise ValueError('Changed455pin')
        ranges=[]
        for row in body['ranges']['result']:
            if row['error']:raise ValueError('Missing world function')
            addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16);ranges.append({'rva':hex(addr-0x400000),'bytes':size,'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        table={'rva':'0x738494','bytes':48,'sha256':hashlib.sha256(read_va(raw,0xb38494,48)).hexdigest()}
        if pins and (ranges!=pins[0]['ranges'] or table!=pins[0]['vtable_prefix']):raise ValueError('455world functions differ betweenpins')
        pins.append({'sha256':sha(source),'architecture':'x86','image_base':'0x400000','ranges':ranges,'vtable_prefix':table})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);maps=[]
    for race in ['bellato','cora','accretia']:
        files={};parsed={}
        for extension in ['bsp','ebp','cam']:
            source=client/f'Map/{race}/{race}.{extension}';raw=source.read_bytes();files[extension]={'file':str(source),'sha256':sha(source),'bytes':len(raw)}
            if extension!='cam':parsed[extension]=MapFile(raw,extension)
        bsp,ebp=parsed['bsp'],parsed['ebp'];sizes={l.name:l.size for l in bsp.lumps};ext={l.name:l.size for l in ebp.lumps}
        expected={'vertices':sizes['BVertex']//3+sizes['WVertex']//6+sizes['FVertex']//12,'faces':sizes['Face']//6,'leaves':sizes['Leaf']//25,'materials':sizes['ReadMatGroup']//42,'map_entities':ext['MapEntitiesList']//38}
        maps.append({'race':race,'files':files,'expected':expected,'BSP_sequential_mismatches':bsp.sequential_offset_mismatches(),'EBP_sequential_mismatches':ebp.sequential_offset_mismatches()})
    result={'scope':'Source BSP owner/destructor with realTutorial worlds;fullILevel/Empty/INS/Tutorial/game acceptance remainsopen','references':pins,'raw_evidence':{'file':path.relative_to(WS).as_posix(),'sha256':sha(path),'assemblies':list(assembly_rows(body['assemblies']))},'maps':maps,'script_sha256':sha(Path(__file__)),
        'facts':['7C8600 deletes oldlevel before suffix selection;ins->CLevelIns,otherwise CLevel;updatesgloballevel and cameraBSP afterload','8EA120 destructor calls8E7730 release before deletingSky/BSP;Release clearslevel loadedflag/resources/RTMovie/dummies','ExistingBSP39/EBP20source loads realMapEntity archives/materials/textures/geometry without geometryloader rewrite','Source newBSP owner and destructor restore boundedload/reload/release path;legacytypedCLevel is retained temporarily'],
        'gaps':['FullILevel virtualinterface,Empty initialowner andCLevelIns notported;ins explicitlyreturnsFALSE','Indexedmapextras/effects/time/radar/lifecycle andallworldinterfaces notaccepted','GPUframes are ownsource/camera0 views,not pixelcomparison against455;sky/opaque shown,fullalpha/effects/shaders/lighting/audio/lifecycle unresolved','FullTutorialclass/cameraintro/Avatar/QBI/localhandlers/fourstage/auth/gameplay/IME/M6F/M9 open','Allocatorbalance coversDmalloc only,not proof ofallCOM/GPU/heap lifetimes;invalidstrings/OOM/failure domains unaccepted'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-world-reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'ranges':len(ranges),'assemblies':len(result['raw_evidence']['assemblies']),'maps':[m['expected'] for m in maps]}))
if __name__=='__main__':main()
