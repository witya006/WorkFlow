"""Owned ordinary particle/entity slots. RVP keeps its independent owners."""
from pathlib import Path


NATIVE = Path(__file__).with_name('native')
HEADER = 'client455_particle_registry.h.inc'
SOURCE = 'client455_particle_registry.cpp.inc'


def particle_registry_header(raw, section):
    start = raw.index(b'#define\t\tMAXLOADPARTICLE\t1024')
    end = raw.index(b'#define\t\tANI_MAX_ID', start)
    return raw[:start] + (NATIVE / HEADER).read_bytes() + b'\n' + raw[end:]


def particle_registry_source(raw, section):
    first = b'void\tCParticleManager::AddParticle('
    last = b'void\tCParticleManager::RestoreAll()'
    start, _ = section(raw, first, first)
    _, end = section(raw, last, last)
    return raw[:start] + (NATIVE / SOURCE).read_bytes() + raw[end:]
