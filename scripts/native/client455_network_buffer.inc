struct _NET_BUFFER
{
    DWORD m_capacity=0,m_extra=0,m_dwPopRot=0,m_dwPopPnt=0,m_dwPushRot=0,m_dwPushPnt=0;
    char* m_sMainBuffer=nullptr;
    CNetCriticalSection m_csPush,m_csPop;
    char* m_sTempBuffer=nullptr; // shared process scratch,borrowed
    _NET_BUFFER()=default;
    ~_NET_BUFFER(){delete[]m_sMainBuffer;}
    bool Configure(DWORD capacity,DWORD extra,char* scratch){
        if(m_sMainBuffer||!capacity||!extra||!scratch)return false;
        auto* data=new(std::nothrow)char[static_cast<std::size_t>(capacity)+extra];if(!data)return false;
        m_capacity=capacity;m_extra=extra;m_sMainBuffer=data;m_sTempBuffer=scratch;Init();return true;
    }
    void Init(){m_csPush.Lock();m_dwPushRot=m_dwPushPnt=0;m_csPush.Unlock();m_csPop.Lock();m_dwPopRot=m_dwPopPnt=0;m_csPop.Unlock();}
    char* GetPushPos(){return m_sMainBuffer+m_dwPushPnt;}
    char* GetPopPos(){return m_sMainBuffer+m_dwPopPnt;}
    DWORD GetTotalPush(){m_csPush.Lock();DWORD n=m_dwPushRot*m_capacity+m_dwPushPnt;m_csPush.Unlock();return n;}
    DWORD GetTotalPop(){m_csPop.Lock();DWORD n=m_dwPopRot*m_capacity+m_dwPopPnt;m_csPop.Unlock();return n;}
    void AddPushPos(DWORD size){m_csPush.Lock();DWORD next=m_dwPushPnt+size;if(next>=m_capacity){++m_dwPushRot;next%=m_capacity;}m_dwPushPnt=next;m_csPush.Unlock();}
    void AddPopPos(DWORD size){m_csPop.Lock();DWORD next=m_dwPopPnt+size;if(next>=m_capacity){++m_dwPopRot;next%=m_capacity;}m_dwPopPnt=next;m_csPop.Unlock();}
    char* GetPopPoint(bool* missing,bool encrypted=false){
        const DWORD available=GetTotalPush()-GetTotalPop();*missing=false;if(!available)return nullptr;
        const unsigned header=encrypted?3:2;if(available<header){*missing=true;return nullptr;}
        WORD size=static_cast<BYTE>(m_sMainBuffer[m_dwPopPnt])|(static_cast<WORD>(static_cast<BYTE>(m_sMainBuffer[(m_dwPopPnt+1)%m_capacity]))<<8);
        if(size<header||size>m_capacity||size>m_extra||size>available){*missing=true;return nullptr;}
        if(m_dwPopPnt+size<=m_capacity)return m_sMainBuffer+m_dwPopPnt;
        DWORD first=m_capacity-m_dwPopPnt;memcpy(m_sTempBuffer,m_sMainBuffer+m_dwPopPnt,first);memcpy(m_sTempBuffer+first,m_sMainBuffer,size-first);return m_sTempBuffer;
    }
    char* GetSendPoint(int* size,bool* missing){
        const DWORD available=GetTotalPush()-GetTotalPop();*size=static_cast<int>(available);*missing=false;if(!available)return nullptr;
        if(available>m_capacity){*missing=true;return nullptr;}if(m_dwPopPnt+available<=m_capacity)return m_sMainBuffer+m_dwPopPnt;
        if(available>m_extra){*missing=true;return nullptr;}DWORD first=m_capacity-m_dwPopPnt;
        memcpy(m_sTempBuffer,m_sMainBuffer+m_dwPopPnt,first);memcpy(m_sTempBuffer+first,m_sMainBuffer,available-first);return m_sTempBuffer;
    }
};
static_assert(sizeof(_NET_BUFFER)==80,"455ring buffer layout must stay80bytes onx86");
