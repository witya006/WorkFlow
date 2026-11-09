public:
    // Own class storage;does not overlay the original CBsp's private offsets.
    void SetWorldMatrices455(const void* world,const void* inverse){
        memcpy(&mWorldMatrix455,world,64);memcpy(&mInverseWorldMatrix455,inverse,64);
    }
    const D3DXMATRIX& WorldMatrix455()const{return mWorldMatrix455;}
    const D3DXMATRIX& InverseWorldMatrix455()const{return mInverseWorldMatrix455;}
private:
    D3DXMATRIX mWorldMatrix455,mInverseWorldMatrix455;
public:
