"""Check the generated CDataFile methods against one pinned EDF and failed reloads."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

from client455_edf_file_port import edf_file_definitions, port_edf_file
from prepare_client455_normal import section
from workspace_guard import ROOT, require_budget


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    require_budget()
    work = ROOT / 'work/recovered/client455/resource-cache/edf'
    work.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'work/client455-port/source/RF_Client'
    cpp = source / 'datafile.cpp'
    header = source / 'datafile.h'
    native = ROOT / 'scripts/native'
    client_bin = ROOT / 'work/client455-port/normal/build/RF_Online.bin'
    client_before = digest(client_bin)
    generated, changed = port_edf_file(cpp.read_bytes(), 'datafile.cpp', section)
    if not changed:
        raise ValueError('EDF generator did not replace the legacy methods')
    prefix, bodies = edf_file_definitions()
    names = {b'CDataString::Read': b'DWORD', b'CDataFile::LoadFile': b'BOOL',
             b'CDataFile::LoadFile_ReadFile': b'BOOL', b'CDataFile::LoadFile_ReadSection': b'BOOL'}
    for key in (b'CDataString::CDataString', b'CDataString::~CDataString',
                b'CDataFile::CDataFile', b'CDataFile::~CDataFile'):
        names[key] = b''
    pieces = [b'#include "datafile.h"\n', prefix]
    for key, result in names.items():
        for match in re.finditer(re.escape(key + b'('), generated):
            tail = generated[match.end():]
            if tail.index(b'{') > tail.index(b')') + 5:
                continue
            _, end = section(generated[match.start():], key + b'(', key + b'(')
            pieces.append(result + b' ' + generated[match.start():match.start()+end] + b'\n')
    for body in bodies.values():
        if body not in b''.join(pieces):
            raise ValueError('Test extraction omitted a generated EDF method')
    (work / 'edf-methods.cpp').write_bytes(b''.join(pieces))

    reference = json.loads((ROOT / 'inventory/client455-language-reference.json').read_text(encoding='utf-8'))
    row = next(item for item in reference['files'] if item['folder'] == 'zh-tw')
    edf, payload = ROOT / row['copy'], ROOT / row['decoded']
    if digest(edf) != row['sha256'] or digest(payload) != row['decoded_sha256']:
        raise ValueError('Pinned EDF fixture changed')
    raw = edf.read_bytes()
    (work / 'retry.edf').write_bytes(raw[:-1])
    (work / 'replacement.edf').write_bytes(raw)
    (work / 'tail.edf').write_bytes(raw + b'trailing bytes')
    # Exercise the uncached path on an installed table without staging a copy.
    paths = json.loads((ROOT / 'config/paths.json').read_text())
    large = Path(paths['client_455']) / 'DataTable/zh-tw/NDItem.edf'
    with large.open('rb') as file:
        large_prefix = file.read(33)
    large_payload_size = int.from_bytes(large_prefix[29:33], byteorder='little')
    assert large_payload_size > 8 * 1024 * 1024
    assert large_payload_size + 289 <= large.stat().st_size
    check = b'''#include "datafile.h"
#include "client455_character_rfs.h"
#include "client455_language.h"
#include <cstdio>
#include <cstring>
#include <vector>
static_assert(sizeof(CDataString) == 12 && sizeof(CDataFile) == 304, "455 EDF layout");
int main(int argc, char** paths) {
    if (argc != 4) return 1;
    FILE* an = fopen(paths[2], "rb");
    if (!an) return 2;
    fseek(an, 0, SEEK_END); const long size = ftell(an); rewind(an);
    if (size < 4) { fclose(an); return 2; }
    std::vector<char> expected(static_cast<size_t>(size));
    const auto got = fread(expected.data(), 1, expected.size(), an); fclose(an);
    if (got != expected.size()) return 2;
    unsigned char envelope[289] = {};
    char target = 'x';
    if (!RF455_DecodeEdf(envelope, sizeof(envelope), nullptr, 0) ||
        RF455_DecodeEdf(envelope, sizeof(envelope)-1, &target, 1) || target != 'x') return 14;
    CDataFile file(paths[1]);
    auto* data = file.GetSourceData();
    if (!data->GetString() || data->GetStringLength() != expected.size() ||
        data->GetString()[size] != 0 || memcmp(data->GetString(), expected.data(), expected.size())) return 3;
    char first[4] = {};
    if (data->Read(first, 1, 4) != 4 || memcmp(first, expected.data(), 4)) return 4;
    char bad[] = "retry.edf";
    if (file.LoadFile(bad) || data->Read(first, -1, -1) || data->Read(first, 65536, 65536)) return 5;
    if (data->Read(first, 1, 4) != 4 || memcmp(first, expected.data() + 4, 4)) return 6;
    CDataFile absent(bad);
    if (absent.GetSourceData()->GetString()) return 7;
    auto* cache = RF455_GetCharacterRfsCache();
    const auto beforeRetry = cache->Stats();
    if (!CopyFileA("replacement.edf", bad, FALSE) || !file.LoadFile(bad) ||
        data->GetStringLength() != expected.size() || data->Read(first, 1, 4) != 4 ||
        memcmp(first, expected.data(), 4) || memcmp(data->GetString(), expected.data(), expected.size()) ||
        cache->Stats().payloadReads != beforeRetry.payloadReads + 1 ||
        cache->Stats().hits != beforeRetry.hits) return 15;
    const auto afterRetry = cache->Stats();
    CDataFile refreshed(bad);
    const auto* refreshedBytes = refreshed.GetSourceData()->GetString();
    if (!refreshedBytes || refreshed.GetSourceData()->GetStringLength() != expected.size() ||
        memcmp(refreshedBytes, expected.data(), expected.size()) ||
        cache->Stats().payloadReads != afterRetry.payloadReads || cache->Stats().hits != afterRetry.hits + 1) return 16;
    char withTail[] = "tail.edf";
    if (!file.LoadFile(withTail) || data->Read(first, 1, 4) != 4 || memcmp(first, expected.data(), 4)) return 8;
    const auto cached = cache->Stats();
    CDataFile same(withTail);
    auto* sameData = same.GetSourceData();
    if (!sameData->GetString() || data->GetString() == sameData->GetString() ||
        memcmp(sameData->GetString(), expected.data(), expected.size()) ||
        cache->Stats().payloadReads != cached.payloadReads || cache->Stats().hits != cached.hits + 1) return 9;
    sameData->GetString()[0] ^= 1;
    if (memcmp(data->GetString(), expected.data(), expected.size()) ||
        data->Read(first, 1, 4) != 4 || memcmp(first, expected.data() + 4, 4)) return 10;
    if (!same.LoadFile(withTail) || sameData->Read(first, 1, 4) != 4 ||
        memcmp(first, expected.data(), 4)) return 11;
    const auto beforeStream = cache->Stats();
    if (!file.LoadFile(paths[3]) || data->GetStringLength() <= 8u * 1024u * 1024u ||
        data->GetString()[data->GetStringLength()] != 0 ||
        cache->Stats().payloadReads != beforeStream.payloadReads ||
        cache->Stats().retainedBytes != beforeStream.retainedBytes) return 12;
    cache->SetByteBudget(0);
    const auto noBudget = cache->Stats();
    if (!same.LoadFile(paths[1]) || sameData->GetStringLength() != expected.size() ||
        memcmp(sameData->GetString(), expected.data(), expected.size()) ||
        cache->Stats().hits != noBudget.hits || cache->Stats().misses != noBudget.misses ||
        cache->Stats().payloadReads != noBudget.payloadReads) return 13;
    puts("PASS: zh-tw EDF, corrected-file retry, cache reuse and private cursors, rollback, large stream and zero budget");
}
'''
    (work / 'check.cpp').write_bytes(check)
    info = json.loads((ROOT / 'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dev = info['installation_path'] + '/Common7/Tools/VsDevCmd.bat'
    compiled = [native / name for name in ('client455_language.cpp', 'client455_nation_paths.cpp',
                                            'client455_font_settings.cpp', 'client455_character_rfs.cpp')]
    sources = ' '.join(f'"{path}"' for path in compiled)
    batch = work / 'build.cmd'
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\n'
                     'if errorlevel 1 exit /b 1\n'
                     f'cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W3 /D_CRT_SECURE_NO_WARNINGS '
                     f'/I"{source}" /I"{native}" /FIwindows.h edf-methods.cpp check.cpp {sources} '
                     'user32.lib /Feedf-check.exe /link /OPT:REF\nexit /b %errorlevel%\n', encoding='utf-8')
    build = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work, capture_output=True, timeout=90)
    (work / 'build.txt').write_bytes(build.stdout + build.stderr)
    build.check_returncode()
    result = subprocess.run([str(work / 'edf-check.exe'), str(edf), str(payload), str(large)], cwd=work,
                            check=True, capture_output=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
    assert digest(client_bin) == client_before
    report = {'passed': True, 'architecture': 'x86', 'locale': row['folder'], 'fixture_sha256': row['sha256'],
              'payload_sha256': row['decoded_sha256'], 'reconstructed_client_sha256_after': client_before,
              'large_fixture': large.name, 'large_fixture_bytes': large.stat().st_size,
              'large_payload_bytes': large_payload_size,
              'generator_sha256': digest(ROOT / 'scripts/client455_edf_file_port.py'),
              'source_sha256': {path.name: digest(path) for path in [cpp, header, *compiled]},
              'output': result.stdout.decode('ascii').strip(), 'game_launched': False, 'full_client_build': False}
    (ROOT / 'artifacts/resource-cache/edf-check.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(report['output'])


if __name__ == '__main__':
    main()
