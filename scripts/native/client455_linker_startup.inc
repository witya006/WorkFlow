// MainGame455 RVA147832..1478CB, x86/base400000, both pinned clients.
// The complete board factory and later MainGame bindings are separate work.
void CLinkBoard::InitializeMainGame455()
{
    Create(6, 5, 10);
    InitWindow(3, 400, 500);
    for (BYTE bank = 0; bank < 5; ++bank)
        AddPack(bank);
    OpenWindow();
}
