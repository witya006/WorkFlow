"""Restore selected455Resource.edf consumers in the ordinary client manager."""
def port_resource_catalog(raw,relative,section):
    if relative=='datatable/cresourcedatamgr.h':
        old=b'GetResourceList( BYTE pi_byType ){ &m_listResData[pi_byType]; }'
        if raw.count(old)!=1:raise ValueError('Resource list own accessor changed')
        return raw.replace(old,b'GetResourceList( BYTE pi_byType ){ return pi_byType<MAX_RES_DATA_LIST?&m_listResData[pi_byType]:NULL; }'),True
    if relative!='datatable/cresourcedatamgr.cpp':return raw,False
    includes=b'''#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_language.h"
#include "client455_resource_catalog.h"
#include <io.h>
#include <cstdio>
'''
    raw=includes+raw
    def edit(signature,change):
        nonlocal raw
        first,last=section(raw,signature,signature);body=raw[first:last]
        raw=raw[:first]+change(body)+raw[last:]
    def one(body,old,new):
        if body.count(old)!=1:raise ValueError('Resource catalog anchor changed:'+old.decode(errors='replace'))
        return body.replace(old,new)
    def bones(body):
        anchor=b'\t\tl_pBone = _GetBoneMgr()->AddBone( pi_byResFileType, l_pBuf );'
        added=b'''        if(RF455_MissingPlayerBoneFatal(l_pBuf,_access(l_pBuf,0)!=-1)){
            const char* format=RF455_GetNormalLanguagePack()->get(0x22c);
            char message[1024];std::snprintf(message,sizeof(message),format,l_pBuf);OutputDebugStringA(message);
            _GetMainApp()->RequestQuitProgram(0,NULL);return FALSE;
        }
'''
        return one(body,anchor,added+anchor)
    edit(b'CCharResData::LoadBoneDataList(',bones)
    def meshes(body):
        body=one(body,b'\tDWORD\t\tl_pTemp = 0;',b'\tDWORD\t\tl_pTemp = 0;\n\tBOOL validPlayerBones455=TRUE;')
        anchor=b'''\t\t\t\tl_pBone = _GetBoneMgr()->GetBone( RLI_PLAYER, m_listMesh[i].dwBoneID );
\t\t\t\tif( !l_pBone )
\t\t\t\t\tcontinue;'''.replace(b'\n',b'\r\n' if b'\r\n' in body else b'\n')
        added=b'''
                if(!RF455_PlayerBoneMatches(l_pBone->m_ID,l_pBone->m_MaxObj,
                    l_pBone->m_pMesh?l_pBone->m_pMesh[0].m_Name:NULL))validPlayerBones455=FALSE;'''
        body=one(body,anchor,anchor+added)
        anchor=b'\treturn TRUE;'
        added=b'''    if(!validPlayerBones455){
        OutputDebugStringA("Invalid Bone File.");
        if(_GetNetworkMgr()->GetAvatarGrade()>=2)
            _GUIMessageBox(NULL,"Invalid Bone File.",0xd0ffffff,0,4,0xffffffff,FALSE,FALSE,TRUE);
        _GetMainApp()->RequestQuitProgram(3000,const_cast<char*>(RF455_GetNormalLanguagePack()->get(0x7cf)));
    }
'''
        return one(body,anchor,added+anchor)
    edit(b'CCharResData::LoadMeshDataList(',meshes)
    def manager(body):
        anchor=b'\tfor( int i = 0; i < MAX_RES_DATA_LIST; ++i )'
        added=b'''    static_assert(sizeof(BONE_DATA)==260&&sizeof(MESH_DATA)==328&&sizeof(ANI_DATA)==244,"455 resource catalog rows");
    static_assert(sizeof(ANI_EXT_INFO)==84,"455 event metadata");
    RF455ResourceCatalogSummary catalog455;
    if(!RF455_CheckResourceCatalog(l_pSourceData->GetString(),l_pSourceData->GetStringLength(),catalog455))return FALSE;
'''
        return one(body,anchor,added+anchor)
    edit(b'CCharResDataMgr::LoadData(',manager)
    return raw,True
