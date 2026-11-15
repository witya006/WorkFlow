"""Keep Ninja's MSVC include-prefix match in the compiler's output encoding."""

import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


def _show_includes_prefix(build):
    cache = (build / 'CMakeCache.txt').read_text(encoding='utf-8')
    compiler = re.search(r'^CMAKE_CXX_COMPILER:[^=]+=([^\r\n]+)$', cache, re.MULTILINE)
    if not compiler:
        raise ValueError(f'CMake did not record the MSVC compiler: {build}')

    header = 'rf455_include_probe.h'
    with TemporaryDirectory(prefix='msvc-include-', dir=build) as scratch:
        (Path(scratch) / header).write_bytes(b'#pragma once\n')
        (Path(scratch) / 'probe.cpp').write_text(f'#include "{header}"\n', encoding='ascii')
        result = subprocess.run(
            [compiler[1], '/nologo', '/showIncludes', '/c', 'probe.cpp', '/Foprobe.obj'],
            cwd=scratch, capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW,
        )
    if result.returncode:
        raise ValueError(f'MSVC /showIncludes probe failed ({result.returncode}): {result.stderr or result.stdout!r}')

    for line in result.stdout.splitlines() + result.stderr.splitlines():
        if line.lower().endswith(header.encode('ascii')):
            path = re.search(rb'(?<=[ \t])(?:[A-Za-z]:[\\/]|\\\\)', line)
            if path:
                return line[:path.start()]
    raise ValueError(f'MSVC /showIncludes did not identify its probe header: {build}')


def configure_msvc_ninja_prefix(build):
    prefix = _show_includes_prefix(build)
    rules = build / 'CMakeFiles/rules.ninja'
    original = rules.read_bytes()
    assignment = b'msvc_deps_prefix = ' + prefix.replace(b'$', b'$$')
    normalized, count = re.subn(rb'^msvc_deps_prefix[ \t]*=[^\r\n]*',
                                lambda _: assignment, original, flags=re.MULTILINE)
    if count > 1:
        raise ValueError(f'Multiple CMake MSVC include prefixes: {rules}')
    if count == 0:
        newline = b'\r\n' if b'\r\n' in original else b'\n'
        normalized = assignment + newline + original
    if normalized != original:
        rules.write_bytes(normalized)
    return prefix.hex()


def ninja_has_header(ninja, build, object_file, header):
    result = subprocess.run([str(ninja), '-t', 'deps', object_file], cwd=build,
                            capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise ValueError(f'Ninja dependency query failed for {object_file}: {result.stderr!r}')
    rows = result.stdout.splitlines()
    if not rows or not rows[0].endswith(b' (VALID)'):
        return False
    leaf = header.encode('ascii').lower()
    return any(row.strip().replace(b'\\', b'/').rsplit(b'/', 1)[-1].lower() == leaf for row in rows[1:])


def prepare_ninja_dependencies(ninja, build, previous, object_file, header):
    prefix = configure_msvc_ninja_prefix(build)
    record = {'prefix_hex': prefix, 'object': object_file, 'header': header}
    # An old object can be up to date in Ninja even with an empty include list.
    has_outputs = (build / '.ninja_log').exists() or (build / object_file).exists()
    recover = has_outputs and (previous.get('ninja_dependencies') != record or
                               not ninja_has_header(ninja, build, object_file, header))
    return record, recover
