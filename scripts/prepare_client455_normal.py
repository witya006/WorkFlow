"""Port actual normal client consumers into a separate455-only source tree.

No CharacterMR link or fake method bodies. Open methods remain unresolved at link.
Engine033 and the diagnostic baseline are preserved byte-for-byte.
"""
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from compare_client_binaries import WS
from client455_d3d9_port import ENGINE_DEFINITIONS
from audit_client455_normal_character_api import code_only

def sha(data):return hashlib.sha256(data).hexdigest()
def write_owned(path,raw,previous):
    if path.exists() and path.read_bytes()!=raw and sha(path.read_bytes())!=previous.get(path.relative_to(WS).as_posix()):
        raise ValueError('Preserving differing normal port file:'+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or path.read_bytes()!=raw:path.write_bytes(raw)

def section(raw,first,last):
    masked=code_only(raw);start=masked.index(first);at=masked.index(b'{',masked.index(last,start));depth=1;end=at+1
    while depth:
        if end>=len(raw):raise ValueError('Unterminated source function')
        depth+=(masked[end]==ord('{'))-(masked[end]==ord('}'));end+=1
    return start,end

def kernel_sources(native):
    owner=json.loads((WS/'inventory/client455-renderer-owner-build.json').read_text())
    animation=json.loads((WS/'inventory/client455-animation-manager-build.json').read_text())
    wanted={owner['library']:owner['library_sha256'],animation['library']:animation['library_sha256']}
    wanted.update({r['file']:r['sha256'] for r in owner['dependencies']})
    found=set();sources={};evidence=[]
    for path in sorted((WS/'inventory').glob('client455*.json')):
        report=json.loads(path.read_text(encoding='utf-8'));library=report.get('library')
        if library not in wanted or report.get('library_sha256')!=wanted[library] or not report.get('source_sha256'):continue
        found.add(library);evidence.append({'report':path.relative_to(WS).as_posix(),'sha256':sha(path.read_bytes())})
        for name,digest in report['source_sha256'].items():
            if not name.startswith('client455_') or not name.endswith('.cpp'):continue
            source=native/name
            if sha(source.read_bytes())!=digest:raise ValueError('Changed kernel algorithm:'+name)
            sources[name]=source
    if found!=set(wanted):raise ValueError('Missing kernel production source reports:'+str(set(wanted)-found))
    return sorted(sources.values()),evidence

def main():
    port=WS/'work/client455-port';root=port/'normal';native=WS/'scripts/native';art=WS/'artifacts/client455-normal';art.mkdir(parents=True,exist_ok=True)
    manifest=art/'sources.json';previous={r['file']:r['sha256'] for r in json.loads(manifest.read_text())} if manifest.exists() else {};records=[]
    def save(path,raw,source=None,changes=None):
        write_owned(path,raw,previous);row={'file':path.relative_to(WS).as_posix(),'sha256':sha(raw)}
        if source:row.update(input=source.relative_to(WS).as_posix(),input_sha256=sha(source.read_bytes()))
        if changes:row['changes']=changes
        records.append(row)
    codec_reference=json.loads((WS/'inventory/client455-network-codec-reference.json').read_text())
    defaults=WS/codec_reference['generated_defaults']['file']
    if sha(defaults.read_bytes())!=codec_reference['generated_defaults']['sha256'] or sha((WS/'scripts/audit_client455_network_codec.py').read_bytes())!=codec_reference['script_sha256']:raise ValueError('Run current network codec audit before preparing')
    save(root/'include/client455_network_defaults.h',defaults.read_bytes(),defaults)
    intro_reference=json.loads((WS/'inventory/client455-tutorial-intro-reference.json').read_text())
    intro_tables=WS/intro_reference['generated']['file']
    if sha(intro_tables.read_bytes())!=intro_reference['generated']['sha256'] or sha((WS/'scripts/audit_client455_tutorial_intro.py').read_bytes())!=intro_reference['script_sha256']:raise ValueError('Run current Tutorial intro audit before preparing')
    save(root/'include/client455_tutorial_intro_tables.h',intro_tables.read_bytes(),intro_tables)
    # Keep the kernel type names/allocations unchanged. Add named confirmed
    # fields only to the normal port headers, leaving all existing evidence valid.
    replacements={
        'client455_mesh_bindings.h':(rb'struct RF455MeshStorage \{ unsigned char bytes\[5803\]; \};','client455_normal_mesh.inc'),
        'client455_character_manager.h':(rb'struct RF455CharacterStorage \{RF455KnownModelPrefix prefix;unsigned char tail\[388\];\};','client455_normal_model.inc'),
        'client455_animation.h':(rb'struct RF455AnimationStorage \{unsigned char bytes\[284\];\};','client455_normal_animation.inc')}
    for source in sorted(native.glob('*.h')):
        raw=source.read_bytes();changes=[]
        if source.name in replacements:
            pattern,filename=replacements[source.name];replacement=(native/filename).read_bytes()
            if source.name=='client455_animation.h':replacement=b'struct RF455AnimationData;\n'+replacement
            raw,count=re.subn(pattern,lambda _:replacement,raw)
            if count!=1:raise ValueError('Record definition changed:'+source.name)
            raw=b'#include <d3dx9.h>\n'+raw;changes=[filename]
        save(root/'include'/source.name,raw,source,changes)
    save(root/'include/Character.h',(native/'Character455.h').read_bytes(),native/'Character455.h')
    split_units=[]
    for source in sorted((port/'source/RF_Client').rglob('*')):
        if not source.is_file():continue
        if source.suffix.lower() in ['.lib','.dsp','.dsw']:continue
        raw=source.read_bytes();changes=[]
        if source.suffix.lower() in ['.cpp','.h']:
            relative=source.relative_to(port/'source/RF_Client').as_posix().lower()
            if relative=='network/protocol/characterdb.h':
                raw=b'#include "client455_storage.h"\r\n'+raw
                anchor=b'enum { INVEN = 0, EQUIP, EMBELLISH, BELT, FORCE, ANIMUS, LINKER };'
                if raw.count(anchor)!=1:raise ValueError('Legacy storage enum boundary changed')
                raw=raw.replace(anchor,b'enum { INVEN=0,EQUIP=1,EMBELLISH=2,FORCE=3,ANIMUS=4,TRUNK=5,LINKER=6,BELT=RF455_REMOVED_LEGACY_BELT };')
                anchor=b'enum { STORAGE_NUM = ANIMUS+1 };'
                if raw.count(anchor)!=1:raise ValueError('Storage count boundary changed')
                raw=raw.replace(anchor,b'enum { STORAGE_NUM = RF455_STORAGE_COUNT };')
                changes.append('455logical storage IDs Force3/Animus4/Trunk5;oldBelt INVALID255,not a wire-layout migration')
            if relative=='define.h':
                raw=b'#include "client455_storage.h"\r\n'+raw
                raw,count=re.subn(rb'(#define\s+MAX_BOARD_TYPE\s+)\( 19 \)',rb'\1( RF455_BOARD_COUNT )',raw)
                if count!=1:raise ValueError('Legacy board-count boundary changed')
                changes.append('455public board capacity56;registered classes tracked separately')
            if relative=='gameobject/board/common/cboardmanager.h':
                raw=b'#include "client455_storage.h"\r\n'+raw
                raw,count=re.subn(rb'(#define\s+_GetBeltBoard\(\)\s+)[^\r\n]+',rb'\1RF455_RejectRemovedLegacyBelt()',raw)
                if count!=1:raise ValueError('Legacy belt getter boundary changed')
                changes.append('retired potion-belt getter explicitly refuses unrecovered legacy callers')
            if relative=='gameobject/board/common/cboardmanager.cpp':
                raw,count=re.subn(rb'\tm_listBoard\[IBT_ITEM_BELT\][^\r\n]+\r?\n',b'\t//455: no separate legacy potion-belt object.\r\n',raw)
                if count!=1:raise ValueError('Legacy belt factory boundary changed')
                anchor=b'if( !( pi_byBoardType == IBT_INVENTORY || pi_byBoardType == IBT_EQUIP || pi_byBoardType == IBT_ITEM_BELT ) )'
                if raw.count(anchor)!=1:raise ValueError('ReturnItemToItemBoard guard boundary changed')
                raw=raw.replace(anchor,b'if( !RF455_IsPhysicalItemStorage(pi_byBoardType) )')
                changes.append('actual17existing class constructors now occupy455IDs;legacyBelt removed;ReturnItem guard0/1/5 from4FEF50;36class providers remain open')
            if relative=='gameobject/board/itemboard/citemboard.cpp':
                # These legacy helpers applied to Inventory/Equip/Belt. Retire
                # the missing Belt explicitly;do not turn its sentinel into a
                # numeric upper bound accepting arbitrary board IDs.
                anchor=b'if( m_byBoardType > IBT_ITEM_BELT )'
                if raw.count(anchor)!=2:raise ValueError('Legacy trade lookup boundaries changed')
                raw=raw.replace(anchor,b'if( m_byBoardType != IBT_INVENTORY && m_byBoardType != IBT_EQUIP )')
                changes.append('legacy trade lookups retain inventory/equip domain after belt retirement;full455trade/trunk remains open')
            if relative=='userinterface/guicontroller/guitextboard.h':
                raw=(native/'client455_gui_text_board.h').read_bytes()
                changes.append('455TextBoard fragment/line caches,WORD indices,markup and pixel layout source interfaces')
            if relative=='userinterface/guicontroller/guitextboard.cpp':
                raw=(native/'client455_gui_text_board.cpp').read_bytes()
                changes.append('455TextBoard fragment/line layout,retention,markup and actual ordinary drawing')
            if relative=='userinterface/guicontroller/guitext.h':
                anchor=b'\tDWORD\tdwColor;'
                if raw.count(anchor)!=1:raise ValueError('FONT_INFO color declaration changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tfloat\tfScale455;')
                anchor=b'\t\tdwStyle = 0;'
                if raw.count(anchor)!=1:raise ValueError('FONT_INFO constructor changed')
                raw=raw.replace(anchor,b'\t\tbySize = 0;\r\n\t\tfScale455 = 1.0f;\r\n'+anchor)
                anchor=b'\tFONT_INFO\tm_sFontInfo;'
                if raw.count(anchor)!=1:raise ValueError('CGUITextInfo font member changed')
                raw=raw.replace(anchor,b'\tWORD m_wTextLength455 = 0;\r\n'+anchor)
                anchor=b'\tchar *\t\tGetText( void ) { return m_pText; }'
                if raw.count(anchor)!=1:raise ValueError('CGUITextInfo text accessor changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tWORD GetLength455() const { return m_wTextLength455; }')
                changes.append('455FONT_INFO16/scale1/defaultsize0 and CGUITextInfo28 cachedWORD length;Clear retains length')
            if relative=='userinterface/guicontroller/guitext.cpp':
                raw=b'#include "client455_text_metrics.h"\r\n#include <stdexcept>\r\n'+raw
                first,last=section(raw,b'CGUITextInfo::SetText(',b'CGUITextInfo::SetText(')
                brace=raw.index(b'{',first)
                raw=raw[:brace+1]+b'\r\n const auto length455=pi_pText?strlen(pi_pText):0;\r\n if(length455>0xffff)throw std::length_error("CGUITextInfo WORD length domain exceeded");\r\n m_wTextLength455=static_cast<WORD>(length455);\r\n'+raw[brace+1:]
                raw=raw.replace(b'memcpy( &m_sFontInfo, pi_pFontInfo, sizeof( FONT_INFO ) );',b'if(pi_pFontInfo)memcpy( &m_sFontInfo, pi_pFontInfo, sizeof( FONT_INFO ) );')
                first,last=section(raw,b'CGUIText::SetString(',b'CGUIText::SetString(')
                raw=raw[:first]+(native/'client455_gui_text_size.inc').read_bytes()+raw[last:]
                first,last=section(raw,b'CGUIText::~CGUIText()',b'CGUIText::~CGUIText()')
                raw=raw[:first]+b'CGUIText::~CGUIText(){RF455_ForgetGuiText(this);}\r\n'+raw[last:]
                changes.append('455CGUIText measured byte-string geometry and exact high-style flag fallthrough;GDI route only')
            if relative=='userinterface/guicontroller/guiscrollbar.cpp':
                raw=(native/'client455_gui_scrollbar.cpp').read_bytes()
                changes.append('455ordinary scrollbar composite thumb/layout/amount/x87 snap/mouse/timers;legacy parent-routing adapter')
            if relative=='userinterface/gamewindow/etcwin/guiminimapwindow.h':
                raw=raw.replace(b'#include "../../GUIController/GUIText.h"',b'#include "../../GUIController/GUIText.h"\r\n#include "../../GUIController/GUIScrollbar.h"')
                anchor=b'class CGUIMiniMapWindow : public CGUIWindow'
                if raw.count(anchor)!=1:raise ValueError('Minimap base boundary changed')
                raw=raw.replace(anchor,anchor+b', public IScrollObserver')
                raw,count=re.subn(rb'CGUIObject([ \t]+m_uiTitleBoard;)',rb'CGUIContainer\1',raw)
                if count!=1:raise ValueError('Minimap frame storage changed')
                raw,count=re.subn(rb'CGUIObject([ \t]+m_uiMiniMap;)',rb'CGUIContainer\1',raw)
                if count!=1:raise ValueError('Minimap map container storage changed')
                anchor=b'BOOL\t\t\t\tm_bCreated;'
                if raw.count(anchor)!=1:raise ValueError('Minimap member boundary changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tCGUIScrollbarEX m_opacityScrollbar455;\r\n\tCGUIObject m_mapBackground455;\r\n\tCSprite m_frameSkin455;\r\n\tBYTE m_alpha455=255;\r\n\tBOOL m_zoomEligible455=FALSE,m_suppressZoom455=FALSE,m_clearZoomSuppression455=FALSE;\r\n\tvoid InitOpacity455();')
                anchor=b'void\tMouseEvent( _mouse_event & event );'
                if raw.count(anchor)!=1:raise ValueError('Minimap event API changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tvoid ScrollEvent(_scroll_event& event);\r\n\tvoid SetAlpha455(BYTE alpha);\r\n\tBYTE GetAlpha455()const{return m_alpha455;}\r\n\tBOOL TakeCameraZoomGate455();\r\n\tCGUIScrollbarEX& GetOpacityScrollbar455(){return m_opacityScrollbar455;}\r\n\tCGUIObject& GetMapBackground455(){return m_mapBackground455;}')
                changes.append('455minimap opacity owner and mapped frame/map containers;other455controls/world remain open')
            if relative=='userinterface/gamewindow/etcwin/guiminimapwindow.cpp':
                raw=b'#include "client455_minimap_opacity.h"\r\n#include "client455_modal.h"\r\n#include "client455_sprites.h"\r\n#include <io.h>\r\n#include <stdexcept>\r\n'+raw
                for method,expected in [(b'SetSprite(',b'void'),(b'Draw(',b'BOOL')]:
                    signature=b'CGUIMiniMapWindow::'+method
                    first,last=section(raw,signature,signature);begin=raw.rfind(b'\n',0,first-1)+1
                    if raw[begin:first].strip()!=expected:raise ValueError('Minimap method return boundary changed')
                    raw=raw[:begin]+b'//455implementation below.\r\n'+raw[last:]
                first,last=section(raw,b'CGUIMiniMapWindow::Init(',b'CGUIMiniMapWindow::Init(')
                body=raw[first:last]
                for member in [b'm_uiTitle',b'm_uiCloseButton']:
                    anchor=b'Add( &'+member+b' );'
                    if body.count(anchor)!=1:raise ValueError('Minimap title hierarchy changed')
                    body=body.replace(anchor,b'm_uiTitleBoard.'+anchor)
                body=body[:-1]+b'\r\n\tInitOpacity455();\r\n}'
                raw=raw[:first]+body+raw[last:]
                first,last=section(raw,b'CGUIMiniMapWindow::~CGUIMiniMapWindow()',b'CGUIMiniMapWindow::~CGUIMiniMapWindow()')
                body=raw[first:last];body=body[:-1]+b'\r\n\tm_frameSkin455.ReleaseSprite();\r\n}'
                raw=raw[:first]+body+raw[last:]
                raw+=b'\r\n'+(native/'client455_minimap_opacity_owner.inc').read_bytes()
                changes.append('455minimap EX opacity setup/observer/alpha for mapped owner;fullmap/zoom consumer remains open')
            if relative=='userinterface/guicontroller/guibutton.h':
                anchor=b'void\t\tSetLabel( char * pi_pLabel );'
                if raw.count(anchor)!=1:raise ValueError('Button label API changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tvoid SetLabelMetrics455(int width,int height){m_cLabel.SetSize(width,height);SetLabelPos((GetSizeX()-width)/2,(GetSizeY()-height)/2);}')
                changes.append('455modal caption uses measured GDI text extent rather than legacy byte-count geometry')
                anchor=b'DWORD\t\t\tm_dwLabelColor[2];'
                if raw.count(anchor)!=1:raise ValueError('Button caption colors changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tDWORD m_dwDisabledLabelColor455=0xff797979;')
            if relative=='userinterface/guicontroller/guibutton.cpp':
                first,last=section(raw,b'CGUIButtonEx::ResetLabelColor(',b'CGUIButtonEx::ResetLabelColor(')
                raw=raw[:first]+b'CGUIButtonEx::ResetLabelColor(void)\r\n{m_cLabel.GetFont()->dwColor=(GetState()&DISABLED)?m_dwDisabledLabelColor455:m_dwLabelColor[(GetState()&HOVERED)?1:0];}\r\n'+raw[last:]
                changes.append('confirmed455disabled caption color FF797979 before hover/normal colors')
            if relative=='userinterface/guicontroller/guiobject.h':
                anchor=b'BOOL\tIsActive( void )'
                position=raw.find(anchor)
                if position<0:raise ValueError('GUI active getter boundary changed')
                line=raw.rfind(b'\n',0,position)+1
                raw=raw[:line]+b'\tvirtual BOOL IsFocused455()const{return m_bEnableFocus&&m_bShow&&m_bActive&&s_pFocusedObject==this;}\r\n'+raw[line:]
                raw,count=re.subn(rb'(static\s+CGUIObject\s*\*\s*s_pFocusedObject\s*;)',rb'\1\r\n\tstatic CGUIObject *s_pRightPressed455,*s_pMouseModal455,*s_pLastClick455;\r\n\tstatic DWORD s_lastClickTime455;',raw)
                if count!=1:raise ValueError('GUI focus storage changed')
                raw,count=re.subn(rb'(BOOL\s+m_bEnableFocus\s*;)',rb'\1\r\n\tBOOL m_mouseInput455=TRUE;\r\n\tIFocusObserver455* m_focusObserver455=nullptr;',raw)
                if count!=1:raise ValueError('GUI focus flag changed')
                raw,count=re.subn(rb'(virtual\s+void\s+SetFocus\( void \)\s*)\{[^\r\n]*\}',rb'\1{TryFocus455();}',raw)
                if count!=1:raise ValueError('GUI SetFocus boundary changed')
                anchor=b'CGUIObject();'
                if raw.count(anchor)!=2:raise ValueError('GUI constructor/destructor declarations changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tBOOL TryFocus455();\r\n\tvoid KillFocus455();\r\n\tvoid SendFocusEvent455(WORD id);\r\n\tvoid AddFocusHandler455(IFocusObserver455* observer){m_focusObserver455=observer;}\r\n\tvoid SetMouseInput455(BOOL enabled){m_mouseInput455=enabled;}\r\n\tBOOL GetMouseInput455()const{return m_mouseInput455;}\r\n\tstatic void SetMouseModal455(CGUIObject* object);\r\n\tstatic CGUIObject* GetMouseModal455(){return s_pMouseModal455;}\r\n\tstatic CGUIObject* GetRightPressed455(){return s_pRightPressed455;}\r\n\tvirtual void CloseMouseModal455(){}',1)
                changes.append('confirmed455show/active/enableFocus/static-focus predicate')
            if relative=='userinterface/guicontroller/guiobjectevent.h':
                raw,count=re.subn(rb'#define\s+LMOUSE_STROKED\s+7',b'#define MOUSE_DOUBLE_STROKED 7\r\n#define LMOUSE_STROKED 8',raw)
                if count!=1:raise ValueError('Legacy right mouse event changed')
                raw,count=re.subn(rb'(WORD\s+wSelectIndex\s*;)',rb'\1\r\n\tDWORD nValue455;',raw)
                if count!=1:raise ValueError('GUI event payload changed')
                extra=b'\r\n#define FOCUS_ACQUIRED455 70\r\n#define FOCUS_RELEASED455 71\r\nstruct _focus_event455{CGUIObject* source;WORD id;};\r\nstruct _value_event455{CGUIObject* source;WORD id;DWORD value;};\r\nclass IFocusObserver455{public:virtual void FocusEvent455(_focus_event455& event)=0;};\r\nclass IValueObserver455{public:virtual void ValueEvent455(_value_event455& event)=0;};\r\n'
                raw=raw.replace(b'#endif // __GUIOBJECTEVENT_H__',extra+b'#endif // __GUIOBJECTEVENT_H__')
                changes.append('455double7/right8,focus70/value80 event domains and DWORD value payload')
            if relative=='userinterface/guicontroller/guiobject.cpp':
                raw=b'#include "client455_gui_input.h"\r\n'+raw
                for name,expected in [(b'InputProc(',b'BOOL'),(b'SendMouseEvent(',b'void'),(b'SendMouseMotionEvent(',b'void'),(b'MsgProc(',b'LRESULT'),(b'InActive(',b'void'),(b'DisableFocus(',b'void')]:
                    signature=b'CGUIObject::'+name;first,last=section(raw,signature,signature);begin=raw.rfind(b'\n',0,first-1)+1
                    if raw[begin:first].strip()!=expected:raise ValueError('GUI input method boundary changed')
                    raw=raw[:begin]+b'//455implementation below.\r\n'+raw[last:]
                first,last=section(raw,b'CGUIObject::~CGUIObject()',b'CGUIObject::~CGUIObject()')
                body=raw[first:last];body=body[:-1]+b'\r\n\tif(s_pRightPressed455==this)s_pRightPressed455=nullptr;\r\n\tif(s_pMouseModal455==this)s_pMouseModal455=nullptr;\r\n\tif(s_pLastClick455==this)s_pLastClick455=nullptr;\r\n}'
                raw=raw[:first]+body+raw[last:]+b'\r\n'+(native/'client455_gui_input_object.inc').read_bytes()
                changes.append('455mouse/doubleclick/modal guard/focus/key contracts;known object state cleanup')
            if relative=='userinterface/guicontroller/guiobjecteventproc.cpp':
                raw=b'#include "GUIDialogBox.h"\r\n'+raw
                anchor=b's_qEventList[i].wEventID == pi_EventInfo.wEventID )'
                if raw.count(anchor)!=1:raise ValueError('GUI queue duplicate key changed')
                raw=raw.replace(anchor,b's_qEventList[i].wEventID == pi_EventInfo.wEventID && s_qEventList[i].byKeyCode == pi_EventInfo.byKeyCode )')
                first,last=section(raw,b'CGUIObject::EventProcess(',b'CGUIObject::EventProcess(');begin=raw.rfind(b'\n',0,first-1)+1
                if raw[begin:first].strip()!=b'void':raise ValueError('GUI queue process boundary changed')
                raw=raw[:begin]+(native/'client455_gui_input_queue.inc').read_bytes()+raw[last:]
                changes.append('455queue dedup includes byte key;focus70/value80 dispatch;existing mouse/motion/key/scroll/window routes')
            if relative=='userinterface/guicontroller/guicontainer.h':
                anchor=b'virtual\tvoid\tAdd( CGUIObject * pi_pObj );'
                if raw.count(anchor)!=1:raise ValueError('Container Add API changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tvoid AddFront455(CGUIObject* object);')
                raw,count=re.subn(rb'(void\s+SetFocus\( void \)\s*)\{;\}',rb'\1{CGUIObject::SetFocus();}',raw)
                if count!=1:raise ValueError('Container SetFocus override changed')
                changes.append('455front insertion and inherited focus request;other container layers remain open')
            if relative=='userinterface/guicontroller/guicontainer.cpp':
                for signature,expected in [(b'CGUIContainer::Add( CGUIObject * pi_pObj )',b'void'),(b'CGUIContainer::Remove(',b'BOOL'),(b'CGUIContainer::RemoveAll(',b'void')]:
                    first,last=section(raw,signature,signature);begin=raw.rfind(b'\n',0,first-1)+1
                    if raw[begin:first].strip()!=expected:raise ValueError('Container input method boundary changed')
                    raw=raw[:begin]+b'//455implementation below.\r\n'+raw[last:]
                first,last=section(raw,b'CGUIContainer::CGUIContainer()',b'CGUIContainer::CGUIContainer()');body=raw[first:last];body=body[:-1]+b'CGUIObject::DisableFocus();\r\n}'
                raw=raw[:first]+body+raw[last:]+b'\r\n'+(native/'client455_gui_input_container.inc').read_bytes()
                changes.append('455default focus-off,Add show inheritance,Remove focus-only cleanup;other two layers remain open')
            if relative=='userinterface/guicontroller/guiscreen.h':
                anchor=b'CGUIScreen();'
                if raw.count(anchor)!=2:raise ValueError('Screen constructor boundary changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tvoid SetCapture455(CGUIWindow* window){m_capture455=window;if(window&&!IsAddedObject(window))m_capture455=nullptr;}\r\n\tCGUIWindow* GetCapture455()const{return m_capture455;}\r\n\tBOOL IsCaptureVisible455()const{return m_capture455&&m_capture455->IsShow();}',1)
                anchor=b'HWND\t\t\t\tm_hWnd;'
                if raw.count(anchor)!=1:raise ValueError('Screen storage boundary changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tCGUIWindow* m_capture455=nullptr;')
                changes.append('455screen capture pointer:validate main-list membership at assignment only;shown capture routes input and messages')
            if relative=='userinterface/guicontroller/guiwindow.cpp':
                signature=b'CGUIWindow::PostUIMessage( UINT pi_uMsg, LPARAM pi_lParam )'
                first,last=section(raw,signature,signature)
                raw=raw[:first]+signature+b'\r\n{auto* screen=CGUIScreen::GetSingletonPtr();if(!screen)return FALSE;return PostMessage(screen->GetHWND(),pi_uMsg,m_dwID,pi_lParam);}\r\n'+raw[last:]
                changes.append('455PostUIMessage checks Screen singleton,not current game stage;actual target45FBD0/65EFB0')
            if relative=='userinterface/guicontroller/guiscreen.cpp':
                first,last=section(raw,b'CGUIScreen::InputProc(',b'CGUIScreen::InputProc(');body=raw[first:last]
                anchor=b'if( g_nLockDlgBoxCount > 0 &&'
                if body.count(anchor)!=1:raise ValueError('Screen capture input boundary changed')
                body=body.replace(anchor,b'if(IsCaptureVisible455()){m_capture455->InputProc();g_dwGUIInputID=m_capture455->GetID();}\r\n\telse '+anchor)
                raw=raw[:first]+body+raw[last:]
                first,last=section(raw,b'CGUIScreen::MsgProc(',b'CGUIScreen::MsgProc(')
                replacement=(native/'client455_screen_message.inc').read_bytes().replace(b'LRESULT CGUIScreen::',b'CGUIScreen::',1)
                raw=raw[:first]+replacement+raw[last:]
                changes.append('455capture overrides ordinary windows after screen dialogs;captured ID regardless child return;MsgProc visible-only and modal short-circuit')
            if relative=='userinterface/mousedev.cpp':
                first,last=section(raw,b'CMouseDev::Update(',b'CMouseDev::Update(');body=raw[first:last];anchor=b'\tif( l_bPress )'
                if body.count(anchor)!=1:raise ValueError('Mouse update priority changed')
                body=body.replace(anchor,b'\telse if(gMouse.button & _MIDDLE_BUTTON_DOWN){m_wKey=3;l_bPress=true;}\r\n'+anchor)
                raw=raw[:first]+body+raw[last:];changes.append('455mouse priority left/right/middle and existing drag/move rules')
            if relative=='userinterface/guicontroller/guiscrollbar.h':
                raw=(native/'client455_gui_scrollbar.h').read_bytes()
                changes.append('455ordinary scrollbar source interfaces and composite scrollbar button')
            if relative=='userinterface/guicontroller/guidialogbox.h':
                raw,count=re.subn(rb'(BOOL[ \t]+m_bOpened[ \t]*;)',rb'\1\r\n\tBOOL m_allowClose455=FALSE; // Target base window starts with Escape disabled.',raw)
                if count!=1:raise ValueError('Dialog storage boundary changed')
                anchor=b'WORD\tGetResultMsg( void )'
                position=raw.find(anchor)
                if position<0:raise ValueError('Dialog result API changed')
                line=raw.rfind(b'\n',0,position)+1
                raw=raw[:line]+b'\tvoid SetAllowClose455(BOOL value){m_allowClose455=value;}\r\n\tBOOL GetAllowClose455()const{return m_allowClose455;}\r\n'+raw[line:]
                changes.append('455Escape close permission;Escape result3 rather than legacy cancel2')
            if relative=='userinterface/guicontroller/guidialogbox.cpp':
                raw=b'#include "client455_modal.h"\r\n'+raw
                first,last=section(raw,b'CGUIDialogBox::MsgProc(',b'CGUIDialogBox::MsgProc(')
                # Preserve the original leading LRESULT outside the replaced span.
                body=(native/'client455_dialog_input.inc').read_bytes().replace(b'LRESULT CGUIDialogBox::',b'CGUIDialogBox::',1)
                raw=raw[:first]+body+raw[last:]
                changes.append('455dialog Enter/Esc/YN/focused-chat-input gate;real GUI event queue retained')
            if relative=='userinterface/guicontroller/guimessagebox.cpp':
                raw=b'#include "client455_modal.h"\r\n'+raw
                for anchor,argument in [(b'g_uiMsgBox[l_nAvailMsgBox].SetDuration( pi_pCreateInfo->wDurationTime );',b'pi_pCreateInfo->bAllowClose455'),
                                         (b'g_uiMsgBox[l_nAvailMsgBox].SetDuration( pi_wDurationTime );',b'TRUE')]:
                    if raw.count(anchor)!=1:raise ValueError('Modal close-permission wrapper changed')
                    raw=raw.replace(anchor,anchor+b'\r\n\tg_uiMsgBox[l_nAvailMsgBox].SetAllowClose455('+argument+b');')
                raw=raw.replace(b'g_uiMsgBox[l_nAvailMsgBox].SetMsg( pi_pCreateInfo->pMsg );',b'g_uiMsgBox[l_nAvailMsgBox].SetMsg( pi_pCreateInfo->pMsg, pi_pCreateInfo->bFormatted455 );')
                raw=raw.replace(b'g_uiMsgBox[l_nAvailMsgBox].SetMsg( pi_pMsg );',b'g_uiMsgBox[l_nAvailMsgBox].SetMsg( pi_pMsg, pi_bFormatted455 );')
                raw,count=re.subn(rb'BOOL\s+pi_bScrollable/\* = FALSE\*/\s*\)',b'BOOL pi_bScrollable/* = FALSE*/, BOOL pi_bFormatted455, BOOL pi_bAllowClose455 )',raw)
                if count!=1:raise ValueError('Modal ordinary wrapper signature changed')
                raw=raw.replace(b'SetAllowClose455(TRUE);',b'SetAllowClose455(pi_bAllowClose455);')
                for method in [b'Init(',b'SetSprite(',b'SetAlpha(',b'SetBound(',b'Open(',b'SetMsg(']:
                    signature=b'CGUIMessagebox::'+method
                    first,last=section(raw,signature,signature)
                    # The return type is on a preceding line in the legacy TU.
                    begin=raw.rfind(b'\n',0,first-1)+1
                    if raw[begin:first].strip()!=b'void':raise ValueError('Modal method return boundary changed')
                    raw=raw[:begin]+b'// 455implementation below.\r\n'+raw[last:]
                raw+=b'\r\n'+(native/'client455_modal_init.inc').read_bytes()
                raw+=b'\r\n'+(native/'client455_modal_message.inc').read_bytes()
                changes.append('455normal modal controls and SetMsg plain/formatted color/pixel sizing/order;legacy SetBound bridge for target SetSize')
            if relative=='userinterface/guicontroller/guimessagebox.h':
                anchor=b'BOOL\t\t\tbLockOtherWin;'
                if raw.count(anchor)!=1:raise ValueError('Modal create-info boundary changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tBOOL bAllowClose455=TRUE;\r\n\tBOOL bFormatted455=FALSE;')
                raw,count=re.subn(rb'BOOL\s+pi_bScrollable = FALSE \);',b'BOOL pi_bScrollable = FALSE, BOOL pi_bFormatted455 = FALSE, BOOL pi_bAllowClose455 = TRUE );',raw,count=1)
                if count!=1:raise ValueError('Modal public wrapper declaration changed')
                first,last=section(raw,b'class CGUIMessagebox :',b'class CGUIMessagebox :')
                definition=raw[first:last]
                definition,count=re.subn(rb'void\s+SetMsg\( char \* pi_pMsg \);',b'void SetMsg(char* pi_pMsg, BOOL formatted455=FALSE);\r\n\tvoid SetSize(LONG width,LONG height);\r\n\tvoid SetSize(POINT& size){SetSize(size.x,size.y);}',definition)
                if count!=1:raise ValueError('Modal SetMsg declaration changed')
                raw=raw[:first]+definition+raw[last:]
                changes.append('typed455modal Escape permission/default reset for pooled windows')
            if relative=='character/avatar/cavatar.h':
                raw=b'#include "client455_avatar_stage.h"\r\n'+raw
                anchor=b'CAvatar();'
                if raw.count(anchor)!=2:raise ValueError('Avatar constructor boundary changed')
                api=(b'void SetClientStage455(BYTE value){m_stage455.current=value;}\r\n\tBYTE GetClientStage455()const{return m_stage455.current;}\r\n\tBOOL IsClientStage455(BYTE value)const{return m_stage455.is(value);}\r\n\tvoid SetSkipTutorial455(DWORD value){m_stage455.skipTutorial=value;}\r\n\tDWORD GetSkipTutorial455()const{return m_stage455.skipTutorial;}\r\n\tBYTE SelectClientStage455(BYTE value)const{return m_stage455.select(value);}\r\n\tBOOL HandlesTutorialLocally455()const{return m_stage455.handlesTutorialLocally();}\r\n\t')
                raw=raw.replace(anchor,api+anchor,1)
                anchor=b'QUEST_INFO *\t\t\t\tm_pTutorialInfo;'
                if raw.count(anchor)!=1:raise ValueError('Avatar Tutorial storage boundary changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tRF455AvatarStage m_stage455;')
                for member in ['Gold','Dalant']:
                    raw,count=re.subn(rb'DWORD(\s+m_dw'+member.encode()+rb'\s*;)',rb'__int64\1',raw)
                    if count!=1:raise ValueError('Avatar money field '+member)
                    raw,count=re.subn(rb'(void\s+Set'+member.encode()+rb'\(\s*)DWORD',rb'\1__int64',raw)
                    if count!=1:raise ValueError('Avatar money setter '+member)
                    raw,count=re.subn(rb'inline\s+DWORD(\s+Get'+member.encode()+rb'\()',rb'inline __int64\1',raw)
                    if count!=1:raise ValueError('Avatar money getter '+member)
                changes.append('455Avatar stageBYTE/skipDWORD initialized0,copyable source state;explicit455IDs separate from legacy3stage factory')
                changes.append('455signed64 money storage and typed setter/getter ABI;network/trade producers remain separate acceptance gaps')
            if relative=='character/avatar/cavatar_etc.cpp':
                for member in ['Gold','Dalant']:
                    raw,count=re.subn(rb'(CAvatar::Set'+member.encode()+rb'\(\s*)DWORD',rb'\1__int64',raw)
                    if count!=1:raise ValueError('Avatar money implementation '+member)
                changes.append('45564-bit Avatar money setters retain real optional inventory update')
            if relative=='userinterface/gamewindow/guiinventorywindow.h':
                for member in ['Dalant','Gold']:
                    raw,count=re.subn(rb'DWORD(\s+m_dwOwn'+member.encode()+rb'\s*;)',rb'__int64\1',raw)
                    if count!=1:raise ValueError('Inventory money field '+member)
                    raw,count=re.subn(rb'(void\s+SetOwn'+member.encode()+rb'\(\s*)DWORD',rb'\1__int64',raw)
                    if count!=1:raise ValueError('Inventory money setter '+member)
                    raw,count=re.subn(rb'inline\s+DWORD(\s+GetOwn'+member.encode()+rb'\()',rb'inline __int64\1',raw)
                    if count!=1:raise ValueError('Inventory money getter '+member)
                changes.append('455signed64 inventory money fields and API')
            if relative=='userinterface/gamewindow/guiinventorywindow.cpp':
                raw=b'#include "client455_money.h"\r\n'+raw
                for member,filename in [('Dalant','client455_inventory_money.inc'),('Gold','client455_inventory_gold.inc')]:
                    method=('CGUIInventoryWindow::SetOwn'+member+'(').encode();first,last=section(raw,method,method)
                    raw=raw[:first]+(native/filename).read_bytes()+raw[last:]
                changes.append('455grouped signed64 money labels positioned before wider title with10pixel gap;no legacy fixed318/335 coordinates')
            if relative=='character/avatar/cavatar.cpp':
                raw+=b'\r\n'+(native/'client455_avatar_stage.inc').read_bytes()
                changes.append('real Avatar global supplies455Tutorial-stage login packing predicate')
            if relative=='gameprogress/cgameprogress.h':
                raw,count=re.subn(rb'(BOOL\s+m_bIsLoadedData\s*;)',rb'\1\r\n\tDWORD m_nextStage455=0xffffffff; // Owned initial safety domain;target Init retains this field.',raw)
                if count!=1:raise ValueError('Progress storage boundary changed')
                anchor=b'BOOL\tIsCreated( void )'
                if raw.count(anchor)!=1:raise ValueError('Progress getter boundary changed')
                api=b'void SetNextStage455(DWORD value){m_nextStage455=value;}\r\n\tDWORD GetNextStage455()const{return m_nextStage455;}\r\n\tvoid RequestStageExit455(){m_bExit=TRUE;}\r\n\t'
                raw=raw.replace(anchor,api+anchor)
                changes.append('target nextstageDWORD retained across Init;explicit next/exit API;whole4stage factory remains open')
            if relative=='gameprogress/cgameprogress.cpp':
                method=b'CGameProgress::MainLoop(';first,last=section(raw,method,method)
                raw=raw[:first]+(native/'client455_progress_loop.inc').read_bytes()+raw[last:]
                changes.append('455base input/exit/update/render/reset ordering;focus handling belongs to derived stages')
            if relative=='gameprogress/cgp_title.cpp':
                method=b'CGP_Title::CGP_Title()';first,last=section(raw,method,method);body=raw[first:last]
                if body.count(b'Init();')!=1:raise ValueError('Title nextstage boundary changed')
                body=body.replace(b'Init();',b'Init();\r\n\tSetNextStage455(1);');raw=raw[:first]+body+raw[last:]
                changes.append('455Title constructor sets explicitnext1;fullTitle lifecycle notyetported')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='userinterface/spritemgr.cpp':
                start,end=section(raw,b'CSpriteMgr::LoadSprite( WORD pi_wSpriteID )',b'CSpriteMgr::LoadSprite( WORD pi_wSpriteID )')
                body=raw[start:end];anchor=b'\tif( pi_wSpriteID >= SP_ID_MINIMAP )'
                if body.count(anchor)!=1:raise ValueError('Normal sprite entry changed')
                nl=b'\r\n' if b'\r\n' in raw else b'\n'
                bridge=(b'\t// IDs0/1 agree with455;other legacy UI groups still need semantic migration.'+nl+
                    b'\tif(pi_wSpriteID==SP_ID_MOUSE || pi_wSpriteID==SP_ID_COMMON){'+nl+
                    b'\t\tchar path[260];if(RF455_SelectSpritePath(pi_wSpriteID,path,sizeof(path)))LoadSprite(pi_wSpriteID,path);return;'+nl+b'\t}'+nl)
                body=body.replace(anchor,bridge+anchor);raw=b'#include "client455_sprites.h"'+nl+raw[:start]+body+raw[end:]
                changes.append('confirmed455localized/Common sprite route for actual startup mouse/common consumers;other legacyUI groups open')
            if source.name.lower()=='cland.cpp':
                raw=b'#include <cstring>\r\n'+raw
                first,last=section(raw,b'CLand::LoadLevel( char * pi_pLevelName )',b'CLand::LoadLevel( char * pi_pLevelName )')
                body=(native/'client455_land_load.inc').read_bytes().replace(b'BOOL CLand::',b'CLand::',1)
                raw=raw[:first]+body+raw[last:]
                first,last=section(raw,b'CLand::LoadLevel( BYTE pi_byMapIndex )',b'CLand::LoadLevel( BYTE pi_byMapIndex )')
                body=raw[first:last];anchor=b'm_pLevel->LoadLevel( m_pMapInfo[pi_byMapIndex].pFileName );'
                if body.count(anchor)!=1:raise ValueError('Indexed land load boundary changed')
                body=body.replace(anchor,b'if(!LoadLevel(m_pMapInfo[pi_byMapIndex].pFileName))return FALSE;');raw=raw[:first]+body+raw[last:]
                changes.append('455BSP level ownership recreated per load and camera rebound;INS provider explicitly missing;fullILevel/Empty/INS stillopen')
                start,end=section(raw,b'CLand::UnloadLevel( void )',b'CLand::UnloadLevel( void )')
                body=raw[start:end];anchor=b'\tassert( m_pLevel != NULL );'
                if body.count(anchor)!=1:raise ValueError('Land unload entry changed')
                nl=b'\r\n' if b'\r\n' in body else b'\n'
                body=body.replace(anchor,b'\t// 455 RVA 3C8F30: an uncreated level returns FALSE before cleanup.'+nl+b'\tif( m_pLevel == NULL ) return FALSE;')
                raw=raw[:start]+body+raw[end:]
                changes.append('confirmed455 unload early return before level creation;full ILevel ownership port remains open')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='mainapp.cpp':
                first,last=section(raw,b'CMainApp::LoadData(',b'CMainApp::LoadData(');body=raw[first:last];anchor=b'\tm_bLoadedAllData = TRUE;'
                if body.count(anchor)!=1:raise ValueError('MainApp default FOV boundary changed')
                body=body.replace(anchor,anchor+b'\r\n\tRF455_SetDefaultCameraFov(0.6f);SetDefaultFov(); //4557D1BCB/D1');raw=raw[:first]+body+raw[last:]
                raw=b'#include "client455_movie_state.h"\r\n'+raw
                first,last=section(raw,b'CMainApp::GameMainLoop(',b'CMainApp::GameMainLoop(');body=raw[first:last]
                replacement=(b'if(!m_pGameProgress->IsCreated()){\r\n\t\t\tif(!m_pGameProgress->Create())return FALSE;\r\n\t\t\tif(_GetAvatar())_GetAvatar()->SetClientStage455(RF455_FromLegacyStage(m_byGameProgressID));\r\n\t\t}')
                body,count=re.subn(rb'if\( !m_pGameProgress->IsCreated\(\) \)\s+m_pGameProgress->Create\(\);',lambda _:replacement,body)
                if count!=1:raise ValueError('MainApp stage Create boundary changed')
                raw=raw[:first]+body+raw[last:]
                raw=b'#include "client455_avatar_stage.h"\r\n'+raw
                anchor=b'\tInitR3Engine();'
                if raw.count(anchor)!=1:raise ValueError('Normal WinMain engine boundary changed')
                nl=b'\r\n' if b'\r\n' in raw else b'\n'
                raw=b'#include "client455_nation_paths.h"'+nl+b'#include "client455_language.h"'+nl+b'#include "client455_launcher.h"'+nl+b'#include "client455_bootstrap.h"'+nl+b'#include "client455_connection.h"'+nl+raw.replace(anchor,b'\tif(!RF455_InitializeNationPaths()) return 0;'+nl+b'\tif(!g_MainApp.GetDataFromLauncher()){MessageBoxA(NULL,"Connectioninfo load failure.","RF Online",0);return 0;}'+nl+b'\tif(!RF455_InitializeLanguageData()){MessageBoxA(NULL,"LangPack reading failure.","RF Online",0);return 0;}'+nl+b'\tRF455_LoadBootstrapSettings();'+nl+b'\tg_MainApp.CreateNetworkMgr455();'+nl+b'\tif(!RF455_CheckStartupInstance()) return 0;'+nl+b'\tif(!g_MainApp.ConnectNetwork455()) return 0;'+nl+anchor)
                start,end=section(raw,b'CMainApp::GetDataFromLauncher( void )',b'CMainApp::GetDataFromLauncher( void )')
                raw=raw[:start]+(native/'client455_launcher_bridge.inc').read_bytes()+raw[end:]
                start,end=section(raw,b'CMainApp::Create( void )',b'CMainApp::Create( void )');body=raw[start:end]
                pattern=rb'\tif\( !GetDataFromLauncher\(\) \)\s*\{\s*RequestQuitProgram\(\);\s*\}'
                body,count=re.subn(pattern,b'\t// 455 launcher data is loaded in WinMain before language/engine.',body)
                if count!=1:raise ValueError('Legacy late launcher call changed')
                if body.count(b'\tm_cNetworkMgr.Create();')!=1:raise ValueError('Legacy network creation boundary changed')
                body=body.replace(b'\tm_cNetworkMgr.Create();',b'\t// Network creation moved before engine in WinMain,as in455.')
                # Keep a named initialization boundary for diagnostics in the
                # modern port;this one-time call is otherwise inlined away.
                body=body.replace(b'CMainApp::Create( void )',b'__declspec(noinline) CMainApp::Create( void )',1)
                raw=raw[:start]+body+raw[end:]+nl+(native/'client455_bootstrap_bridge.inc').read_bytes()+nl+(native/'client455_connection_bridge.inc').read_bytes()
                changes.append('455country launcher before language;typed network fields;remove late legacy launcher read;full connection order remains open')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='mainapp.h':
                anchor=b'BOOL\tGetDataFromLauncher( void );'
                if raw.count(anchor)!=1:raise ValueError('MainApp public launcher declaration changed')
                raw=raw.replace(anchor,b'BOOL CreateNetworkMgr455( void );\r\n\tBOOL ConnectNetwork455();\r\n\t'+anchor)
                changes.append('named ordinary pre-engine network creation entry')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='network/cnetworkmgr.h':
                raw=b'#include "client455_account.h"\r\n'+raw
                first,last=section(raw,b'struct WORLD_SERVER_INFO',b'struct WORLD_SERVER_INFO')
                raw=raw[:first]+b'using WORLD_SERVER_INFO=RF455WorldInfo;'+raw[last+1:]
                raw,count=re.subn(rb'(#define\s+MAX_WORLD_SERVER\s+\(\s*)100\b',rb'\g<1>300',raw)
                if count!=1:raise ValueError('World list capacity changed')
                raw,count=re.subn(rb'BYTE(\s+m_byWorldServerNum\s*;)',rb'std::uint32_t\1',raw)
                if count!=1:raise ValueError('World list count storage changed')
                raw=raw.replace(b'AccountMsg_LoginAccountRequest_cllo( void )',b'AccountMsg_LoginAccountRequest_cllo( const char* ticket=nullptr )')
                anchor=b'\tCNetworkMgr();'
                if raw.count(anchor)!=1:raise ValueError('Account public declaration boundary changed')
                raw=raw.replace(anchor,b'\tRF455AccountHandshake m_account455;\r\n\tBOOL DispatchTutorial455(DWORD,BYTE*,void*,int);\r\n\tBOOL AccountMsg_CryptoSeedRequest455();\r\n\tbool DispatchAccount455(BYTE,char*,std::size_t);\r\n'+anchor)
                for name,size in [(b'm_pID',51),(b'm_pPassword',33)]:
                    raw,count=re.subn(rb'\b'+name+rb'\[32\]',name+b'['+str(size).encode()+b']',raw)
                    if count!=1:raise ValueError('Normal network credential storage changed')
                raw,count=re.subn(rb'(#define\s+MAX_GAME_SERVER\s+)3\b',rb'\g<1>4',raw)
                if count!=1:raise ValueError('Normal network endpoint count changed')
                raw,count=re.subn(rb'(char\s+m_nActiveServerID\s*;)',rb'\1\r\n\tBYTE m_activeServer455[6];',raw)
                if count!=1:raise ValueError('Normal active network field changed')
                anchor=b'void\tConnect( BYTE pi_byServerType );'
                if raw.count(anchor)!=1:raise ValueError('Normal network connect declaration changed')
                raw=raw.replace(anchor,b'int ConnectToServer455(BYTE endpoint,BYTE process=0);\r\n\t\t\t'+anchor)
                changes.append('455source-owned identifier51/password33 storage;wire protocols still pending')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='network/cnetworkmgr.cpp':
                nl=b'\r\n' if b'\r\n' in raw else b'\n';raw=b'#include "client455_launcher.h"'+nl+b'#include "client455_network_state.h"'+nl+b'#include "client455_account.h"'+nl+b'#include "client455_language.h"'+nl+raw
                for method,field in [(b'SetID',b'm_pID'),(b'SetPassword',b'm_pPassword')]:
                    signature=b'CNetworkMgr::'+method+b'( char * pi_p'+(b'ID' if method==b'SetID' else b'Password')+b' )'
                    start,end=section(raw,signature,signature);param=b'pi_pID' if method==b'SetID' else b'pi_pPassword'
                    raw=raw[:start]+signature+nl+b'{'+nl+b'\tRF455_CopyLauncherText('+field+b','+param+b',sizeof('+field+b'));'+nl+b'}'+raw[end:]
                    raw=re.sub(rb'ZeroMemory\( '+field+rb', 32 \)',b'ZeroMemory( '+field+b', sizeof('+field+b') )',raw)
                signature=b'CNetworkMgr::Connect( BYTE pi_byServerType )';start,end=section(raw,signature,signature)
                raw=raw[:start]+signature+nl+b'{ConnectToServer455(pi_byServerType,0);}' +raw[end:]+nl+(native/'client455_network_bridge.inc').read_bytes()
                for method in [b'CNetworkMgr::Init( void )',b'CNetworkMgr::Create( void )']:
                    start,end=section(raw,method,method);body=raw[start:end];at=body.index(b'{')+1;body=body[:at]+nl+b'\tmemset(m_activeServer455,255,sizeof(m_activeServer455));'+body[at:];raw=raw[:start]+body+raw[end:]
                start,end=section(raw,b'CNetworkMgr::AcceptClientCheck(',b'CNetworkMgr::AcceptClientCheck(');body=raw[start:end];at=body.index(b'{')+1
                body=body[:at]+nl+b'\tif(dwProID>=6)return;'+nl+b'\tm_nActiveServerID=static_cast<char>(m_activeServer455[dwProID]);'+nl+b'\tif(m_nActiveServerID<0 || m_nActiveServerID>=MAX_GAME_SERVER)return;'+body[at:]
                anchor=b'\tif( m_nActiveServerID == GST_ZONE )'
                if body.count(anchor)!=1:raise ValueError('Gate accept branch changed')
                body=body.replace(anchor,b'\tif(m_nActiveServerID==0)AccountMsg_CryptoSeedRequest455();'+nl+anchor)
                raw=raw[:start]+body+raw[end:]
                start,end=section(raw,b'CNetworkMgr::Init( void )',b'CNetworkMgr::Init( void )');body=raw[start:end];at=body.index(b'{')+1
                body=body[:at]+nl+b'\tm_account455.delta=0;m_account455.mask=0;m_account455.selectedWorld=0xffffffff;m_account455.zoneRequestMode=-1;'+body[at:];raw=raw[:start]+body+raw[end:]
                dispatch=(native/'client455_account_dispatch.inc').read_bytes()
                for method in [b'CNetworkMgr::SendRequestMsg(',b'CNetworkMgr::ReceiveResponseMsg(']:
                    start,end=section(raw,method,method);a,b=section(dispatch,method,method);raw=raw[:start]+dispatch[a:b]+raw[end:]
                start,end=section(raw,b'CNetworkMgr::AnalysisServerPacket(',b'CNetworkMgr::AnalysisServerPacket(');body=raw[start:end];at=body.index(b'{')+1
                body=body[:at]+nl+b'\tif(!pMsgHeader || pMsgHeader->m_wSize<4)return false;'+nl+b'\tif(pMsgHeader->m_byType[0]==21)return DispatchAccount455(pMsgHeader->m_byType[1],pi_pMsg,pMsgHeader->m_wSize-4);'+body[at:]
                new_methods=dispatch[dispatch.index(b'BOOL CNetworkMgr::AccountMsg_CryptoSeedRequest455'):]
                raw=raw[:start]+body+raw[end:]+nl+new_methods
                start,end=section(raw,b'CNetworkMgr::CloseClientCheck(',b'CNetworkMgr::CloseClientCheck(');body=raw[start:end]
                body,count=re.subn(rb'(m_nActiveServerID\s*=\s*GST_NONE;)',rb'\1\r\n\tif(dwProID<6)m_activeServer455[dwProID]=255;',body)
                if count!=1:raise ValueError('Normal close callback reset changed')
                raw=raw[:start]+body+raw[end:]
                changes.append('confirmed bounded455identifier/password setters;no credentials logged')
                start,end=section(raw,b'CNetworkMgr::Create( void )',b'CNetworkMgr::Create( void )');body=raw[start:end]
                first=body.index(b'_NET_TYPE_PARAM typeParam;');last=body.index(b'SetNetSystem( 1, &typeParam, "RF_CLIENT");',first)+len(b'SetNetSystem( 1, &typeParam, "RF_CLIENT");')
                body=body[:first]+(native/'client455_network_config.inc').read_bytes()+body[last:]
                if body.count(b'return TRUE;')!=1:raise ValueError('Network Create return changed')
                body=body.replace(b'return TRUE;',b'return transportCreated;');raw=raw[:start]+body+raw[end:]
                signature=b'CNetworkMgr::SendNetMessage(';start,end=section(raw,signature,signature);body=raw[start:end];at=body.index(b'{')+1
                body=body[:at]+nl+b'\tif(_GetAvatar()&&_GetAvatar()->HandlesTutorialLocally455())return DispatchTutorial455(pi_dwClientIndex,pi_pType,pi_pMsg,pi_nSize);'+nl+b'\tm_Process[0].m_codec455.enabled=(pi_pType[0]!=21);'+body[at:];raw=raw[:start]+body+raw[end:]
                raw=b'#include "client455_avatar_stage.h"\r\n'+raw+b'\r\n'+(native/'client455_tutorial_dispatch.inc').read_bytes()
                changes.append('455actual Avatar stage2+skip0 gates localTutorial route;knownignored packets swallowed,1/17directtransport,missing localhandlers explicitly fail')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='network/cnetworkmgr_masterservermsg.cpp':
                raw=b'#include "client455_account.h"\r\n#include "client455_avatar_stage.h"\r\n#include "client455_nation_paths.h"\r\n'+raw
                bridge=(native/'client455_account_bridge.inc').read_bytes()
                for method in [b'JoinAccountRequest_cllo',b'JoinAccountResult_locl',b'LoginAccountRequest_cllo',b'LoginAccountResult_locl',b'WorldListRequest_cllo',b'WorldListResult_locl',b'SelectWorldRequest_cllo',b'SelectWorldResult_locl',b'PushCloseRequest_cllo',b'PushCloseResult_locl']:
                    signature=b'CNetworkMgr::AccountMsg_'+method+b'('
                    first,last=section(raw,signature,signature);a,b=section(bridge,signature,signature)
                    raw=raw[:first]+bridge[a:b]+raw[last:]
                changes.append('455 account84/342/88 payloads,seed mask,50/24 replies and72byte world records;full game protocols/UI remain open')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='network/networklib/networking.h':
                anchor=b'bool Connect(DWORD dwProID, DWORD dwSocketIndex, DWORD dwIP, WORD wPort);'
                if raw.count(anchor)!=1:raise ValueError('Normal transport declaration changed')
                raw=raw.replace(anchor,b'int ConnectRaw455(DWORD process,DWORD socketIndex,DWORD address,WORD port);\r\n\t'+anchor)
                raw=raw.replace(b'#define max_process 3',b'#define max_process 6').replace(b'void SetNetSystem(',b'bool SetNetSystem(')
                anchor=b'void OnLoop();'
                if raw.count(anchor)!=1:raise ValueError('Network event pump declaration changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tvoid PumpEvents455(){for(DWORD i=0;i<m_dwUseProcessNum;++i)m_Process[i].PumpEvents455();}')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='network/networklib/networking.cpp':
                signature=b'bool CNetWorking::Connect(';start,end=section(raw,signature,signature)
                raw=raw[:start]+(native/'client455_network_transport.inc').read_bytes()+raw[end:]
                start,end=section(raw,b'void CNetWorking::SetNetSystem(',b'void CNetWorking::SetNetSystem(');body=raw[start:end]
                body=body.replace(b'void CNetWorking::SetNetSystem(',b'bool CNetWorking::SetNetSystem(')
                anchor=b'm_Process[i].SetProcess(i, &pType[i], this);'
                if body.count(anchor)!=1:raise ValueError('Transport process initialization changed')
                body=body.replace(anchor,b'if(!m_Process[i].SetProcess(i, &pType[i], this))return false;')
                body=body[:-1]+b'\r\n\treturn true;\r\n}';raw=raw[:start]+body+raw[end:]
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='network/networklib/netprocess.h':
                raw=b'#include "client455_network_codec.h"\r\n#include <vector>\r\n#include <new>\r\n'+raw
                start,end=section(raw,b'struct _NET_BUFFER',b'struct _NET_BUFFER');raw=raw[:start]+(native/'client455_network_buffer.inc').read_bytes()+raw[end+1:] if raw[end:end+1]==b';' else raw[:start]+(native/'client455_network_buffer.inc').read_bytes()+raw[end:]
                pattern=rb'CNetSocket\s+m_NetSocket;'
                raw,count=re.subn(pattern,lambda match:b'RF455NetworkCodec m_codec455;\r\n\tstd::vector<char> m_receiveScratch455,m_sendScratch455;\r\n\tunsigned char m_encoded455[20000],m_decoded455[20000];\r\n\t'+match[0],raw)
                if count!=1:raise ValueError('NetProcess socket member changed')
                anchor=b'void OnLoop();'
                if raw.count(anchor)!=1:raise ValueError('Process event pump declaration changed')
                raw=raw.replace(anchor,anchor+b'\r\n\tvoid PumpEvents455(){_Receipt();}')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='network/networklib/netprocess.cpp':
                raw=b'#include "client455_connection.h"\r\n'+raw
                signature=b'CNetProcess::_Receipt(';start,end=section(raw,signature,signature)
                raw=raw[:start]+(native/'client455_network_receipt.inc').read_bytes()+raw[end:]
                signature=b'CNetProcess::SetProcess(';start,end=section(raw,signature,signature);body=raw[start:end]
                anchor=b'm_NetSocket.SetSocket(&m_Type);'
                if body.count(anchor)!=1:raise ValueError('Socket initialization changed')
                body=body.replace(anchor,b'if(!m_NetSocket.SetSocket(&m_Type))return false;')
                pattern=rb'(m_pSendBuffer\s*=\s*new _NET_BUFFER\s*\[m_Type.m_wSocketMaxNum\];)'
                addition=b'\r\n\tm_receiveScratch455.resize(20000);m_sendScratch455.resize(1000000);\r\n\tfor(unsigned i=0;i<m_Type.m_wSocketMaxNum;++i){\r\n\t\tif(!m_pRecvBuffer[i].Configure(20000,20000,m_receiveScratch455.data()) || !m_pSendBuffer[i].Configure(1000000,1000000,m_sendScratch455.data()))return false;\r\n\t}'
                body,count=re.subn(pattern,lambda match:match[0]+addition,body)
                if count!=1:raise ValueError('Process buffer allocation changed')
                raw=raw[:start]+body+raw[end:]
                signature=b'CNetProcess::RecvThread(';start,end=section(raw,signature,signature);body=raw[start:end]
                body=body.replace(b'MAX_NET_BUFFER',b'pNB->m_capacity').replace(b'MAX_EXTRA_BUFFER',b'pNB->m_extra');raw=raw[:start]+body+raw[end:]
                signature=b'CNetProcess::LoadSendMsg(DWORD dwClientIndex, BYTE* pbyType';start,end=section(raw,signature,signature)
                raw=raw[:start]+(native/'client455_network_send.inc').read_bytes()+raw[end:]
                signature=b'CNetProcess::_PopRecvMsg(';start,end=section(raw,signature,signature);body=raw[start:end]
                body=body.replace(b'pNB->GetPopPoint(&bMiss)',b'pNB->GetPopPoint(&bMiss,m_codec455.configured&&m_codec455.enabled)')
                anchor=b'_MSG_HEADER* pHeader = (_MSG_HEADER*)pMsg;'
                if body.count(anchor)!=1:raise ValueError('Receive packet publication changed')
                body=body.replace(anchor,b'WORD wireSize;memcpy(&wireSize,pMsg,2);std::size_t decodedSize=0;\r\n\t\tif(!m_codec455.decode(pMsg,wireSize,m_decoded455,sizeof(m_decoded455),decodedSize)){PushCloseNode(wSocketIndex);return;}\r\n\t\t_MSG_HEADER* pHeader=(_MSG_HEADER*)m_decoded455;\r\n\t\tpMsg=(char*)m_decoded455;')
                body=body.replace(b'pNB->AddPopPos(pHeader->m_wSize)',b'pNB->AddPopPos(wireSize)');raw=raw[:start]+body+raw[end:]
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='addcodebyyun/particlelist.cpp':
                old=b'pd3dDevice->CopyRects(backbuf,&r,1,psurface[count],&pt)'
                if raw.count(old)!=1:raise ValueError('Screenshot readback call changed')
                raw=raw.replace(old,b'pd3dDevice->GetRenderTargetData(backbuf,psurface[count])')
                old=b'Desc.Format, D3DPOOL_SCRATCH, &psurface[i], NULL'
                if raw.count(old)!=1:raise ValueError('Screenshot readback surface changed')
                raw=raw.replace(old,b'Desc.Format, D3DPOOL_SYSTEMMEM, &psurface[i], NULL')
                changes.append('D3D9 full-render-target readback into SYSTEMMEM')
            raw,n=re.subn(rb'\b(?:class|struct)\s+(CHARACTEROBJECT|ChAnimation|ObjectMesh)\s*;',b'',raw)
            if n:changes.append('replace legacy forward declarations with455type aliases')
            raw,n=re.subn(rb'\b(?:class|struct)\s+(CHARACTEROBJECT|ChAnimation|ObjectMesh)\b',rb'\1',raw)
            if n:changes.append('remove elaborated legacy type names')
            raw,n=re.subn(rb'\.m_ParticleID\b',b'.particleSlots()',raw)
            if n:changes.append('open455particle slot contract')
            raw,n=re.subn(rb'(\bpMesh\[[^\]\r\n]+\])\.m_Entity\b',rb'\1.entitySlot()',raw)
            if n:changes.append('open455entity slot contract')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='addcodebyyun/particlelist.cpp':
                masked=code_only(raw);matches=list(re.finditer(rb'for\s*\(int i=0;i<MaxObj;i\+\+\)\s*\{',masked))
                if len(matches)!=1:raise ValueError('Active particle mesh loop changed')
                at=matches[0].end();nl=b'\r\n' if b'\r\n' in raw else b'\n'
                raw=raw[:at]+nl+b'\t\tif(!pMesh[i].particleSlots())continue; // 455 null effect guard'+raw[at:]
                changes.append('455 current-effect null guard before particle/entity slots')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='addcodebyjang/foreffect.cpp':
                anchor=b'#define GetMega(a)'
                if raw.count(b'g_ChMemoryInfo')!=8 or raw.count(anchor)!=1 or b'characterMemoryInfo' in raw:raise ValueError('Memory diagnostic consumer changed')
                nl=b'\r\n' if b'\r\n' in raw else b'\n'
                raw=raw.replace(anchor,b'const CHMEMORYINFO characterMemoryInfo=RF455_GetCharacterMemoryInfo();'+nl+anchor)
                raw=raw.replace(b'g_ChMemoryInfo',b'characterMemoryInfo')
                changes.append('read confirmed process counters via source-owned memory snapshot')
            # Production modularization, not a test-only copy: the identical
            # methods are removed from their original TU and compiled once here.
            if source.name.lower() in ['global.cpp','cresobject.cpp']:
                unity=source.name.lower()=='global.cpp'
                first=b'CUnityBoneMgr::CUnityBoneMgr()' if unity else b'CAnimation::CAnimation()'
                last=b'_DestroyAnimationMgr( void )' if unity else b'CAnimation::GetRemainEffectFrameNum( void )'
                start,end=section(raw,first,last);body=raw[start:end]
                generated=b'#include "cresobject.h"\n#include "global.h"\n'
                if not unity:generated+=b'#include "client455_animation_timing.h"\n'
                if unity:
                    match=re.search(rb'ChInterface \*\s*g_ifCharIF\s*= NULL;',raw)
                    if not match:raise ValueError('Normal renderer global definition changed')
                    generated+=match[0]+b'\n'
                    # Remove after taking the section, to retain the offsets.
                generated+=body+b'\n';name='unity_managers.cpp' if unity else 'animation_control.cpp'
                destination=root/'generated'/name;save(destination,generated,source,['unchanged production function bodies extracted to separate TU']);split_units.append(destination)
                raw=raw[:start]+b'// Implementations moved to generated/'+name.encode()+b'.\n'+raw[end:]
                if unity:raw=raw[:match.start()]+b'// g_ifCharIF is defined in unity_managers.cpp'+raw[match.end():]
                changes.append('production TU split; extracted method bytes unchanged')
        save(root/'source'/source.relative_to(port/'source/RF_Client'),raw,source,changes)
    tree=ET.parse(WS/'work/client-build/build-character-diagnostic/RF_Online.vcxproj');units=[]
    for node in tree.iter():
        if node.tag.rsplit('}',1)[-1]=='ClCompile' and 'Include' in node.attrib:
            source=Path(node.attrib['Include']);base=WS/'work/client-build/source/RF_Client'
            if source.is_relative_to(base):units.append(root/'source'/source.relative_to(base))
            else:
                target=root/'generated'/source.name;save(target,source.read_bytes(),source);units.append(target)
    if len(units)!=180:raise ValueError('Normal source set changed')
    units+=split_units
    sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text());engine=port/'source/R3Engine'
    directories=[root/'include',root/'source',engine,engine/'extension',engine/'1stclass',engine/'2ndclass',engine/'common',engine/'d3d/include',WS/sdk['include'],native]
    flags=sorted(set(ENGINE_DEFINITIONS+['WIN32','_WINDOWS','_NEW_UI_','RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_EFFECT_LOG','RF_CLIENT_455_LOBBY_TRANSITION','RF_CLIENT_455_FRUSTUM']))
    cmake='cmake_minimum_required(VERSION 3.24)\nproject(RFNormal455 LANGUAGES CXX)\nif(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)\nmessage(FATAL_ERROR "MSVC x86 required")\nendif()\nadd_library(RFClient455Consumers OBJECT\n'+''.join(' "'+p.as_posix()+'"\n' for p in units)+')\n'
    cmake+='target_include_directories(RFClient455Consumers PRIVATE\n'+''.join(' "'+p.as_posix()+'"\n' for p in directories)+')\n'
    cmake+='target_compile_definitions(RFClient455Consumers PRIVATE '+' '.join(flags)+')\ntarget_compile_options(RFClient455Consumers PRIVATE /W3 /O2 /Gy /EHsc /Zc:forScope- /MP4 "/FI'+(port/'port_std.hpp').as_posix()+'")\nset_target_properties(RFClient455Consumers PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES MSVC_RUNTIME_LIBRARY MultiThreaded)\n'
    facade_units=[]
    typing_source=native/'client455_gui_text_typing_board.cpp'
    typing_facade=root/'generated'/typing_source.name
    save(typing_facade,typing_source.read_bytes(),typing_source);facade_units.append(typing_facade)
    controls_source=native/'client455_briefing_controls.cpp'
    controls_facade=root/'generated'/controls_source.name
    save(controls_facade,controls_source.read_bytes(),controls_source);facade_units.append(controls_facade)
    window_source=native/'client455_briefing_window.cpp'
    window_facade=root/'generated'/window_source.name
    save(window_facade,window_source.read_bytes(),window_source);facade_units.append(window_facade)
    intro_camera=native/'client455_tutorial_intro_camera.cpp';intro_camera_facade=root/'generated'/intro_camera.name
    save(intro_camera_facade,intro_camera.read_bytes(),intro_camera);facade_units.append(intro_camera_facade)
    # This TU reads _R3ENGINE_STATE directly;its conditional weather fields must
    # agree with the actual engine and client. Keep unrelated facade TUs unchanged.
    cmake+='set_source_files_properties("'+intro_camera_facade.as_posix()+'" PROPERTIES COMPILE_DEFINITIONS "'+';'.join(ENGINE_DEFINITIONS)+'")\n'
    for name in ['client455_tutorial_intro.cpp','client455_avatar_stage.cpp','client455_normal_facade.cpp','client455_normal_renderer_math.cpp','client455_normal_contracts.cpp','client455_normal_shadow.cpp','client455_normal_effect_tables.cpp','client455_effect_tables.cpp','client455_effects.cpp','client455_normal_effects.cpp','client455_character_clock.cpp','client455_normal_clock.cpp','client455_normal_accounting.cpp','client455_nation_paths.cpp','client455_language.cpp','client455_font_settings.cpp','client455_font.cpp','client455_sprites.cpp','client455_launcher.cpp','client455_bootstrap.cpp','client455_network_state.cpp','client455_network_codec.cpp','client455_connection.cpp','client455_account.cpp','client455_camera.cpp','client455_modal.cpp','client455_text_metrics.cpp','client455_gui_text_metrics.cpp','client455_minimap_opacity.cpp','client455_gui_input.cpp']:
        source=native/name;facade=root/'generated'/name;save(facade,source.read_bytes(),source);facade_units.append(facade)
    for name in ['client455_rvp.cpp','client455_rvp_runtime.cpp','client455_rvp_actor.cpp','client455_normal_rvp.cpp','client455_rvp_effects.cpp','client455_rvp_audio.cpp','client455_money.cpp']:
        source=native/name;facade=root/'generated'/name;save(facade,source.read_bytes(),source);facade_units.append(facade)
        if name in ['client455_rvp_runtime.cpp','client455_rvp_actor.cpp','client455_rvp_effects.cpp','client455_rvp_audio.cpp']:cmake+='set_source_files_properties("'+facade.as_posix()+'" PROPERTIES COMPILE_DEFINITIONS "'+';'.join(ENGINE_DEFINITIONS)+'")\n'
    cmake+='add_library(RFClient455Facade STATIC '+''.join(' "'+p.as_posix()+'"' for p in facade_units)+')\ntarget_include_directories(RFClient455Facade PRIVATE\n'+''.join(' "'+p.as_posix()+'"\n' for p in directories)+')\ntarget_compile_options(RFClient455Facade PRIVATE /W3 /O2 /Gy /EHsc)\nset_target_properties(RFClient455Facade PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES MSVC_RUNTIME_LIBRARY MultiThreaded)\n'
    header_report=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text())['camera_header_overlay'];camera_header=WS/header_report['file']
    if sha(camera_header.read_bytes())!=header_report['sha256']:raise ValueError('Changed owned camera header')
    for target in ['RFClient455Consumers','RFClient455Facade']:
        cmake+='target_compile_options('+target+' PRIVATE "/FI'+(port/'port_std.hpp').as_posix()+'" "/FI'+camera_header.as_posix()+'")\n'
    sources,kernel_evidence=kernel_sources(native);kernel_units=[]
    for source in sources:
        target=root/'generated/kernels'/source.name;save(target,source.read_bytes(),source);kernel_units.append(target)
    cmake+='add_library(RFClient455Kernels STATIC '+''.join(' "'+p.as_posix()+'"' for p in kernel_units)+')\ntarget_include_directories(RFClient455Kernels PRIVATE\n'+''.join(' "'+p.as_posix()+'"\n' for p in directories)+')\ntarget_compile_definitions(RFClient455Kernels PRIVATE _CRT_SECURE_NO_WARNINGS)\ntarget_compile_options(RFClient455Kernels PRIVATE /W3 /O2 /Gy /EHsc /MP4)\nset_target_properties(RFClient455Kernels PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES MSVC_RUNTIME_LIBRARY MultiThreaded)\n'
    save(root/'CMakeLists.txt',cmake.encode());manifest.write_text(json.dumps(records,indent=2)+'\n')
    report={'scope':'Actual180original client sources plus2production TU splits against455records/D3D9;open methods remain undefined','original_sources':180,'sources':len(units),'manifest':manifest.relative_to(WS).as_posix(),'manifest_sha256':sha(manifest.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'record_inputs':{name:sha((native/name).read_bytes()) for name in ['Character455.h','client455_normal_model.inc','client455_normal_mesh.inc','client455_normal_animation.inc','client455_normal_facade.cpp','client455_normal_renderer_math.cpp','client455_normal_renderer_math.h','client455_normal_renderer_constants.h']},'legacy_character_linked':False,'baseline_modified':False,'engine033_modified':False}
    report['canonical_kernel_sources']=[p.relative_to(WS).as_posix() for p in kernel_units];report['kernel_source_reports']=kernel_evidence
    report['record_inputs']['client455_normal_contracts.cpp']=sha((native/'client455_normal_contracts.cpp').read_bytes())
    for name in ['client455_normal_shadow.cpp','client455_normal_shadow.h','client455_normal_shadow_constants.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_normal_effect_tables.cpp','client455_effect_tables.cpp','client455_effect_tables.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_effects.cpp','client455_effects.h','client455_effect_constants.h','client455_normal_effects.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_character_clock.cpp','client455_character_clock.h','client455_normal_clock.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_normal_accounting.cpp','client455_normal_accounting.h','client455_normal_facade.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_nation_paths.cpp','client455_nation_paths.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_language.cpp','client455_language.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_font_settings.cpp','client455_font_settings.h','client455_font.cpp','client455_font.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_sprites.cpp','client455_sprites.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_launcher.cpp','client455_launcher.h','client455_launcher_bridge.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_bootstrap.cpp','client455_bootstrap.h','client455_bootstrap_bridge.inc','client455_network_state.cpp','client455_network_state.h','client455_network_bridge.inc','client455_network_transport.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_network_codec.cpp','client455_network_codec.h','client455_network_config.inc','client455_network_buffer.inc','client455_network_send.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_connection.cpp','client455_connection.h','client455_connection_bridge.inc','client455_network_receipt.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_account.cpp','client455_account.h','client455_account_bridge.inc','client455_account_dispatch.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    report['record_inputs']['client455_progress_loop.inc']=sha((native/'client455_progress_loop.inc').read_bytes())
    for name in ['client455_camera.h','client455_camera.cpp','client455_camera_load.inc','client455_camera_play.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    report['network_defaults']=codec_reference['generated_defaults']
    for name in ['client455_modal.h','client455_modal.cpp','client455_modal_init.inc','client455_modal_message.inc','client455_dialog_input.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_text_metrics.h','client455_text_metrics.cpp','client455_gui_text_size.inc','client455_gui_text_metrics.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_gui_text_board.h','client455_gui_text_board.cpp','client455_gui_text_typing_board.h','client455_gui_text_typing_board.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_briefing_controls.h','client455_briefing_controls.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_briefing_window.h','client455_briefing_window.cpp','client455_screen_message.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_avatar_stage.h','client455_avatar_stage.cpp','client455_avatar_stage.inc','client455_tutorial_dispatch.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    report['record_inputs']['client455_land_load.inc']=sha((native/'client455_land_load.inc').read_bytes())
    for name in ['client455_tutorial_intro.h','client455_tutorial_intro.cpp','client455_tutorial_intro_camera.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_rvp.h','client455_rvp.cpp','client455_rvp_runtime.h','client455_rvp_runtime.cpp','client455_rvp_actor.h','client455_rvp_actor.cpp','client455_normal_rvp.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_rvp_effects.h','client455_rvp_effects.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_rvp_audio.h','client455_rvp_audio.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_money.h','client455_money.cpp','client455_inventory_money.inc','client455_inventory_gold.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    report['record_inputs']['client455_storage.h']=sha((native/'client455_storage.h').read_bytes())
    report['camera_header_overlay']=header_report
    report['tutorial_intro_reference_sha256']=sha((WS/'inventory/client455-tutorial-intro-reference.json').read_bytes())
    for name in ['client455_gui_scrollbar.h','client455_gui_scrollbar.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_minimap_opacity.h','client455_minimap_opacity.cpp','client455_minimap_opacity_owner.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_gui_input.h','client455_gui_input.cpp','client455_gui_input_object.inc','client455_gui_input_container.inc','client455_gui_input_queue.inc']:report['record_inputs'][name]=sha((native/name).read_bytes())
    snapshot=art/'pre-canonical-renderer-gpu.json'
    if not snapshot.exists():snapshot.write_bytes((WS/'inventory/client455-normal-renderer-gpu.json').read_bytes())
    preserved=WS/'inventory/client455-normal-renderer-precanonical.json'
    if not preserved.exists():preserved.write_bytes(snapshot.read_bytes())
    report['precanonical_renderer_sha256']=sha(preserved.read_bytes())
    (WS/'inventory/client455-normal-preparation.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared180originalsources+2production splits;canonical kernel sources:'+str(len(kernel_units)))
if __name__=='__main__':main()
