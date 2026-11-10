"""Resolve bounded own-PE stack candidates;never label system exception RVAs as own code."""
import argparse,json,struct
from compare_client_binaries import WS,pe
from client455_ui_checkpoint import own_symbols
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import sha,require

def inspect(link,live):
    path=WS/link['executable']['file'];require(sha(path)==link['executable']['sha256']==live['executable']['sha256'],'Exact own PE')
    raw=path.read_bytes();symbols=own_symbols(link);image=pe(raw)
    def resolve(address):
        starts=[(a,n) for a,n in symbols if a<=address]
        if not starts:return dict(rva=hex(address),symbol=None)
        start,name=max(starts);result=dict(rva=hex(address),symbol=name,offset=hex(address-start),is_code=any(s['name']=='.text' and s['rva']<=address<s['rva']+s['raw_size'] for s in image['sections']))
        try:result['previous_eight_bytes']=read_va(raw,image['image_base']+address-8,8).hex()
        except StopIteration:result['previous_eight_bytes']=None
        return result
    fatal=[e for e in live['exceptions'] if not e.get('first_chance')];require(len(fatal)==1,'One observed fatal exception')
    events=[json.loads(line) for line in (WS/live['events']['file']).read_text().splitlines()]
    context=next(e for e in events if e['kind']=='fatal_context')
    own='RF_Online.bin' in fatal[0]['module']
    return dict(normal_executable=link['executable'],exception=fatal[0],fault_rva_is_own=own,own_fault=resolve(int(fatal[0]['rva'],16)) if own else None,candidates=[dict(resolve(int(c['rva'],16)),stack_offset=c['stack_offset']) for c in context['own_stack_rva_candidates'][:20]],stack_is_candidate_scan_not_unwind=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args()
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());live=json.loads((WS/'inventory/client455-character-selection-live-taiwan-native.json').read_text());result=inspect(link,live)
    if args.output:
        path=(WS/args.output).resolve();require(path.is_relative_to((WS/'artifacts').resolve()),'Private diagnostic output');path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
