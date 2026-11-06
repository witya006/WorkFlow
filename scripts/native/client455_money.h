#pragma once
#if !defined(_M_IX86)
#error RF455 money conversion requires the measured x86 floating-point route
#endif
void RF455_FormatMoney(__int64 value,char* destination);
char* RF455_GetMoneyText(__int64 value);
