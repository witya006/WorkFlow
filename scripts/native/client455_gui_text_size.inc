CGUIText::SetString(char* text)
{
    m_sTextInfo.SetText(text);
    RF455_UpdateGuiTextSize(this);
}
