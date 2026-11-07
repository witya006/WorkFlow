    // Source-owned455 metadata/grade frame;not the complete privateGUIItem ABI.
    DWORD m_objectIndex455=0xffffffff;
    BYTE m_grade455=0;
    BOOL m_typedIcon455=FALSE,m_gradeFrameVisible455=TRUE;
    BYTE m_ownerContext455=0;
    CGUIObject m_gradeFrame455;
    RF455GuiTimer m_timer455;
    BOOL DrawTypedIcon455(RECT*);
    void SetTypedSprite455();
    void SetNum455(WORD);
    void SetUsable455(BYTE);
public:
    RF455GuiTimer& Timer455(){return m_timer455;}
    void BeginDelayAnimation455(DWORD,LONG elapsed=-1);
    void StopDelayAnimation455();
    void ResetTimerOnEmpty455(){if(m_timer455.IsStarted455())m_timer455.Reset455();}
    BOOL DrawTimerLabel455(RECT*);
    void Update()override;
    void SetObjectIndex455(DWORD index,BOOL typed=TRUE){m_objectIndex455=index;if(typed){m_typedIcon455=TRUE;m_bySpriteSize=64;}}
    DWORD GetObjectIndex455()const{return m_objectIndex455;}
    void SetGrade455(BYTE grade);
    BYTE GetGrade455()const{return m_grade455;}
    void SetGradeFrameColor455(DWORD color){m_gradeFrame455.SetARGB(color);}
    DWORD GetGradeFrameColor455(){return m_gradeFrame455.GetARGB();}
    void ShowGradeFrame455(BOOL visible){m_gradeFrameVisible455=visible;}
    void SetIconType455(BYTE type){m_typedIcon455=TRUE;m_byIconType=type;m_bySpriteSize=64;}
    BOOL UsesTypedIcon455()const{return m_typedIcon455;}
    void SetOwnerContext455(BYTE context){m_ownerContext455=context;}
    BYTE GetOwnerContext455()const{return m_ownerContext455;}
    void SetPos(LONG,LONG) override;
    void SetPos(POINT& point) override{SetPos(point.x,point.y);}
    virtual void SetSize(LONG,LONG);
    virtual void SetSize(POINT& point){SetSize(point.x,point.y);}
