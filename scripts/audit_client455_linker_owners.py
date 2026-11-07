"""Pin actual Linker clone/icon/registration contracts;stage real owner fixtures."""
import hashlib,json,shutil,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def main():
    evidence=WS/'artifacts/client455-progress/linker-owners096-reference.json';raw=json.loads(evidence.read_text());metadata=raw['ranges']['result'];require(len(metadata)==21 and len(raw['functions'])==21 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines'] for r in raw['functions']),'Incomplete reference');heads={r['fn']['addr']:r['fn'] for r in metadata};assembly=[];tails=[]
    for body in raw['assembly']:
        page=body['pages'][0];lines=page['asm']['lines'];a=int(body['addr'],16);end=a+int(heads[body['addr']]['size'],16);require(len(lines)==len({r['addr'] for r in lines})==page['total_instructions'] and page['cursor']['done'],'Incomplete assembly');assembly.append(dict(rva=hex(a-0x400000),instructions=len(lines)))
        tails.extend(dict(rva=hex(int(r['addr'],16)-0x400000),bytes=15) for r in lines if not a<=int(r['addr'],16)<end)
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Pin identity');ranges=[]
        for r in metadata:
            fn=r['fn'];a,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()))
        windows=[dict(**r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in tails]
        if refs:require(ranges==refs[0]['ranges'] and windows==refs[0]['external_assembly_windows'],'Pins differ')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=windows))
    root=WS/'work/client-reference/linker-owners455';root.mkdir(parents=True,exist_ok=True);inputs=[]
    for row in load('client455-icon-links-reference')['inputs']:
        check(row);dest=root/Path(row['file']).name;shutil.copyfile(WS/row['file'],dest);inputs.append(record(dest))
    samples=(root/'metadata-samples.bin').read_bytes();require(samples[:4]==b'MS94' and len(samples)==200,'Real samples extent');rows=list(struct.iter_unpack('<III',samples[8:]));require(all(r[0]==0 for r in rows),'Real physical samples')
    report=dict(status='CONFIRMED_SELECTED',scope='Ordinary CLinkBoard typed clone/registration/removal and actualwindow banked icon storage;fullCGUILinkWindow and livecallbacks stillopen',script_sha256=sha(Path(__file__)),references=refs,assembly=assembly,actual_instructions=sum(r['instructions'] for r in assembly),raw_evidence=[record(evidence)],inputs=inputs,fixtures=[],
        facts=['Target Add_ProcessExist returnsfalse;Add new detaches original icon reference,clones,packAdd failure destroys clone',
            'Window TakeIn has5banks/10slots,SetData then38*scale size,refnull;GetItem is direct slot address;TakeOut locally empties after unregister',
            'Actual Add binds copied icon to cloned wrapper and registers it;icon ownercontext1360 becomes2,physical grade refreshed',
            'SF/Animus source-board state callbacks are conditional on payload owner pointer;freshnull owner has no callback',
            'Target Remove unregisters current bankicon,clears matching50cooldown records,empties icon and deletes owned pack wrapper'],
        gaps=['Full CGUILinkWindow Init/layout/scale/controls/input notwired;banked sourceowned icons are realwindow members but not connected to ordinary legacy8slot drawing',
            'Live SF/Animus source-board callbacks,locked-item overlay and potion11 cooldown provider explicitly refuse;fresh null callback paths supported',
            'Full GUIItem.SetData/empty child-timer-shake-lock state and targetprivateABI remainopen;source copies selectedmetadata/grade only',
            'Target Remove cooldownrecord cleanup and source earlytyped cleanup before window destruction differ until fullcooldown/shutdown migration',
            'Untyped legacy borrowed path preserved until coordinated kind/caller migration;Macro/Vending/fullCItemBoard.Add/bootstrap/Tutorial/Login/game/M6F/M7/M9 mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-linker-owners-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(ranges=21,instructions=report['actual_instructions'],inputs=len(inputs),samples=rows)))
if __name__=='__main__':main()
