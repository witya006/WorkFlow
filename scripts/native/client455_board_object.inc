// Actual source-owned wrapper,not a cast of the old mixed payload objects.
class CBoardObject:public CItemObject {
protected:
    BYTE m_bIsUsing;
    CGUIItem* m_uiIcon;
    unsigned char m_boardFields600455[17];
public:
    CBoardObject();
    CBoardObject(const CBoardObject&);
    virtual ~CBoardObject();
    void Clear() override;
    void SetItem455(RF455ManagedItem*) override;
    void SetIndex(DWORD) override;
    BOOL IsEqual(DWORD index);
    virtual BOOL IsEqual(CBoardObject*);
    virtual CBoardObject* New();
    virtual CBoardObject* Clone();
    void Copy455(const CBoardObject*);
    virtual BOOL IsEqualItemType(BYTE kind){return GetItemType()==kind;}
    // Compatibility discriminator for the still-unported mixed derived classes.
    // Base455 wrapper returns0;payload kind is GetItem455()->header().kind.
    virtual BYTE GetItemType(){return BOT_BASE;}
    void SetUsingState(BOOL value){m_bIsUsing=static_cast<BYTE>(value);}
    BOOL IsUsing(){return m_bIsUsing;}
    void SetIcon(CGUIItem*);
    virtual CGUIItem* GetIcon(){return m_uiIcon;}
    void BeginDelayAnimation(DWORD);
    void RefreshIcon455();
    void RefreshLock455();
};
static_assert(sizeof(CBoardObject)==620,"455 typed board wrapper");
