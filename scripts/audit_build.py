"""Read-only VC6 input audit. No preprocessing, compilation, or input execution.

ASCII directives are read losslessly with latin-1; original bytes are never written.
Include closure is conservative (all conditional branches); basename candidates
are evidence of a misplaced file, never an automatic include-path resolution.
"""
import collections
import hashlib
import json
import re
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
ROOT = Path(json.loads((WS / 'config/paths.json').read_text(encoding='utf-8'))['legacy_source'])
SRC_EXT = {'.cpp', '.c', '.cxx', '.h', '.hpp', '.inl', '.rc', '.idl', '.odl'}


def read(path):
    return path.read_bytes().decode('latin-1')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def resolve(base, name):
    return (base / name.replace('\\', '/')).resolve()


def values(text, flag):
    return [a or b for a, b in re.findall(r'(?i)(?:^|\s)/' + flag + r'\s*(?:"([^"]*)"|([^\s]+))', text)]


def uncomment(text):
    # Preserve line numbers and quoted strings; remove // and /* */ comments.
    pat = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/'
    return re.sub(pat, lambda m: '\n' * m[0].count('\n') if m[0].startswith(('//', '/*')) else m[0], text)


def parse_project(path):
    text = read(path)
    configs = {}
    current = None
    sources = []
    directives = []
    for line_no, line in enumerate(text.splitlines(), 1):
        match = re.match(r'!(?:IF|ELSEIF)\s+"\$\(CFG\)"\s*==\s*"([^"]+)"', line)
        if match:
            current = match[1]
            configs.setdefault(current, [])
        elif line.startswith('!ENDIF'):
            current = None
        if line.startswith(('# ADD ', '# SUBTRACT ', '# PROP Exclude_From_Build', '# PROP Use_MFC')) and not line.startswith(('# ADD BASE ', '# SUBTRACT BASE ')):
            rec = {'line': line_no, 'directive': line, 'config': current}
            directives.append(rec)
            if current:
                configs[current].append(rec)
        if line.startswith('SOURCE='):
            name = line.split('=', 1)[1].strip().strip('"')
            target = resolve(path.parent, name)
            sources.append({'line': line_no, 'reference': name, 'resolved': rel(target), 'exists': target.is_file()})
    return text, configs, sources, directives


