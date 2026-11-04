"""Build pinned official IJG JPEG 6b as x86 /MT, verify legacy ABI and stock vectors.

Only genuine public source is extracted; original RF sources are read unchanged.
Executables run below are built here from that source, never supplied game EXEs.
"""
import hashlib
import json
import re
import struct
import subprocess
import tarfile
import urllib.request
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
URL = 'https://www.ijg.org/files/jpegsrc.v6b.tar.gz'
SHA256 = '75c3ec241e9996504fe02a9ed4d12f16b74ade713972f3db9e65ce95cd27e35d'


def write_generated(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding='ascii') != data:
        path.write_text(data, encoding='ascii')


def main():
    archive = WS/'local/downloads/jpegsrc.v6b.tar.gz'
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        with urllib.request.urlopen(URL, timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError('Official JPEG archive differs from pinned digest')
        archive.write_bytes(data)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError('JPEG archive hash mismatch')
    work = WS/'work/client-dependencies/jpeg6b'
    source = work/'jpeg-6b'
    work.mkdir(parents=True, exist_ok=True)
    # Extract only ordinary files under the expected directory; preserve changed copies.
    with tarfile.open(archive, 'r:gz') as bundle:
        for member in bundle.getmembers():
            parts = Path(member.name).parts
            if not parts or parts[0] != 'jpeg-6b' or '..' in parts or Path(member.name).is_absolute():
                raise ValueError('Unexpected JPEG archive path')
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError('Non-regular JPEG archive member')
            target = work/member.name
            data = bundle.extractfile(member).read()
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_bytes() != data:
                raise ValueError(f'Preserving modified third-party file: {target}')
            if not target.exists():
                target.write_bytes(data)
    config = source/'jconfig.h'
    expected_config = (source/'jconfig.vc').read_bytes()
    if config.exists() and config.read_bytes() != expected_config:
        raise ValueError('Preserving modified JPEG configuration')
    if not config.exists():
        config.write_bytes(expected_config)
    makefile = (source/'makefile.vc').read_text(encoding='ascii')
    library_sources = re.search(r'LIBSOURCES=(.*?)\n# memmgr', makefile, re.S)[1]
    sources = re.findall(r'\b\w+\.c\b', library_sources)+['jmemnobs.c']
    if len(sources) != 46:
        raise ValueError('Unexpected IJG 6b library source set')
    decoder = re.search(r'DOBJECTS=(.*?)\n', makefile.replace('\\\n', ' '), re.S)[1]
    decoder_sources = [x.replace('.obj', '.c') for x in re.findall(r'\b\w+\.obj\b', decoder)]
    legacy = WS/'work/client-build/source/R3Engine/common'
    values = ['JPEG_LIB_VERSION', 'BITS_IN_JSAMPLE', 'sizeof(boolean)', 'sizeof(JDIMENSION)',
              'sizeof(JSAMPLE)', 'sizeof(JCOEF)', 'sizeof(struct jpeg_error_mgr)',
              'sizeof(struct jpeg_common_struct)', 'sizeof(struct jpeg_compress_struct)',
              'sizeof(struct jpeg_decompress_struct)', 'sizeof(jpeg_component_info)',
              'sizeof(JQUANT_TBL)', 'sizeof(JHUFF_TBL)']
    fields = ['err', 'image_width', 'image_height', 'num_components', 'jpeg_color_space',
              'out_color_space', 'dct_method', 'output_width', 'output_height', 'output_components',
              'output_scanline', 'comp_info', 'quant_tbl_ptrs', 'dc_huff_tbl_ptrs', 'ac_huff_tbl_ptrs']
    values += [f'offsetof(struct jpeg_decompress_struct, {x})' for x in fields]
    for name, folder in [('provider', source), ('legacy', legacy)]:
        text = '#include <stdio.h>\n#include <stddef.h>\n'
        text += f'#include "{(folder/"jpeglib.h").as_posix()}"\n'
        text += f'const unsigned* config_{name}(unsigned* n) {{\nstatic const unsigned a[] = {{'+','.join(values)+'};\n'
        text += '*n=sizeof(a)/sizeof(a[0]); return a; }\n'
        write_generated(work/f'{name}_abi.c', text)
    write_generated(work/'abi_probe.c', '''#include <stdio.h>
const unsigned* config_provider(unsigned*);
const unsigned* config_legacy(unsigned*);
int main(void) {
  unsigned na, nb, i;
  const unsigned *a=config_provider(&na), *b=config_legacy(&nb);
  if(na!=nb) return 2;
  for(i=0;i<na;i++) if(a[i]!=b[i]) return 3;
  printf("[");
  for(i=0;i<na;i++) printf("%s%u",i?",":"",a[i]);
  printf("]\\n"); return 0;
}
''')
    cmake = '''cmake_minimum_required(VERSION 3.24)
project(RFJpeg6b LANGUAGES C)
if(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
 message(FATAL_ERROR "JPEG client dependency requires MSVC x86")
endif()
set(CMAKE_MSVC_RUNTIME_LIBRARY MultiThreaded)
set(JPEG "${CMAKE_CURRENT_LIST_DIR}/jpeg-6b")
add_library(JpegLibMT STATIC
'''+''.join(f' "${{JPEG}}/{x}"\n' for x in sources)+''')
target_include_directories(JpegLibMT PUBLIC "${JPEG}")
target_compile_definitions(JpegLibMT PRIVATE _CRT_SECURE_NO_WARNINGS _CRT_NONSTDC_NO_DEPRECATE)
target_compile_options(JpegLibMT PRIVATE /MP4)
set_target_properties(JpegLibMT PROPERTIES ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
add_executable(jpeg_abi_probe abi_probe.c provider_abi.c legacy_abi.c)
add_executable(djpeg
'''+''.join(f' "${{JPEG}}/{x}"\n' for x in decoder_sources)+''')
target_link_libraries(djpeg PRIVATE JpegLibMT)
target_compile_definitions(djpeg PRIVATE _CRT_SECURE_NO_WARNINGS _CRT_NONSTDC_NO_DEPRECATE)
'''
    write_generated(work/'CMakeLists.txt', cmake)
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    cmake_exe = Path(verified['installation_path'])/'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
    logs = WS/'artifacts/jpeg6b'
    logs.mkdir(parents=True, exist_ok=True)
    build = work/'build'
    commands = [([str(cmake_exe), '-S', str(work), '-B', str(build), '-G', 'Visual Studio 18 2026', '-A', 'Win32', '-T', 'v145'], 'configure.txt'),
                ([str(cmake_exe), '--build', str(build), '--config', 'Release', '--parallel', '4'], 'build.txt')]
    for command, log in commands:
        with (logs/log).open('wb') as output:
            run = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
        if run.returncode:
            raise RuntimeError(f'JPEG build failed: {logs/log}')
    result = subprocess.check_output([str(build/'Release/jpeg_abi_probe.exe')], cwd=work)
    abi = json.loads(result)
    if len(abi) != len(values):
        raise ValueError('Incomplete JPEG ABI probe')
    vectors = []
    for name in ['testorig.jpg', 'testprog.jpg']:
        output = logs/(name+'.ppm')
        run = subprocess.run([str(build/'Release/djpeg.exe'), '-dct', 'int', '-ppm', '-outfile', str(output), str(source/name)], capture_output=True)
        if run.returncode or output.read_bytes() != (source/'testimg.ppm').read_bytes():
            raise ValueError(f'IJG golden decode differs: {name}')
        vectors.append({'input': name, 'input_sha256': hashlib.sha256((source/name).read_bytes()).hexdigest(),
                        'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'golden_exact': True})
    lib = build/'lib/Release/JpegLibMT.lib'
    if not lib.read_bytes().startswith(b'!<arch>\n'):
        raise ValueError('JPEG output is not a COFF archive')
    probe = (build/'Release/jpeg_abi_probe.exe').read_bytes()
    pe = struct.unpack_from('<I', probe, 0x3c)[0]
    if struct.unpack_from('<H', probe, pe+4)[0] != 0x14c:
        raise ValueError('JPEG ABI probe is not x86')
    report = {'provider': 'Independent JPEG Group, JPEG 6b', 'source_url': URL, 'archive_sha256': SHA256,
              'license_file': (source/'README').relative_to(WS).as_posix(), 'modified_upstream_sources': [],
              'configuration': 'Unmodified jconfig.vc copied to generated jconfig.h', 'library_sources': len(sources),
              'library': lib.relative_to(WS).as_posix(), 'library_sha256': hashlib.sha256(lib.read_bytes()).hexdigest(),
              'architecture': 'x86', 'runtime': '/MT',
              'legacy_abi': {'matched': True, 'values': dict(zip(values, abi))}, 'golden_vectors': vectors,
              'input_game_exe_execution': False, 'limit': 'Library/source-header ABI and IJG stock vectors; client 455 JPEG behavior not established.'}
    (WS/'inventory/jpeg6b-build.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: JPEG 6b x86 /MT; {len(abi)} ABI values match legacy headers; two exact golden decodes.')


if __name__ == '__main__':
    main()
