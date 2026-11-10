// Pinned4557B4670/4760/4960/49F0. Target private44byte records become source owners.
#undef min
#undef max
CGUIMoveObjectMgr::CGUIMoveObjectMgr(){}
CGUIMoveObjectMgr::~CGUIMoveObjectMgr(){RemoveAllObject();}
void CGUIMoveObjectMgr::AddMoveObject(CGUIObject* object,MoveAxis axis,int from,int to,DWORD duration,BYTE waves,WORD wavelength){AddMoveObject455(object,axis,from,to,float(duration),-1.0f,waves,wavelength);}
void CGUIMoveObjectMgr::AddMoveObject455(CGUIObject* object,MoveAxis axis,int from,int to,float velocity,float acceleration,BYTE waves,WORD wavelength){
    if(!object||!std::isfinite(velocity)||!std::isfinite(acceleration)||velocity<0||double(velocity)>=4294967296.0)throw std::invalid_argument("455 GUI movement domain not admitted");
    auto* entry=GetMoveObject(object);if(!entry)entry=GetMoveFinishedObject();if(!entry){entry=new MoveObjectInfo;m_listMoveObj.push_back(entry);}*entry={};
    entry->pObject=object;entry->eAxis=axis;entry->nInitPos=from;entry->nLastPos=to;entry->byWaveCnt=waves;entry->wMaxWaveLength=wavelength;entry->fAcceleration=acceleration;
    if(acceleration==-1.0f)entry->dwVelocity=DWORD(velocity);else entry->fInitialVelocity=velocity;
}
void CGUIMoveObjectMgr::StartMove(CGUIObject* object){StartMoveAt455(object,timeGetTime());}
void CGUIMoveObjectMgr::StartMoveAt455(CGUIObject* object,DWORD now){
    auto* entry=GetMoveObject(object);if(!entry)return;if(entry->eAxis==MOVE_AXIS_X)object->SetPos(entry->nInitPos,object->GetPosY());else object->SetPos(object->GetPosX(),entry->nInitPos);
    entry->byCurWaveCnt=0;const int overshoot=int(entry->byWaveCnt)*entry->wMaxWaveLength;entry->nMidPos=entry->nLastPos+(entry->nLastPos>entry->nInitPos?overshoot:-overshoot);entry->dwMoveStartTime=now;
}
void CGUIMoveObjectMgr::RemoveObject(CGUIObject* object){for(auto it=m_listMoveObj.begin();it!=m_listMoveObj.end();++it)if((*it)->pObject==object){delete *it;m_listMoveObj.erase(it);return;}}
void CGUIMoveObjectMgr::RemoveAllObject(){for(auto* entry:m_listMoveObj)delete entry;m_listMoveObj.clear();}
BOOL CGUIMoveObjectMgr::IsFinishedMove(CGUIObject* object){auto* entry=GetMoveObject(object);return entry?entry->bIsFinished:TRUE;}
void CGUIMoveObjectMgr::FrameMove(){FrameMoveAt455(timeGetTime());}
void CGUIMoveObjectMgr::FrameMoveAt455(DWORD now){
    const float halfPi=1.5707963705062866f; // BDD2A8 bytesDB0FC93F.
    for(auto* entry:m_listMoveObj){if(entry->bIsFinished||!entry->dwMoveStartTime)continue;
        const int direction=entry->nMidPos>entry->nInitPos?1:-1;int position;
        if(entry->fAcceleration>=0){const float seconds=float(double(DWORD(now-entry->dwMoveStartTime))*double(0.001f));position=int(double(entry->nInitPos)+double(direction)*entry->fInitialVelocity*seconds+double(direction)*0.5*entry->fAcceleration*std::pow(double(seconds),2.0));}
        else{const float angle=entry->dwVelocity?float(double(DWORD(now-entry->dwMoveStartTime))*double(halfPi)/double(entry->dwVelocity)):halfPi;
            if(double(angle)>=double(halfPi))position=entry->nMidPos;else{const float sine=float(std::sin(double(angle)));position=int(double(entry->nMidPos-entry->nInitPos)*double(sine)+double(entry->nInitPos));}}
        const bool finished=(direction>0&&position>=entry->nMidPos)||(direction<0&&position<=entry->nMidPos);if(finished)position=entry->nMidPos;
        if(entry->eAxis==MOVE_AXIS_X)entry->pObject->SetPos(position,entry->pObject->GetPosY());else entry->pObject->SetPos(entry->pObject->GetPosX(),position);
        if(finished){if(entry->byWaveCnt&&++entry->byCurWaveCnt<=entry->byWaveCnt){entry->nInitPos=position;const int amount=(int(entry->byWaveCnt)-entry->byCurWaveCnt)*entry->wMaxWaveLength;entry->nMidPos=entry->nLastPos+((entry->byCurWaveCnt&1)?-amount:amount);entry->dwMoveStartTime=now;}else entry->bIsFinished=TRUE;}
    }
}
MoveObjectInfo* CGUIMoveObjectMgr::GetMoveObject(CGUIObject* object){for(auto* entry:m_listMoveObj)if(entry->pObject==object)return entry;return nullptr;}
MoveObjectInfo* CGUIMoveObjectMgr::GetMoveFinishedObject(){for(auto* entry:m_listMoveObj)if(entry->bIsFinished)return entry;return nullptr;}
CGUIMoveObjectMgr g_cMoveObjectMgr;
