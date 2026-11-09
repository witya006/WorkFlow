"""Read physical pinned-client EBP20 entity options without altering game inputs."""
import json,struct
from collections import Counter
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS
from map455 import MapFile


def entities(data):
    container=MapFile(data,'ebp');lump=next(x for x in container.lumps if x.name=='EntityList');raw=data[lump.offset:lump.offset+lump.size]
    require(len(raw)%84==0,'Complete84-byte entity entries');rows=[]
    for i in range(len(raw)//84):
        particle,exists,name,fade_start,fade_end,flag,shader,a,b=struct.unpack_from('<BB62sffHH2f',raw,i*84)
        rows.append(dict(index=i,particle=particle,stored_exists=exists,name=name.split(b'\0')[0].decode('cp949',errors='backslashreplace'),flag=flag,shader=shader))
    return rows


def main():
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);maps=[]
    for file in sorted((client/'Map').rglob('*.ebp')):
        rows=entities(file.read_bytes());static=[r for r in rows if not r['particle']];selected=[r for r in static if r['flag']&0x40]
        maps.append(dict(file=str(file),relative=file.relative_to(client).as_posix(),sha256=sha(file),entries=len(rows),static_entities=len(static),particle_entries=len(rows)-len(static),static_lit=len(selected),static_lit_shader=sum(bool(r['shader']) for r in selected),
                         flag_shader_counts=[dict(flag=f,shader=s,count=n) for (f,s),n in sorted(Counter((r['flag'],r['shader']) for r in static).items())],lit_entries=selected))
    require(maps and any(x['static_lit'] for x in maps),'Real pinned maps contain static lighting producers')
    out=dict(scope='Physical Map/**/*.ebp files in configured455 installation;not archive-only maps or fullworld acceptance',script=record(Path(__file__)),maps=maps,
             totals=dict(files=len(maps),entries=sum(x['entries'] for x in maps),static_lit=sum(x['static_lit'] for x in maps),static_lit_shader=sum(x['static_lit_shader'] for x in maps)),input_exe_executed=False,server_modified=False)
    (WS/'inventory/client455-entity-flags-inputs.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(totals=out['totals'],selected=[dict(map=x['relative'],lit=x['static_lit'],shader=x['static_lit_shader']) for x in maps if x['static_lit']])))


if __name__=='__main__':main()
