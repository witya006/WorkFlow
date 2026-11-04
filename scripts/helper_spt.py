"""Strict parser/writer for the observed helper-only map SPT subset.

Reference loader: R3Engine/2ndclass/extdummy.cpp CExtDummy::LoadExtDummy.
No game files are modified. Unknown sections/options are rejected explicitly.
"""
from dataclasses import dataclass
import math
import re
import struct


class FormatError(ValueError):
    pass


@dataclass(frozen=True)
class Helper:
    name: bytes
    bounds: tuple[float, ...]
    matrix: tuple[float, ...]

    @property
    def legacy_name(self):
        """Canonical 31-byte lowercase name (455; old goto skipped later strlwr)."""
        return self.name.lower()[:31]


def f32(token):
    try:
        value = struct.unpack('<f', struct.pack('<f', float(token)))[0]
    except (ValueError, OverflowError, struct.error) as exc:
        raise FormatError('Invalid float32') from exc
    if not math.isfinite(value):
        raise FormatError('Non-finite float32')
    return value


def parse(data: bytes, *, max_bytes=16*1024*1024, max_records=1_000_000):
    if len(data) > max_bytes:
        raise FormatError('File size limit exceeded')
    tokens = re.findall(rb'\S+', data)
    if any(len(t) > 255 or b'\0' in t for t in tokens):
        raise FormatError('Invalid/oversized token')
    cursor = 0
    def take():
        nonlocal cursor
        if cursor >= len(tokens):
            raise FormatError('Truncated input')
        value = tokens[cursor]
        cursor += 1
        return value
    def expect(value):
        if take() != value:
            raise FormatError(f'Expected {value!r}')
    expect(b'script_begin')
    expect(b'[HelperObjectBegin]')
    helpers = []
    while True:
        name = take()
        if name == b'[HelperObjectEnd]':
            break
        if not name.startswith(b'*'):
            raise FormatError('Expected helper name')
        if len(helpers) >= max_records:
            raise FormatError('Record limit exceeded')
        bounds = tuple(f32(take()) for _ in range(6))
        expect(b'-node_tm')
        matrix = tuple(f32(take()) for _ in range(16))
        helpers.append(Helper(name[1:], bounds, matrix))
    expect(b'script_end')
    if cursor != len(tokens):
        raise FormatError('Unexpected trailing tokens')
    return helpers


def encode(helpers):
    lines = [b'script_begin', b'[HelperObjectBegin]']
    for helper in helpers:
        if re.search(rb'\s|\0', helper.name) or len(helper.name) > 254:
            raise FormatError('Invalid helper name')
        if len(helper.bounds) != 6 or len(helper.matrix) != 16:
            raise FormatError('Invalid helper dimensions')
        def number(value):
            return format(f32(value), '.9g').encode('ascii')
        lines.append(b'*' + helper.name + b' ' + b' '.join(number(x) for x in helper.bounds))
        lines.append(b'-node_tm')
        for row in range(4):
            lines.append(b' '.join(number(x) for x in helper.matrix[4*row:4*row+4]))
    lines.extend([b'[HelperObjectEnd]', b'script_end'])
    return b'\n'.join(lines) + b'\n'


def fingerprint(helpers):
    # Compare exact float32 bit patterns, including negative zero.
    return [(h.name, h.legacy_name, struct.pack('<22f', *h.bounds, *h.matrix)) for h in helpers]
