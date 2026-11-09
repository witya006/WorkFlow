"""Compare actual engine/D3D fade to an independent rational x87 oracle."""
import argparse,json,struct
from fractions import Fraction as Q
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario


def number(bits):return Q(struct.unpack('<f',struct.pack('<I',bits))[0])
def bits(x):return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def power(e):return Q(2**e) if e>=0 else Q(1,2**-e)
def rounded(x,precision):
    """Round an exact rational to a binary significand, nearest/even."""
    if not x:return Q(0)
    sign=-1 if x<0 else 1;x=abs(x);e=x.numerator.bit_length()-x.denominator.bit_length()
    if x<power(e):e-=1
    step=power(e-precision+1);scaled=x/step;whole,remainder=divmod(scaled.numerator,scaled.denominator)
    if remainder*2>scaled.denominator or remainder*2==scaled.denominator and whole%2:whole+=1
    return sign*whole*step
def single(x):return rounded(x,24)
def ops(cw):
    require(cw&0xc00==0,'Test domain nearest/even');p={0:24,2:53,3:64}[(cw>>8)&3]
    return lambda x:rounded(x,p)
def interpolate(source,destination,alpha,r):return single(r(r(r(Q(destination)-source)*alpha)+source))
def color(source,destination,alpha,r):
    channels=[]
    for shift in (16,8,0):
        src=(source>>shift)&255;dst=(destination>>shift)&255
        channels.append(int(r(r(Q(dst-src)*alpha)+src))&0xffffffff)
    return (0xff000000|(channels[0]<<16)|(channels[1]<<8)|channels[2])&0xffffffff
def quad(destination,alpha,r):return ((destination&0xffffff)|((int(r(alpha*255))&0xffffffff)<<24))&0xffffffff


def verify(run):
    rows=[json.loads(x) for x in (run/'fade.jsonl').read_text().splitlines()];frames=[x for x in rows if x['kind']=='frame'];blends=[x for x in rows if x['kind']=='blend'];require(len(frames)==90 and len(blends)==27,'All90actual frames/27shared-helper cases');modes=set();inactive=active=legacy_differences=legacy_fog_differences=0
    for index,row in enumerate(frames):
        require(row['id']==index,'Sequential trace');r=ops(row['cw']);modes.add((row['cw']>>8)&3);c,t,start,total,alpha,started=row['before'];t,start,total,alpha=map(number,(t,start,total,alpha));now,loop=map(number,(row['now'],row['loop']));after=list(row['before'])
        if not alpha:
            inactive+=1;require(row['after']==after and row['result']==1 and not row['fog_writes'] and not row['draws'] and row['fog']==[0x12345678,0x3f800000,0x40000000],'Idle fade has no state/device side effects');continue
        active+=1;total=single(r(total-loop))
        if t:
            tick=single(r(r(r(now-start)+number(bits(.0001)))/abs(t)))
            if tick>1:alpha=Q(0 if t>0 else 1);t=Q(0)
            else:alpha=single(r(1-tick)) if t>0 else tick
        if not started and total<number(bits(.6)):
            started=1;t=number(bits(.600100040435791015625));start=now
        after=[c,bits(t),bits(start),bits(total),bits(alpha),started]
        require(row['after']==after,'Exact target state bits '+str(index));fog,near,far=row['fog_input'];wanted=[color(fog,c,alpha,r),bits(interpolate(number(near),6,alpha,r)),bits(interpolate(number(far),600,alpha,r))]
        require(row['fog']==wanted and row['fog_writes']==3 and row['result']==0,'Actual D3D fog state/order domain '+str(index));require(row['draws']==[quad(c,alpha,r)],'Actual submitted fade quad color '+str(index))
        for old,destination,actual in [(near,6,wanted[1]),(far,600,wanted[2])]:
            legacy=single(single(single(Q(destination)-number(old))*alpha)+number(old))
            legacy_fog_differences+=bits(legacy)!=actual
    for row in blends:
        r=ops(row['cw']);alpha=number(row['alpha']);require(row['color']==color(row['source'],row['destination'],alpha,r) and row['quad']==quad(row['destination'],alpha,r),'Shared helper matches target x87 including out-of-range finite alpha');legacy_differences+=row['quad']!=row['legacy_quad']
    require(modes=={0,2,3} and active and inactive and legacy_fog_differences,'Three precision modes/idle transitions and demonstrated legacy SSE fog difference')
    names=['fade-base.bgra','fade-middle.bgra','fade-covered.bgra','fade-return.bgra','fade-done.bgra'];images={n:(run/n).read_bytes() for n in names};require(all(len(x)==640*480*4 for x in images.values()),'Five complete GPU frames');base=images[names[0]];require(images[names[-1]]==base,'Finished fade restores actual sky exactly');require(all(images[n]!=base for n in names[1:4]),'Visible fade controls differ');covered=images['fade-covered.bgra'];require(covered==covered[:4]*(640*480) and covered[:3]==bytes.fromhex('204060'),'Full fade covers real sky with exact requested RGB')
    return dict(frame_cases=len(frames),shared_helper_cases=len(blends),precision_bits=[24,53,64],rounding='nearest/even;integer conversion truncates and restoresCW',active_frames=active,idle_frames=inactive,exact_state_and_device_bits=True,actual_quad_colors=True,legacy_SSE_alpha_differences=legacy_differences,legacy_SSE_fog_differences=legacy_fog_differences,GPU_frames=5,finished_sky_byte_equal=True,covered_RGB=list(covered[:3]),full_sky_renderer=False,all_FP_inputs=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-existing',action='store_true');a=p.parse_args();r=json.loads((WS/'inventory/client455-sky-fade-native.json').read_text()) if a.verify_existing else scenario('client455_sky_fade_probe.cpp','sky-fade','client455-sky-fade-native','client455-world-bellato-native');require(not r['natural_exit'] and r['native']['status']=='PASS','Completed own fade run');r.update(status='PASS_SELECTED',scope='Actual engine sky fade state/timing and D3D fog/quad under3x87 precision modes;five real Bellato sky fade frames;full atmosphere/sky materials remain open',driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_world_probe.cpp'),trace=record((WS/r['exe']['file']).parent/'fade.jsonl'),verdict=verify((WS/r['exe']['file']).parent));(WS/'inventory/client455-sky-fade-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
