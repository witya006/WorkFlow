namespace {
bool CanReadLevel455(const char* name)
{
    const auto length = name ? strnlen_s(name, 256) : 0;
    if (length <= 4 || length >= 256 || _stricmp(name + length - 4, ".bsp"))
        return false;
    std::unique_ptr<FILE, decltype(&std::fclose)> input(std::fopen(name, "rb"), std::fclose);
    if (!input) return false;

    // CLevel::LoadLevel opens the supplied file, then loads the BSP from
    // the engine's MapPath using the supplied filename's basename.
    char base[256];
    std::memcpy(base, name, length + 1);
    StripEXT(base);
    StripPath(base);
    char bsp[256];
    const int pathLength = std::snprintf(bsp, sizeof bsp, "%s%s\\%s.bsp",
                                         GetR3State()->MapPath, base, base);
    if (!*base || pathLength <= 0 || static_cast<std::size_t>(pathLength) >= sizeof bsp) return false;
    input.reset(std::fopen(bsp, "rb"));
    if (!input) return false;

    _BSP_FILE_HEADER header{};
    if (std::fread(&header, sizeof header, 1, input.get()) != 1 ||
        header.version != _R3BSP_VERSION || !header.Node.size || !header.Leaf.size)
        return false;

    // The BSP reader consumes these records in file order. Exporters can
    // leave stale offsets, so compare the consumed extent with the file.
    const DWORD sectionSizes[] = {
        header.CPlanes.size, header.CFaceId.size, header.Node.size, header.Leaf.size,
        header.MatListInLeaf.size, header.Object.size, header.Track.size,
        header.EventObjectID.size, header.BVertex.size, header.WVertex.size,
        header.FVertex.size, header.VertexColor.size, header.UV.size, header.LgtUV.size,
        header.Face.size, header.FaceId.size, header.VertexId.size, header.ReadMatGroup.size,
    };
    unsigned long long required = sizeof header;
    for (DWORD size : sectionSizes) required += size;
    for (const auto& entry : header.ReadSpare) required += entry.size;
    if (_fseeki64(input.get(), 0, SEEK_END)) return false;
    const auto bytes = _ftelli64(input.get());
    return bytes >= 0 && required <= static_cast<unsigned long long>(bytes);
}
}

bool CLand::CanLoadMap455(BYTE index) const
{
    if (!m_pLevel || !m_maps455.maps || index >= m_maps455.count) return false;
    const auto& name = m_maps455.maps[index].pFileName;
    return std::memchr(name, '\0', sizeof name) && CanReadLevel455(name);
}
