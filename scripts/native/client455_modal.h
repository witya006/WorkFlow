#pragma once
class CGUIButton;
class CGUIButtonEx;
class CGUIScrollbar;
void RF455_ConfigureModalButton(CGUIButton&, bool closeButton = false);
void RF455_ConfigureModalCaption(CGUIButtonEx&, unsigned languageIndex);
void RF455_ConfigureModalScrollbar(CGUIScrollbar&);
bool RF455_ModalChatInputFocused();
