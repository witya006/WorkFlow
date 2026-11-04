"""Strict read-only tooling for the RPK1.0 layout used by the pinned455 client.

This tool rejects malformed metadata. It does not emulate unchecked fread,
search ordering, path mutation or unbounded FILE* reads of the game loader.
Names stay bytes; nothing is extracted to an input installation.
"""
from dataclasses import dataclass
import struct


@dataclass(frozen=True)
class Node:
    name_field: bytes
    declared_size: int
    name_length: int
    child_count: int
    child_start: int

    @property
    def name(self):
        return self.name_field.split(b'\0', 1)[0]


class Rpk:
    def __init__(self, data: bytes):
        if len(data) < 8:
            raise ValueError('Truncated RPK header')
        version, count = struct.unpack_from('<II', data)
        if version != 0x3f800000:
            raise ValueError('Expected RPK version1.0')
        self.base = 8 + 72 * count
        if not count or self.base > len(data):
            raise ValueError('Truncated/empty RPK tables')
        self.children = struct.unpack_from(f'<{count}I', data, 8)
        self.offsets = struct.unpack_from(f'<{count}i', data, 8+4*count)
        self.nodes = tuple(Node(*struct.unpack_from('<52sIHHI', data, 8+8*count+64*i))
                           for i in range(count))
        self.payload = data[self.base:]
        if sorted(self.children) != list(range(count)):
            raise ValueError('RPK child table must be a permutation')
        self.files = {}
        visited = set()
        stack = [(0, b'')]
        while stack:
            i, parent = stack.pop()
            if i in visited:
                raise ValueError('RPK repeated child/cycle')
            visited.add(i)
            node = self.nodes[i]
            if node.name_length != len(node.name) or not node.name or len(node.name) > 51:
                raise ValueError('Invalid RPK name length')
            if i == 0:
                if node.name != b'.\\' or self.offsets[i] != -1:
                    raise ValueError('Expected RPK directory root')
                path = b''
            else:
                if any(c in node.name for c in (b'\\', b'/', b':')) or node.name in (b'.', b'..'):
                    raise ValueError('Unsafe RPK component')
                path = parent + node.name
            if node.child_start + node.child_count > count:
                raise ValueError('RPK child range outside table')
            offset = self.offsets[i]
            if offset == -1:
                for child in reversed(self.children[node.child_start:node.child_start+node.child_count]):
                    stack.append((child, path+b'\\' if path else b''))
            else:
                if offset < 0 or offset > len(self.payload) or node.child_count:
                    raise ValueError('RPK file offset/children invalid')
                key = path.lower()
                if key in self.files:
                    raise ValueError('Duplicate RPK file path')
                self.files[key] = i
        if len(visited) != count:
            raise ValueError('Unreachable RPK nodes')
        # Many real files have uint32(-1-offset) in the size field, especially
        # before a directory node. The game fopen seeks and ignores this size.
        # Use the next distinct payload offset / EOF as the tooling extent;
        # preserve and expose the inaccurate metadata rather than trusting it.
        starts = sorted({o for o in self.offsets if o != -1} | {len(self.payload)})
        ends = dict(zip(starts, starts[1:]))
        ends[len(self.payload)] = len(self.payload)
        self.extents = {i: ends[o]-o for i, o in enumerate(self.offsets) if o != -1}
        self.size_mismatches = [i for i, extent in self.extents.items()
                                if self.nodes[i].declared_size != extent]

    def read(self, path: bytes) -> bytes:
        """Read inferred extent; content parsers must validate their own end."""
        i = self.files[path.replace(b'/', b'\\').lower()]
        at = self.offsets[i]
        return self.payload[at:at+self.extents[i]]

    def to_bytes(self) -> bytes:
        """Rebuild parsed tables; preserve opaque name padding and payload bytes."""
        count = len(self.nodes)
        return (struct.pack('<II', 0x3f800000, count)
                + struct.pack(f'<{count}I', *self.children)
                + struct.pack(f'<{count}i', *self.offsets)
                + b''.join(struct.pack('<52sIHHI', n.name_field, n.declared_size, n.name_length,
                                       n.child_count, n.child_start) for n in self.nodes)
                + self.payload)
