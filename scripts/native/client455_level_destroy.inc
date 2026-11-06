CLevel::~CLevel(){
    // Target8EA120 calls ReleaseLevel before destroying sky/BSP owners.
    ReleaseLevel();delete mSkyBox;delete mBsp;
}
