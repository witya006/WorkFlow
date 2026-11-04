"""Verify x86 and /MT directives of all real client/engine object files.

This checks compiler artifacts, not binary behavior or old Character/CRT ABI.
"""
import hashlib
import json
import re
import struct
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def directives(data):
    if len(data) < 20:
        raise ValueError('Truncated COFF header')
    machine, count = struct.unpack_from('<HH', data)
    if machine != 0x14c or struct.unpack_from('<H', data, 16)[0] or 20+40*count > len(data):
        raise ValueError('Expected complete x86 COFF object')
    result = b''
    for index in range(count):
        at = 20+40*index
        size, start = struct.unpack_from('<II', data, at+16)
        flags = struct.unpack_from('<I', data, at+36)[0]
        if size and start == 0 and flags & 0x80:
            continue  # Uninitialized data has memory extent, no bytes in the object.
        if size and start+size > len(data):
            raise ValueError('Truncated COFF section')
        if data[at:at+8] == b'.drectve':
            result += data[start:start+size]
    return result.decode('ascii')


def main():
    build = WS/'work/client-build/build-character-diagnostic'
    records = []
    sets = []
    weather='RF_CLIENT_455_WEATHER:BOOL=ON' in (build/'CMakeCache.txt').read_text(encoding='utf-8')
    resource='RF_CLIENT_455_RESOURCE_IO:BOOL=ON' in (build/'CMakeCache.txt').read_text(encoding='utf-8')
    clock='RF_CLIENT_455_CLOCK:BOOL=ON' in (build/'CMakeCache.txt').read_text(encoding='utf-8')
    targets = [('RF_Online', 180, build), ('R3EngineClientMT', 58+int(weather)+int(resource)+int(clock), build)]
    jpeg_report = WS/'inventory/jpeg6b-build.json'
    if jpeg_report.exists():
        jpeg = json.loads(jpeg_report.read_text(encoding='utf-8'))
        library = WS/jpeg['library']
        if hashlib.sha256(library.read_bytes()).hexdigest() != jpeg['library_sha256']:
            raise ValueError('JPEG archive changed since golden verification')
        targets.append(('JpegLibMT', 46, WS/'work/client-dependencies/jpeg6b/build'))
    for target, expected, root in targets:
        objects = sorted((root/f'{target}.dir/Release').glob('*.obj'))
        if len(objects) != expected:
            raise ValueError(f'{target}: expected {expected} objects, found {len(objects)}')
        for path in objects:
            data = path.read_bytes()
            text = directives(data)
            if not re.search(r'/DEFAULTLIB:"?LIBCMT"?(?:\s|$)', text, re.I):
                raise ValueError(f'{path}: no static release CRT directive')
            if 'RuntimeLibrary=MD_' in text or re.search(r'/DEFAULTLIB:"?MSVCRT', text, re.I):
                raise ValueError(f'{path}: dynamic CRT directive in static CRT target')
            records.append({'file': path.relative_to(WS).as_posix(), 'sha256': hashlib.sha256(data).hexdigest(),
                            'architecture': 'x86', 'directives': text})
        sets.append({'target': target, 'objects_verified': len(objects), 'architecture': 'x86', 'runtime': '/MT'})
    archive = build/'lib/Release/R3EngineMT.lib'
    raw = archive.read_bytes()
    if not raw.startswith(b'!<arch>\n'):
        raise ValueError('R3EngineMT output is not a COFF archive')
    detail = json.dumps(records, indent=2)+'\n'
    artifact = WS/'artifacts/client-character-diagnostic/coff-objects.json'
    artifact.write_text(detail, encoding='utf-8')
    report = {'scope': 'Modern client and actual /MT engine variant; old Character library ABI remains unproven',
              'targets': sets, 'archive': archive.relative_to(WS).as_posix(),
              'archive_sha256': hashlib.sha256(raw).hexdigest(), 'archive_bytes': len(raw),
              'object_manifest': artifact.relative_to(WS).as_posix(),
              'object_manifest_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
              'input_exe_execution': False}
    (WS/'inventory/client-mt-variant.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: {sum(x["objects_verified"] for x in sets)} objects are x86 /MT; actual R3EngineMT.lib verified.')


if __name__ == '__main__':
    main()
