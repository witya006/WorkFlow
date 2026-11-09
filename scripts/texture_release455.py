"""Selected target8F2D10/8E08F0 semantics as a separate trace oracle."""
from copy import deepcopy


def release(state,ids):
    rows={x['index']:deepcopy(x) for x in state['rows']}
    live={x['id']:deepcopy(x) for x in state['textures']}
    warnings=[];freed=[];shared=[]
    for ident in ids:
        if ident==-1 or ident not in live:continue
        i=1
        while i<state['records'] and rows[i]['start']<=ident:i+=1
        row=rows[i-1]
        if row['same']:
            row['same']=(row['same']-1)&0xffffffff;shared.append(ident);continue
        if not row['flags']&0x8000:warnings.append(ident)
        row['name']='';del live[ident];freed.append(ident)
    return dict(rows=[rows[i] for i in sorted(rows)],textures=live,warnings=warnings,freed=freed,shared=shared)
