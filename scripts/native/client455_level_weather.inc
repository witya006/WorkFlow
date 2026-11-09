//4558E77B0/8EA690:the map owner retains the DWORD before updating global fog
//exposure. Typed virtual dispatch permits the separate INS/Planet overrides.
void CLevel::SetWeatherColor455(DWORD color){
    mWeatherColor455=color;
    RF455_SetSkyFogExposureColor(color);
}
