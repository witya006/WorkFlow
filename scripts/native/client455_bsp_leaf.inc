short CBsp::GetLeafNum(Vector3f world){
    //4558FAF00:world→local uses the supplied inverse,not a recomputed matrix.
    Vector3fTransform(mTempCamera,world,mInverseWorldMatrix455.m);
    mTempSearchOk=-1;SearchNode(1);return mTempSearchOk;
}
