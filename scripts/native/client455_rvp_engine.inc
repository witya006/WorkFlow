BOOL IsLoadedRTMovie(){return RF455_RvpView().movieLoaded?TRUE:FALSE;}
BOOL IsLoadedRTCamera(){return RF455_RvpView().cameraLoaded?TRUE:FALSE;}
void RTMovieCreate(char* name,CLevel* level){RF455_RvpCreate(name,level);}
void RTMovieRelease(){RF455_RvpRelease();}
void RTMovieFrameMove(){RF455_RvpFrameMove();}
void RTMovieRender(){RF455_RvpRender();}
void RTMovieStartPlay(BOOL restart){RF455_RvpStart(restart!=FALSE);}
void RTMoviePause(BOOL paused){RF455_RvpPause(paused!=FALSE);}
BOOL IsRTMoviePlaying(){return RF455_RvpView().playing?TRUE:FALSE;}
void RTMoiveGetCameraPos(Vector3f output){Vector3fCopy(R3MoveGetViewMatrix()->m[3],output);}
void RTMoiveGetCameraMatrix(float output[4][4]){memcpy(output,R3MoveGetViewMatrix()->m,64);}
