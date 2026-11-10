"""Connect confirmed premium state owners;full cash/UI migration stays open."""
def port_premium_state(raw,relative,native):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Premium state anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='network/cnetworkmgr.h':
        raw=b'#include "client455_premium_state.h"\n'+raw
        once(b'RF455AccountHandshake m_account455;',b'''RF455AccountHandshake m_account455;
    //560C60 initializesDWORD436028;442440/5977E0 read/write it unnormalized.
    DWORD m_premium455=0;
    DWORD PremiumState455()const{return m_premium455;}
    void SetPremiumState455(DWORD value){m_premium455=value;}
    bool DispatchPremiumState455(char*,std::size_t);''')
        return raw,True
    if relative=='character/avatar/cavatar.h':
        raw=b'#include "client455_premium_state.h"\n'+raw
        #The CAvatar member is an owned state,never a cast ofthe old private ABI.
        once(b'RF455AvatarStage m_stage455;',b'RF455PremiumBenefits m_premiumBenefits455;\n\tRF455AvatarStage m_stage455;')
        once(b'void SetClientStage455(BYTE value)',b'RF455PremiumBenefits& PremiumBenefits455(){return m_premiumBenefits455;}\n    const RF455PremiumBenefits& PremiumBenefits455()const{return m_premiumBenefits455;}\n    void SetClientStage455(BYTE value)')
        return raw,True
    if relative=='network/cnetworkmgr.cpp':
        once(b'if(pMsgHeader->m_byType[0]==21)',b'if(pMsgHeader->m_byType[0]==57&&pMsgHeader->m_byType[1]==12)return DispatchPremiumState455(pi_pMsg,pMsgHeader->m_wSize-4);\n\tif(pMsgHeader->m_byType[0]==21)')
        raw+=b'\n'+(native/'client455_premium_state.inc').read_bytes()
        return raw,True
    return raw,False
