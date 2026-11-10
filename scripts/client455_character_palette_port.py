"""Restore the actual ordinary Character20x30palette cache and13dummy slots."""
def port_character_palette(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Character palette anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='character/character/ccharacter.h':
        once(b'#define MAX_PARTS_RESULT\t10',b'#define MAX_PARTS_RESULT\t20\r\n#define RF455_PART_PALETTES 30')
        once(b'#define MAX_EFFECT_DUMMYS\t( 10 )',b'#define MAX_EFFECT_DUMMYS\t( 13 )')
        once(b'm_pMatResMat[MAX_PARTS_RESULT][2]',b'm_pMatResMat[MAX_PARTS_RESULT][RF455_PART_PALETTES]')
        return raw,True
    if relative=='character/character/ccharacter.cpp':
        once(b'm_pMatResMat[i][0]\t= NULL;',b'for(int p=0;p<RF455_PART_PALETTES;++p)m_pMatResMat[i][p]=NULL;')
        once(b'm_pMatResMat[i][1]\t= NULL;',b'')
        once(b'SAFE_DELETE_ARRAY( m_pMatResMat[i][0] );',b'for(int p=0;p<RF455_PART_PALETTES;++p){SAFE_DELETE_ARRAY(m_pMatResMat[i][p]);}')
        once(b'SAFE_DELETE_ARRAY( m_pMatResMat[i][1] );',b'')
        return raw,True
    if relative=='character/character/ccharacter_etc.cpp':
        first,last=section(raw,b'CCharacter::SetVertexBlending(',b'CCharacter::SetVertexBlending(')
        body=b'''CCharacter::SetVertexBlending(int part,CMesh* model,BOOL save){
    assert(part<MAX_PARTS_RESULT);
    if(!model)return FALSE;
    if(save&&m_dwMaxResult[part]<model->m_MaxObj){
        for(int p=0;p<RF455_PART_PALETTES;++p){
            delete[] m_pMatResMat[part][p];
            m_pMatResMat[part][p]=new D3DXMATRIX[model->m_MaxObj];
        }
        m_dwMaxResult[part]=model->m_MaxObj;
    }
    for(DWORD node=0;node<model->m_MaxObj;++node){
        if(!save&&node>=m_dwMaxResult[part])return FALSE;
        ObjectMesh& mesh=model->m_pMesh[node];
        if(!mesh.m_BlendNum){
            if(save)memcpy(&m_pMatResMat[part][0][node],&mesh.m_MatResult,sizeof(D3DXMATRIX));
            else memcpy(&mesh.m_MatResult,&m_pMatResMat[part][0][node],sizeof(D3DXMATRIX));
        }else{
            for(DWORD p=0;p<mesh.m_BlendNum;++p){
                if(save)memcpy(&m_pMatResMat[part][p][node],&mesh.m_pMatBlend[p],sizeof(D3DXMATRIX));
                else memcpy(&mesh.m_pMatBlend[p],&m_pMatResMat[part][p][node],sizeof(D3DXMATRIX));
            }
        }
    }
    return TRUE;
}'''
        return raw[:first]+body+raw[last:],True
    return raw,False
