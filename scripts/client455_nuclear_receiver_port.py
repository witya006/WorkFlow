"""Register actual group60 processing and transfer its owner into MainGame."""


def port_nuclear_receiver(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Nuclear receiver anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='mainapp.h':
        once(b'\tRF455NuclearContainer m_nuclear455;',b'')
        once(b'return m_nuclear455.Aiming();',b'return RF455_NuclearContainer().Aiming();')
        once(b'return m_nuclear455;',b'return RF455_NuclearContainer();')
        return raw,True
    if relative=='mainapp.cpp':
        once(b'\tm_nuclear455.ClearAll();\r\n\tm_nuclear455.Aiming().Clear();',b'')
        return raw,True
    if relative=='gameprogress/cgp_maingame.h':
        raw=b'#include "client455_nuclear_registry.h"\r\n'+raw
        once(b'\tBOOL\tm_bIsCompleteDataDownload;',b'\tstd::unique_ptr<RF455NuclearContainer> m_nuclear455;\r\n\tBOOL\tm_bIsCompleteDataDownload;')
        once(b'\tCGP_MainGame();',b'\tCGP_MainGame();\r\n\tRF455NuclearContainer& Nuclear455(){if(!m_nuclear455)throw std::logic_error("455 nuclear stage owner unavailable");return *m_nuclear455;}\r\n\tvoid ReleaseNuclear455();\r\n\tCGUIMiniMapWindow& MiniMap455(){return m_uiMinimapWindow;}')
        return raw,True
    if relative=='gameprogress/cgp_maingame.cpp':
        begin,end=section(raw,b'CGP_MainGame::Init(',b'CGP_MainGame::Init(');body=raw[begin:end];raw=raw[:end-1]+b'\r\n\tm_nuclear455.reset(new RF455NuclearContainer);\r\n\tRF455_BindNuclearContainer(m_nuclear455.get());\r\n'+raw[end-1:]
        once(b'\tdelete\tm_pNextActionMgr;',b'\tdelete\tm_pNextActionMgr;\r\n\tReleaseNuclear455();')
        begin,end=section(raw,b'CGP_MainGame::~CGP_MainGame(',b'CGP_MainGame::~CGP_MainGame(')
        raw=raw[:end-1]+b'\r\n\t// Own uncreated-stage cleanup is explicit;target early-Destroy leak domain remains unaccepted.\r\n\tReleaseNuclear455();\r\n'+raw[end-1:]
        return raw,True
    if relative=='character/player/cplayer.h':
        raw=b'#include "client455_player_use.h"\r\n'+raw
        once(b'\tBYTE\t\t\tm_byRace;',b'\tRF455PlayerUse m_use455;\r\n\tBYTE\t\t\tm_byRace;')
        once(b'\tinline\tvoid\t\tRemoveUsingItem( void )',b'\tvoid ClearUsingItem455(){m_use455.clear();}\r\n\tconst RF455PlayerUse& UsingItem455()const{return m_use455;}\r\n\tinline\tvoid\t\tRemoveUsingItem( void )')
        return raw,True
    if relative=='network/cnetworkmgr.h':
        once(b'\tNMP_EVENT,',b'\tNMP_EVENT,\r\n\tNMP_NUCLEAR,')
        return raw,True
    if relative=='network/cnetworkmgr.cpp':
        raw=b'#include "client455_nuclear_receiver.h"\r\n'+raw
        # Both developer and ordinary branches keep the same real factory.
        marker=b'\tm_pNetMsgProcessor[NMP_EVENT]'
        lines=raw.splitlines(keepends=True);n=0;out=[]
        for line in lines:
            out.append(line)
            if line.startswith(marker) and b'new CNetMsgProcessor_Event' in line:
                out.append(b'\tm_pNetMsgProcessor[NMP_NUCLEAR] = new CNetMsgProcessor_Nuclear;\r\n');n+=1
        if n!=2:raise ValueError('Nuclear processor factory branches')
        raw=b''.join(out)
        once(b'\tif(pMsgHeader->m_byType[0]==21)',b'\tif(pMsgHeader->m_byType[0]==60)return m_pNetMsgProcessor[NMP_NUCLEAR]&&m_pNetMsgProcessor[NMP_NUCLEAR]->AnalysisServerPacket(pMsgHeader,pi_pMsg);\r\n\tif(pMsgHeader->m_byType[0]==21)')
        return raw,True
    if relative=='gameobject/board/common/cboard.cpp':
        begin,end=section(raw,b'CObjectBoard::UI_UseResult(',b'CObjectBoard::UI_UseResult(');body=raw[begin:end]
        if body.count(b'_GetGBM()->ClearOperation();')!=1:raise ValueError('455 use-result cleanup boundary')
        body=body.replace(b'_GetGBM()->ClearOperation();',b'if(!_GetGBM()->GetHoverObject())_GetGBM()->ClearOperation();');raw=raw[:begin]+body+raw[end:]
        return raw,True
    if relative=='gameobject/board/common/cboardmanager.cpp':
        begin,end=section(raw,b'CBoardManager::SetHoverObject(',b'CBoardManager::SetHoverObject(');body=raw[begin:end];at=body.index(b'{')+1
        raw=raw[:begin]+body[:at]+b'\r\n\tRF455_RequireHoverCancellation();'+body[at:]+raw[end:]
        return raw,True
    if relative=='gameobject/board/itemboard/cinventoryboard.cpp':
        raw=b'#include "client455_nuclear_receiver.h"\r\n'+raw
        begin,end=section(raw,b'CInventoryBoard::UI_UseResult_ProcessObject(',b'CInventoryBoard::UI_UseResult_ProcessObject(');body=raw[begin:end];at=body.index(b'{')+1
        statement=b'\r\n\tauto* typed455=_GetGBM()->GetObject(_GetGBM()->GetOrgBoardType(),_GetGBM()->GetOrgPackNo(),_GetGBM()->GetOrgSocketNo());\r\n\tif(RF455_IsOwnBoardObject455(typed455)){RF455_CompleteNuclearInventoryUse(typed455);return;}\r\n'
        raw=raw[:begin]+body[:at]+statement+body[at:]+raw[end:]
        return raw,True
    return raw,False
