//663850/6638B0/663910/663960/6639C0 address value fields14..18.
//The public methods retain their source names;full455Avatar metric producers
//and the complete23-field window layout are separate remaining work.
namespace {
int RF455_CharInfoSignedWord(DWORD word){int value;static_assert(sizeof(value)==4,"x86 signedDWORD");std::memcpy(&value,&word,4);return value;}
int RF455_CharInfoTruncatedFloat(float value){
    //The target formats the lowDWORD returned by__ftol2_sse,not a WORD.
    //This is the selected masked/truncating64bit conversion used by conditions.
    DWORD word=0;
    if(std::isfinite(value)&&double(value)>=-9223372036854775808.0&&double(value)<9223372036854775808.0)
        word=static_cast<DWORD>(static_cast<long long>(value));
    return RF455_CharInfoSignedWord(word);
}
}
void CGUICharInfoWindow::SetGenAttackFc(DWORD minimum,DWORD maximum){
    char text[256];std::snprintf(text,sizeof(text),"%d - %d",RF455_CharInfoSignedWord(minimum),RF455_CharInfoSignedWord(maximum));SetInfoText455(14,text);
}
void CGUICharInfoWindow::SetForceAttackFc(DWORD minimum,DWORD maximum){
    //Own bounded storage does not reproduce the target's16-byte stack overflow.
    char text[64];std::snprintf(text,sizeof(text),"%d - %d",RF455_CharInfoSignedWord(minimum),RF455_CharInfoSignedWord(maximum));SetInfoText455(15,text);
}
void CGUICharInfoWindow::SetDeffenceFc(DWORD value){
    char text[16];std::snprintf(text,sizeof(text),"%d",RF455_CharInfoSignedWord(value));SetInfoText455(16,text);
}
void CGUICharInfoWindow::SetHitRate(float value){
    char text[64];std::snprintf(text,sizeof(text),"%.2f",double(value));SetInfoText455(17,text);
}
void CGUICharInfoWindow::SetAvoidRate(float value){
    char text[16];std::snprintf(text,sizeof(text),"%d",RF455_CharInfoTruncatedFloat(value));SetInfoText455(18,text);
}
