static bool ReadMagicToken455(RF455ResourceText& input, char (&token)[256])
{
    const bool read = input.read(token);
    if (input.failed()) throw std::runtime_error("455 short MagicTrack stream");
    if (!read) token[0] = '\0';
    return read;
}

static void RequireMagicToken455(RF455ResourceText& input, char (&token)[256])
{
    if (!ReadMagicToken455(input, token) || !_stricmp(token, "end"))
        throw std::runtime_error("455 truncated MagicTrack field");
}

static BOOL GetRandOrNum(RF455ResourceText& input, float* from, float* at)
{
    char token[256];
    RequireMagicToken455(input, token);
    if (std::strncmp(token, "rand", 4)) {
        *from = static_cast<float>(std::atof(token));
        return FALSE;
    }

    while (!std::strchr(token, ')')) {
        char part[256];
        RequireMagicToken455(input, part);
        const auto used = std::strlen(token);
        const auto extra = std::strlen(part);
        if (extra >= sizeof(token) - used)
            throw std::runtime_error("455 overlong MagicTrack rand");
        std::memcpy(token + used, part, extra + 1);
    }

    const char* start = token + 4;
    const char* comma = std::strchr(start, ',');
    const char* close = std::strchr(start, ')');
    if (*start != '(' || !comma || comma <= start + 1 || comma + 1 >= close)
        throw std::runtime_error("455 incomplete MagicTrack rand");

    const DWORD consumed = GetTokenFloat(token, from);
    GetTokenFloat(token + consumed, at);
    return TRUE;
}
