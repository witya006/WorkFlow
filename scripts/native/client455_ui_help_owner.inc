#include "client455_nation_paths.h"
#include "client455_ui_help.h"

namespace {
std::string uiHelpPath455()
{
    const char* root = RF455_GetClientDataRoot();
    return root && *root ? std::string(root) + "\\UIHelp.edf" : std::string();
}

void assignUiHelp455(HSD_HELP& target, const RF455UiHelpPage& page)
{
    target.m_dwID = page.id;
    target.m_dwWindowID = page.window;
    target.m_dwSectionID = page.section;
    target.m_byTotalStringNum = static_cast<BYTE>(page.fragments.size());
    target.m_listString = new HSD_STRING[page.fragments.size()];
    for (std::size_t i = 0; i < page.fragments.size(); ++i) {
        const auto& source = page.fragments[i];
        auto& destination = target.m_listString[i];
        static_assert(sizeof(HSD_FONT) == 12, "455 UIHelp font record");
        std::memcpy(&destination.m_stFont, source.font.data(), source.font.size());
        destination.m_wLength = static_cast<WORD>(source.text.size());
        destination.m_pString = new char[source.text.size() + 1];
        std::memcpy(destination.m_pString, source.text.c_str(), source.text.size() + 1);
    }
}
}
