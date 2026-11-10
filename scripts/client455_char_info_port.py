"""Connect the recovered455 CharInfo owners to the ordinary client window."""
def port_char_info(raw,relative,section,native):
    if relative=='userinterface/gamewindow/guicharinfowindow.h':
        raw=b'#include <memory>\nclass RF455CharInfoView;\n'+raw
        anchor=b'// < Member Function > -----------------------------------------------------'
        if raw.count(anchor)!=1:raise ValueError('CharInfo owner boundary')
        raw=raw.replace(anchor,b'''std::unique_ptr<RF455CharInfoView> m_view455;
    RF455CharInfoView& View455();
    void SetBattleMastery455(BYTE index,WORD current,WORD maximum);
    void SetMakeMastery455(BYTE index,WORD current,WORD maximum);
    void SetResistPoint455(BYTE index,int current,int minimum,int maximum);
    // < Member Function > -----------------------------------------------------''')
        first=raw.index(b'    //The ordinary window\'s existing basic-stat rows')
        last=raw.index(b'    CGUIText\t',first)
        raw=raw[:first]+b'''    CGUIText& ValueForLegacySlot455(unsigned slot){
        static const BYTE indices[14]={0,1,4,2,3,8,9,10,11,13,7,14,15,16};
        return slot<14?m_uiInfoValues455[indices[slot]]:m_uiCharInfo[slot];
    }
'''+raw[last:]
        # Existing callers now write the actual455 value owners. Attribute is
        # the legacy initial-class string; it is not the new race-rank field.
        for name in ['Name','Attr','Race','Sex','Guild']:
            raw=raw.replace(b'm_uiCharInfo['+name.encode()+b'].SetString',b'ValueForLegacySlot455('+name.encode()+b').SetString')
        raw=raw.replace(b'//455value widgets have their own indices. Legacy Level/Guild remain\n    //legacy fields;full455window placement/rendering is still pending.',b'//455 value owners are borrowed by the recovered main page.')
        return raw,True
    if relative!='userinterface/gamewindow/guicharinfowindow.cpp':return raw,False
    for name in ['Init','SetSprite','SetBound','MouseEvent','ScrollEvent','SetTab','IsOpenedTab','SetBattleMastery','SetBattleMasteryExp','SetMakeMastery','SetMakeMasteryExp','SetResistPoint','SetRaceType','SetFP','SetSP','SetExp']:
        sig=('CGUICharInfoWindow::'+name+'(').encode();first,last=section(raw,sig,sig)
        return_type=b'BOOL' if name=='IsOpenedTab' else b'void'
        start=raw.rfind(return_type,0,first)
        if raw[start:first].strip()!=return_type:raise ValueError('CharInfo function boundary '+name)
        raw=raw[:start]+b'//Recovered455 implementation below.\n'+raw[last:]
    raw=b'#include "client455_char_info.h"\n#include "client455_language.h"\n#include "client455_nation_paths.h"\n#include "client455_text_metrics.h"\n#include "client455_modal.h"\n#include "userinterface/uiglobal.h"\n#include <algorithm>\n#include <stdexcept>\n'+raw
    raw+=b'\n'+(native/'client455_char_info.inc').read_bytes()
    return raw,True
