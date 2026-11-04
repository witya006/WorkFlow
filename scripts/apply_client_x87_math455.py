"""Select instruction-identical 455 x87 math; retain the original C++ branch."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_draw455 import merge_behavior_manifest


def main():
    report=json.loads((WS/'inventory/client455-x87-math.json').read_text(encoding='utf-8'))
    library=WS/report['library']
    if hashlib.sha256(library.read_bytes()).hexdigest()!=report['library_sha256']:
        raise ValueError('Verified x87 library changed')
    for name,digest in report['source_sha256'].items():
        if hashlib.sha256((WS/'scripts/native'/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Math source changed since instruction verification')
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    original=(Path(paths['legacy_source'])/'R3Engine/R3Engine/common/r3math.cpp').read_bytes()
    desired=original
    nl=b'\r\n' if b'\r\n' in original else b'\n'
    for anchor,call in [(b'BOOL MatrixInvert( float get[4][4], float a[4][4] )',
                         b'    return RF455_MatrixInvert(get,a);'),
                        (b'void Vector3fTransform( float get[3],float pos[3],float f_matrix[4][4])',
                         b'    RF455_Vector3fTransform(get,pos,f_matrix);')]:
        if desired.count(anchor)!=1: raise ValueError('Nonunique math function anchor')
        start=desired.index(b'{',desired.index(anchor))+1
        end=desired.index(nl+b'}',start)
        body=desired[start:end]
        desired=desired[:start]+nl+b'#if defined(RF_CLIENT_455_X87_MATH)'+nl+call+nl+b'#else'+body+nl+b'#endif'+desired[end:]
    desired=(b'#if defined(RF_CLIENT_455_X87_MATH)'+nl+b'#include "client455_x87_math.h"'+nl+b'#endif'+nl)+desired
    output=WS/'work/client-build/source/R3Engine/common/r3math.cpp'
    if output.read_bytes() not in (original,desired): raise ValueError('Preserving unexpected math source edits')
    if output.read_bytes()!=desired: output.write_bytes(desired)
    merge_behavior_manifest([{'file':output.relative_to(WS).as_posix(),
        'original_sha256':hashlib.sha256(original).hexdigest(),'input_sha256':hashlib.sha256(original).hexdigest(),
        'patched_sha256':hashlib.sha256(desired).hexdigest(),'build_option':'RF_CLIENT_455_X87_MATH',
        'legacy_branch_preserved':True,'implementation_library_sha256':report['library_sha256'],
        'reason':'Preserve 455 x87 arithmetic instruction order, float spills and caller FP control instead of binary32 intermediate rounding.',
        'binary_evidence':report['binary_evidence']}])
    print('PASS: verified 455 x87 math selected separately; original C++ bodies retained.')


if __name__=='__main__': main()
