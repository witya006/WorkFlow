#pragma once
#include <cstdint>
class CGUIText;
long RF455_TextWidth(const char*,std::uint16_t bytes=0xffff);
int RF455_TextFitBytes(const char*,int maximumWidth);
int RF455_DefaultTextHeight();
void RF455_UpdateGuiTextSize(CGUIText*);
void RF455_ForgetGuiText(CGUIText*);
