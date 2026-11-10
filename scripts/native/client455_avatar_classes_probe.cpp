#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemdata.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/guicharinfowindow.h"
#include "mainapp.h"
#include "client455_client_items.h"
#include "client455_character_tables.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
static unsigned word(FILE* file){unsigned n=0;require(std::fread(&n,4,1,file)==1,"Expected word");return n;}
static unsigned crc(const void* raw,std::size_t size){
    unsigned value=0xffffffff;const auto* p=static_cast<const unsigned char*>(raw);
    for(std::size_t i=0;i<size;++i){value^=p[i];for(unsigned j=0;j<8;++j)value=(value>>1)^((value&1)?0xedb88320:0);}return value^0xffffffff;
}
struct Entry{unsigned index;char code[32],name[32];};
static_assert(sizeof(Entry)==68,"Oracle entry");
struct ProbeAvatar:CAvatar{using CAvatar::SetClassName;using CAvatar::GetInitialClassIndex455;};
static const char* value(CGUICharInfoWindow& ui,unsigned slot){auto* field=ui.GetInfoValue455(BYTE(slot));return field&&field->GetString()?field->GetString():"";}
static void names(CAvatar& avatar,CGUICharInfoWindow& ui,const char* base,const char* advanced){
    require(!std::strcmp(avatar.GetClassName(),base)&&!std::strcmp(value(ui,5),base)&&!std::strcmp(value(ui,4),advanced),"Actual stored/UI class names");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    FILE* f=std::fopen("expected.bin","rb");require(f,"Expected file");char magic[4];require(std::fread(magic,1,4,f)==4&&!std::memcmp(magic,"AC44",4),"Expected signature");
    unsigned count=word(f),stride=word(f),expectedCrc=word(f);require(count==165,"Real class count");std::vector<Entry> entries(count);
    require(std::fread(entries.data(),sizeof(Entry),count,f)==count&&std::fgetc(f)==EOF,"Expected complete class entries");std::fclose(f);
    require(RF455_InitializeNationPaths(),"Nation paths");InitR3Engine();
    auto* oldManager=g_pCharDataMgr;auto* oldUi=g_pUiCharInfoWindow;
    CCharacterDataMgr manager;g_pCharDataMgr=&manager;RF455CharacterTables loader;require(loader.loadCharacterFiles(RF455_GameItems().data),"Real Character and localized class tables");
    const auto& table=RF455_GameItems().data.characterTables()[0];require(table.count==count&&table.stride==stride&&crc(table.bytes.data(),table.bytes.size())==expectedCrc,"All class bytes match independent oracle");
    require(!_GetSkillBoard(),"This Login-class scenario has no registered gameplay skill board");g_pUiCharInfoWindow=nullptr;
    {
        ProbeAvatar avatar;
        for(auto& e:entries){avatar.SetClassDTIndexByStrDTCode(0,e.code);require(avatar.GetClassDTIndex(0)==e.index&&avatar.GetClassName()[0]==0,"All real classes apply to actual Avatar without UI");}
        require(avatar.GetClassDTIndex(1)==ID_INVALID&&avatar.GetClassDTIndex(4)==ID_INVALID&&avatar.GetClassDTIndex(255)==ID_INVALID&&avatar.GetClassLevel()==0&&avatar.IsChangableClass(),"Initial class getters/bounds/change availability");
    }
    {
        std::unique_ptr<CGUICharInfoWindow> ui(new CGUICharInfoWindow);g_pUiCharInfoWindow=ui.get();ProbeAvatar avatar;
        ui->m_uiCharInfo[CGUICharInfoWindow::Level].SetString("legacy-level");ui->m_uiCharInfo[CGUICharInfoWindow::Guild].SetString("legacy-guild");ui->m_uiCharInfo[CGUICharInfoWindow::Attr].SetString("legacy-attribute");
        ui->SetInfoText455(4,"advanced-sentinel");avatar.SetClassName("base-sentinel");
        avatar.SetClassDTIndex(0,entries[0].index);names(avatar,*ui,"base-sentinel",entries[0].name);
        avatar.SetClassDTIndexByStrDTCode(0,entries[1].code);names(avatar,*ui,entries[1].name,entries[1].name);
        avatar.SetClassDTIndex(1,entries[2].index);names(avatar,*ui,entries[1].name,entries[2].name);
        require(avatar.GetInitialClassIndex455()==entries[2].index&&avatar.GetClassLevel()==1,"First profession becomes initial class");
        avatar.SetClassDTIndex(0,entries[3].index);names(avatar,*ui,entries[3].name,entries[2].name);
        avatar.SetClassDTIndexByStrDTCode(1,entries[4].code);names(avatar,*ui,entries[3].name,entries[4].name);
        avatar.SetClassDTIndex(2,entries[5].index);avatar.SetClassDTIndexByStrDTCode(3,entries[6].code);names(avatar,*ui,entries[3].name,entries[4].name);
        require(avatar.GetClassLevel()==3&&!avatar.IsChangableClass(),"All three profession slots counted");
        const unsigned prior[4]={entries[3].index,entries[4].index,entries[5].index,entries[6].index};
        avatar.SetClassDTIndex(4,17);avatar.SetClassDTIndex(255,18);avatar.SetClassDTIndexByStrDTCode(4,entries[0].code);
        avatar.SetClassDTIndexByStrDTCode(0,nullptr);avatar.SetClassDTIndexByStrDTCode(0,"!missing!");
        for(unsigned i=0;i<4;++i)require(avatar.GetClassDTIndex(BYTE(i))==prior[i],"Invalid inputs leave indices unchanged");
        names(avatar,*ui,entries[3].name,entries[4].name);
        avatar.SetClassDTIndex(1,ID_INVALID);names(avatar,*ui,entries[3].name,entries[4].name);
        require(avatar.GetInitialClassIndex455()==entries[3].index&&avatar.GetClassLevel()==2&&avatar.IsChangableClass(),"Cleared first profession falls back to class0");
        g_pUiCharInfoWindow=nullptr;avatar.SetClassDTIndexByStrDTCode(0,entries[0].code);require(avatar.GetClassDTIndex(0)==entries[0].index,"UI absent still writes index");names(avatar,*ui,entries[3].name,entries[4].name);
        g_pUiCharInfoWindow=ui.get();avatar.SetClassDTIndex(0,entries[0].index);names(avatar,*ui,entries[3].name,entries[0].name);
        avatar.SetClassDTIndex(0,0xdeadbeef);require(avatar.GetClassDTIndex(0)==0xdeadbeef,"Numeric setter accepts unknown index");names(avatar,*ui,entries[3].name,entries[0].name);
        char longName[48];std::memset(longName,'X',47);longName[47]=0;avatar.SetClassName(longName);
        require(std::strlen(avatar.GetClassName())==31&&avatar.GetClassName()[31]==0&&!std::strcmp(value(*ui,5),avatar.GetClassName()),"Copy truncates to31 and terminates");
        avatar.SetClassName("Q");require(avatar.GetClassName()[0]=='Q',"Short copy");for(unsigned i=1;i<32;++i)require(avatar.GetClassName()[i]==0,"Whole32byte destination zeroed");
        avatar.SetClassName(nullptr);require(!std::strcmp(avatar.GetClassName(),"Q"),"Null name leaves destination unchanged");
        ui->SetInfoText455(22,"last-field");ui->SetInfoText455(23,"ignored");ui->SetInfoText455(255,"ignored");
        require(!std::strcmp(value(*ui,22),"last-field")&&!ui->GetInfoValue455(23)&&!ui->GetInfoValue455(255),"23-field bounds");
        require(!std::strcmp(ui->m_uiCharInfo[CGUICharInfoWindow::Level].GetString(),"legacy-level")&&!std::strcmp(ui->m_uiCharInfo[CGUICharInfoWindow::Guild].GetString(),"legacy-guild")&&!std::strcmp(ui->m_uiCharInfo[CGUICharInfoWindow::Attr].GetString(),"legacy-attribute"),"Class writers preserve legacy Level/Guild/Attribute widgets");
        g_pUiCharInfoWindow=nullptr;
    }
    g_pCharDataMgr=oldManager;g_pUiCharInfoWindow=oldUi;
    FILE* out=std::fopen("result.json","wb");require(out,"Output");std::fputs("{\"status\":\"PASS\",\"actual_Avatar\":true,\"class_rows\":165,\"all_class_bytes\":true,\"numeric_string_setter_difference\":true,\"ui_absent_retains_names\":true,\"class23_text_owner\":true,\"legacy_fields_preserved\":true,\"class_skill_callback_tested\":false,\"full_layout_equipment_selection\":false}\n",out);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Avatar classes: %s\n",error.what());return 2;}}
