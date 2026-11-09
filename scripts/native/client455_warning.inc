void Warning(char* message,char* context){
    if(No_warning)return;
    char buffer[256];strcpy(buffer,message);strcat(buffer,context);
    if(WarningMessageProc){
        //4558F1160 loads the7 bytes atB39258: "<-" + CP949 warning label.
        strcat(buffer,"\x3c\x2d\xb0\xe6\xb0\xed");
        WarningMessageProc(buffer);
    }
}
