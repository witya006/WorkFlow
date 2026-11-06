static std::uint32_t st455RequestedMovieState=0;
void RF455_SetMovieState(std::uint32_t value){
    st455RequestedMovieState=value;
    stRTMovieFlag=(stRTMovieFlag&~7u)|(value&7u);
    GetR3State()->mWideOn=(value&RF455_MOVIE_WIDE)?TRUE:FALSE;
    GetR3State()->mIsDrawLogo=(value&RF455_MOVIE_LOGO)?TRUE:FALSE;
    if(value&RF455_MOVIE_NO_CAMERA)SetDefaultFov();
}
std::uint32_t RF455_GetMovieState(){return stRTMovieFlag;}
void RF455_AddMovieFlags(std::uint32_t value){stRTMovieFlag|=value;}
void RF455_RemoveMovieFlags(std::uint32_t value){stRTMovieFlag&=~value;}
std::uint32_t RF455_GetRequestedMovieState(){return st455RequestedMovieState;}

// The legacy0.7 request API is explicitly separate from the positive455 flags.
// It stays available to existing source consumers while their stages migrate.
static DWORD st455LegacyMovieRequest=0;
void RTMovieSetState(DWORD value){
    st455LegacyMovieRequest=value;
    RF455_SetMovieState(((value&RTM_STATE_NO_WIDE)?0u:RF455_MOVIE_WIDE)|
        ((value&RTM_STATE_NO_LOGO)?0u:RF455_MOVIE_LOGO)|
        ((value&RTM_STATE_NO_CAMERAMOVE)?RF455_MOVIE_NO_CAMERA:0u));
}
DWORD RTMovieGetState(){return st455LegacyMovieRequest;}
