"""Validate retained real-frame evidence for the bounded lobby graphics package."""
import hashlib,json
from pathlib import Path
from PIL import Image
from workspace_guard import inspect

ROOT=Path(__file__).resolve().parents[1]

def main():
    reports={mode:json.loads((ROOT/f'artifacts/lobby-visual/{mode}.json').read_text()) for mode in ['classic','enhanced']}
    before,after=reports.values()
    assert before['sha256']==after['sha256'],'A/B builds differ'
    camera_delta=max(abs(a-b) for a,b in zip(before['renderer']['camera_view'],after['renderer']['camera_view']))
    assert camera_delta<.001,'A/B camera changed beyond float-time interpolation tolerance'
    for mode,row in reports.items():
        path=ROOT/row['frame']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['frame_sha256'],'Frame changed'
        with Image.open(path) as image:assert image.size==(1920,1080),'Full HD required'
        assert row['exit_code']==0,'Preview did not close normally'
        assert not row['server_modified'] and not row['real_authentication']
    actual=after['renderer']
    assert not before['renderer']['post_enabled']
    assert actual['post_available'] and actual['post_enabled'] and actual['post_frames']>0
    assert actual['passes']==11 and actual['msaa']==4
    assert actual['post_error']==0 and actual['material_errors']==0 and actual['material_binds']>0
    assert actual['sky_ready'] and actual['sky_draws']>0 and actual['sky_errors']==0 and actual['sky_error']==0
    assert actual['sky_volume_bytes']==1048576
    assert after['settings_check']['passed'] and after['settings_check']['completed_phases']==6
    report={
        'status':'PASS','date':'2026-11-14','phase':'M6','package':'VIS-01 first lobby renderer',
        'scope':'Own client, real D3D9 lobby, offline launcher fixture; not live login/world acceptance',
        'architecture':'x86','image_base':'0x400000','entry_rva':after['entry_rva'],
        'executable_sha256':after['sha256'],'resolution':[1920,1080],
        'camera_seconds':actual['camera_seconds'],'same_camera':True,'camera_max_matrix_difference':camera_delta,'camera_tolerance':.001,'original_assets':True,
        'modes':{name:{key:value for key,value in row.items() if key in ['frame','frame_sha256','renderer','memory','exit_code','settings_check']} for name,row in reports.items()},
        'limits':['CPU submission and frame interval are not GPU timestamps or benchmark FPS',
                  'VRAM is a render-target allocation estimate, not total driver residency',
                  'No new shadow maps, depth AO, PBR texture set or rebuilt environment art',
                  'No claim of Expedition 33 parity or the ceiling of Direct3D9',
                  'UI test uses real callbacks and F10 window message; no full live-server regression',
                  'Resource release/recreation checked; full device-loss/reset not covered']}
    report['workspace_after']=inspect()
    assert report['workspace_after']['passed'],'Workspace storage policy failed'
    destination=ROOT/'inventory/client455-lobby-visual.json'
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','binary':after['sha256'],'resolution':[1920,1080],
                      'post_passes':actual['passes'],'material_binds':actual['material_binds'],
                      'settings_phases':6,'receipt':str(destination)}))

if __name__=='__main__':main()
