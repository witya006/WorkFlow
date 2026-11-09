"""Actual loaded Bellato sky with translation/near/ortho and unloaded controls."""
import argparse,json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario


def verify(run):
    names=['sky-base.bgra','sky-translated.bgra','sky-near3000.bgra','sky-ortho.bgra','sky-unloaded.bgra'];frames={name:(run/name).read_bytes() for name in names};require(all(len(x)==640*480*4 for x in frames.values()),'Complete sky frames');base=frames[names[0]]
    require(all(frames[name]==base for name in names[1:4]),'Loaded sky pixels unaffected by translation/world near/ortho restore');clear=frames[names[4]];pixel=clear[:4];require(pixel[:3]==bytes.fromhex('302010') and clear==pixel*(640*480),'Unloaded uniform clear RGB exact;unused backbuffer byte recorded');changed=sum(a!=b for a,b in zip(base,clear));require(changed>100,'Visible actual sky');return dict(frames=5,actual_Bellato_sky=True,loaded_controls_byte_equal=True,unloaded_control_exact=True,clear_pixel=list(pixel),unused_backbuffer_byte=int(pixel[3]),changed_bytes=changed,full_sky_equivalence=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-existing',action='store_true');args=p.parse_args();r=json.loads((WS/'inventory/client455-sky-world-native.json').read_text()) if args.verify_existing else scenario('client455_sky_world_probe.cpp','sky-world','client455-sky-world-native','client455-world-bellato-native');require(r['natural_exit']==0 and r['native']['status']=='PASS','Completed actual native run');r.update(scope='Actual loaded Bellato CLevel sky and three matched controls plus unloaded sky;fullsky/fade/renderer not accepted',status='PASS_SELECTED',driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_world_probe.cpp'),verdict=verify((WS/r['exe']['file']).parent));(WS/'inventory/client455-sky-world-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