def audit():
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts)
    by_name = collections.defaultdict(list)
    for p in files:
        by_name[p.name.lower()].append(p)
    projects = []
    for path in (p for p in files if p.suffix.lower() == '.dsp'):
        text, configs, sources, directives = parse_project(path)
        inc_dirs = []
        lib_dirs = []
        libraries = set()
        outputs = []
        for d in directives:
            s = d['directive']
            if s.startswith('# ADD CPP '):
                inc_dirs.extend(values(s, 'I'))
            if s.startswith('# ADD LINK32 '):
                lib_dirs.extend(values(s, 'libpath:'))
                libraries.update(re.findall(r'(?i)(?<!\S)([^\s"/]+\.lib)(?=\s|$)', s))
            if s.startswith(('# ADD LINK32 ', '# ADD LIB32 ')):
                outputs.extend(values(s, 'out:'))
        inc_dirs = sorted(set(inc_dirs))
        roots = [path.parent] + [resolve(path.parent, d) for d in inc_dirs]
        queue = [ROOT / s['resolved'] for s in sources if s['exists'] and Path(s['resolved']).suffix.lower() in SRC_EXT]
        seen = set()
        unresolved = []
        pragmas = []
        imports = []
        resources = []
        while queue:
            p = queue.pop()
            if p in seen:
                continue
            seen.add(p)
            for n, line in enumerate(uncomment(read(p)).splitlines(), 1):
                m = re.match(r'\s*#\s*include\s*([<"])([^">]+)[">]', line)
                if m:
                    name = m[2]
                    search = ([p.parent] if m[1] == '"' else []) + roots
                    hit = next((q for base in search if (q := resolve(base, name)).is_file()), None)
                    if hit:
                        if hit.suffix.lower() in SRC_EXT:
                            queue.append(hit)
                    else:
                        unresolved.append({'file': rel(p), 'line': n, 'include': name, 'style': m[1], 'candidates': [rel(x) for x in by_name[Path(name.replace('\\', '/')).name.lower()]]})
                m = re.match(r'\s*#\s*pragma\s+comment\s*\(\s*lib\s*,\s*"([^"]+)"', line, re.I)
                if m:
                    libraries.add(m[1])
                    pragmas.append({'file': rel(p), 'line': n, 'library': m[1]})
                m = re.match(r'\s*#\s*import\s*"([^"]+)"', line)
                if m:
                    imports.append({'file': rel(p), 'line': n, 'reference': m[1], 'exists_on_host': resolve(p.parent, m[1]).is_file()})
                if p.suffix.lower() == '.rc':
                    m = re.match(r'\s*\S+\s+(?:ICON|BITMAP|CURSOR|RCDATA|HTML|TYPELIB)\s+(?:DISCARDABLE\s+)?"([^"]+)"', line, re.I)
                    if m:
                        resources.append({'file': rel(p), 'line': n, 'reference': m[1], 'exists': resolve(p.parent, m[1]).is_file()})
        for s in sources:
            if not s['exists']:
                s['candidates'] = [rel(x) for x in by_name[Path(s['reference'].replace('\\', '/')).name.lower()]]
        projects.append({'project': rel(path), 'sha256': sha(path), 'configurations': configs,
                         'sources': sources, 'include_dirs': [{'reference': x, 'exists': resolve(path.parent, x).is_dir()} for x in inc_dirs],
                         'lib_dirs': lib_dirs, 'outputs': sorted(set(outputs)), 'directives': directives,
                         'libraries': [{'name': x, 'candidates': [rel(p) for p in by_name[x.lower()]]} for x in sorted(libraries, key=str.lower)],
                         'include_closure_files': sorted(rel(p) for p in seen), 'unresolved_includes': unresolved,
                         'pragma_libraries': pragmas, 'imports': imports, 'resources': resources})
    workspaces = []
    for p in (p for p in files if p.suffix.lower() == '.dsw'):
        refs = []
        for n, line in enumerate(read(p).splitlines(), 1):
            m = re.match(r'Project: "([^"]+)"=(.*?) - Package Owner=', line)
            if m:
                target = resolve(p.parent, m[2].strip().strip('"'))
                refs.append({'line': n, 'name': m[1], 'reference': m[2], 'exists': target.is_file(), 'resolved': rel(target)})
        workspaces.append({'workspace': rel(p), 'projects': refs})
    duplicates = []
    outer = ROOT / 'RF Server Side/RF_Server'
    inner = outer / 'RF_Server'
    for folder in ['AccountServer', 'LoginServer', 'common', 'network', 'protocol', 'database', 'table']:
        a = {p.relative_to(outer / folder).as_posix(): p for p in (outer / folder).rglob('*') if p.is_file()}
        b = {p.relative_to(inner / folder).as_posix(): p for p in (inner / folder).rglob('*') if p.is_file()}
        duplicates.append({'folder': folder, 'identical': sorted(k for k in a.keys() & b.keys() if sha(a[k]) == sha(b[k])),
                           'different': sorted(k for k in a.keys() & b.keys() if sha(a[k]) != sha(b[k])),
                           'outer_only': sorted(a.keys() - b.keys()), 'inner_only': sorted(b.keys() - a.keys())})
    baseline = json.loads((WS / 'inventory/legacy-files.json').read_text(encoding='utf-8'))
    integrity = {'checked': len(baseline), 'changed_or_missing': [x['path'] for x in baseline if not (ROOT / x['path']).is_file() or sha(ROOT / x['path']) != x['sha256']]}
    global_imports = []
    for p in files:
        if p.suffix.lower() in SRC_EXT:
            for n, line in enumerate(uncomment(read(p)).splitlines(), 1):
                m = re.match(r'\s*#\s*import\s*"([^"]+)"', line)
                if m:
                    global_imports.append({'file': rel(p), 'line': n, 'reference': m[1],
                                           'in_project_closures': [x['project'] for x in projects if rel(p) in x['include_closure_files']]})
    report = {'scope': str(ROOT), 'method': 'Static conservative union of configurations and preprocessor branches; no compiler/global INCLUDE/LIB emulation. Candidates do not prove resolution or ABI compatibility. SOURCE counts include headers/resources/libraries, not just translation units.',
              'projects': projects, 'workspaces': workspaces,
              'library_files': [{'path': rel(p), 'size': p.stat().st_size, 'sha256': sha(p)} for p in files if p.suffix.lower() == '.lib'],
              'database_file_paths': [rel(p) for p in files if p.suffix.lower() in {'.sql', '.bak', '.mdf', '.ldf'}],
              'duplicate_server_trees': duplicates, 'baseline_integrity': integrity, 'global_imports': global_imports}
    report['summary'] = {'projects': len(projects), 'configurations': sum(len(p['configurations']) for p in projects),
                         'source_entries': sum(len(p['sources']) for p in projects),
                         'missing_source_entries': sum(not s['exists'] for p in projects for s in p['sources']),
                         'missing_workspace_projects': sum(not p['exists'] for w in workspaces for p in w['projects'])}
    listed = {str((ROOT / s['resolved']).resolve()).lower() for p in projects for s in p['sources']}
    report['unlisted_translation_units'] = [rel(p) for p in files if p.suffix.lower() in {'.cpp', '.c', '.cxx'} and str(p.resolve()).lower() not in listed]
    out = WS / 'inventory/build-audit.json'
    out.write_text(json.dumps(report, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    for p in projects:
        print(json.dumps({'project': p['project'], 'configs': len(p['configurations']), 'source_entries': len(p['sources']),
                          'missing': [s['reference'] for s in p['sources'] if not s['exists']],
                          'unresolved_local_names': sorted({x['include'] for x in p['unresolved_includes'] if x['style'] == '"'}),
                          'nonbundled_libraries': [x['name'] for x in p['libraries'] if not x['candidates']]}, ensure_ascii=True))


if __name__ == '__main__':
    audit()
