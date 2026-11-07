#include "client455_image_text.h"
#include "userinterface/spritemgr.h"
#include <cstring>
#include <stdexcept>

BYTE CGUIImageText455::glyph(BYTE c,LONG width,LONG imageWidth){
    unsigned index;
    if(c>='0'&&c<='9')index=c-'0';
    else switch(c){case '%':index=10;break;case '.':index=11;break;case '/':index=12;break;
        case ':':index=13;break;case 'A':index=14;break;case 'P':index=15;break;
        case 'M':case '-':index=16;break;case '+':index=17;break;case ',':index=18;break;default:return 255;}
    return static_cast<LONG>(static_cast<DWORD>(width)*(index+1))<=imageWidth?static_cast<BYTE>(index):BYTE(255);
}
void CGUIImageText455::Configure455(BYTE id,WORD action,WORD frame,LONG width,LONG height){
    auto* sprite=gSpriteMgr.GetTargetSprite455(id);
    if(!sprite||action>=sprite->GetMaxActions()||frame>=sprite->GetMaxFrames(action))throw std::runtime_error("455 image-text sprite reference missing");
    SPRITE_INFO reference={sprite,action,frame};SetSpriteInfo(&reference);
    const auto original=sprite->GetSpriteOrgXL(action,frame);
    if(!original)throw std::runtime_error("455 image-text zero-width configuration outside admitted domain");
    const float fraction=static_cast<float>(double(width)/original);SetSpriteU(0,fraction);SetSpriteV(0,1);
    stepU=m_fSpriteUV[0][1]-m_fSpriteUV[0][0];stepV=m_fSpriteUV[1][1]-m_fSpriteUV[1][0];
    cellWidth=width;cellHeight=height;SetSize(width*static_cast<WORD>(glyphs.size()),height);
}
void CGUIImageText455::SetString455(const char* text){
    const auto length=static_cast<WORD>(text?std::strlen(text):0);glyphs.resize(length);
    auto* sprite=GetSpriteInfo()->pSprite;const LONG width=sprite?sprite->GetSpriteOrgXL(GetSpriteInfo()->wActionNo,GetSpriteInfo()->wFrameNo):0;
    for(WORD i=0;i<length;++i)glyphs[i]=glyph(static_cast<BYTE>(text[i]),cellWidth,width);
    SetSize(cellWidth*length,cellHeight);
}
BOOL CGUIImageText455::Draw(){
    auto* sprite=GetSpriteInfo()->pSprite;if(!IsShow()||!sprite||glyphs.empty())return FALSE;
    sprite->SetAction(GetSpriteInfo()->wActionNo);sprite->SetFrame(GetSpriteInfo()->wFrameNo);LONG x=m_ptPos.x;
    for(BYTE index:glyphs){if(index!=255){m_fSpriteUV[0][0]=static_cast<float>(double(index)*stepU);m_fSpriteUV[0][1]=m_fSpriteUV[0][0]+stepU;
        sprite->DrawSpriteUV(x,m_ptPos.y,m_fSpriteUV,x+cellWidth,m_ptPos.y+cellHeight,GetARGB());}x+=cellWidth;}return TRUE;
}
BOOL CGUIImageText455::Draw(RECT& clip){
    auto* sprite=GetSpriteInfo()->pSprite;if(!IsShow()||!sprite||glyphs.empty())return FALSE;
    sprite->SetAction(GetSpriteInfo()->wActionNo);sprite->SetFrame(GetSpriteInfo()->wFrameNo);
    m_fSpriteUV[1][0]=static_cast<float>(double(clip.top-m_ptPos.y)*stepV/m_ptSize.y);
    m_fSpriteUV[1][1]=static_cast<float>(double(clip.bottom-m_ptPos.y)*stepV/m_ptSize.y);
    for(std::size_t i=0;i<glyphs.size();++i){const BYTE index=glyphs[i];if(index==255)continue;
        m_fSpriteUV[0][0]=static_cast<float>(double(index)*stepU);m_fSpriteUV[0][1]=m_fSpriteUV[0][0]+stepU;
        LONG x=m_ptPos.x+static_cast<LONG>(i)*cellWidth,right=x+cellWidth;
        if(clip.left>x){if(clip.left>right)continue;m_fSpriteUV[0][0]=static_cast<float>(double(clip.left-x)*stepU+m_fSpriteUV[0][0]);x=clip.left;}
        if(clip.right<right){if(clip.right<x)continue;
            //642B50 uses stepV and the adjusted left edge here. Preserve the
            //observed formula instead of substituting ideal clipping math.
            m_fSpriteUV[0][1]=static_cast<float>(m_fSpriteUV[0][1]-double(x-clip.right)*stepV);right=clip.right;}
        sprite->DrawSpriteUV(x,clip.top,m_fSpriteUV,right,clip.bottom,GetARGB());
    }return TRUE;
}
