#!/usr/bin/env python3
"""Check document structure offline; this does not validate DSH runtime behavior.

Fenced blocks, inline code, and closed HTML comments are not links. Headings and
explicit anchors inside those regions are not headings either.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(
    r'!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)'
    r'(?:\s+(?:"[^"\n]*"|\'[^\'\n]*\'))?\s*\)')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
SHA = re.compile(r'^[0-9a-f]{40}$')
ANCHOR_TAG = re.compile(r'<a\b[^>]*>', re.IGNORECASE)
ANCHOR_ATTR = re.compile(r'\b(?:id|name)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


def _span_end(text: str, start: int, size: int) -> int | None:
    """Return the index after a closing backtick run of exactly `size`."""
    cursor = start
    while cursor < len(text):
        found = text.find('`', cursor)
        if found < 0:
            return None
        end = found + 1
        while end < len(text) and text[end] == '`':
            end += 1
        if end - found == size:
            return end
        cursor = end
    return None


def _mask(chunk: str) -> str:
    return ''.join('\n' if char == '\n' else ' ' for char in chunk)


def strip_html_comments(text: str) -> str:
    """Blank closed HTML comments, leaving backtick spans intact."""
    out: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == '`':
            end = index + 1
            while end < len(text) and text[end] == '`':
                end += 1
            close = _span_end(text, end, end - index)
            if close is None:
                out.append(text[index:end])
                index = end
                continue
            out.append(text[index:close])
            index = close
            continue
        if text.startswith('<!--', index):
            close = text.find('-->', index + 4)
            if close < 0:
                out.append(text[index])
                index += 1
                continue
            close += 3
            out.append(_mask(text[index:close]))
            index = close
            continue
        out.append(text[index])
        index += 1
    return ''.join(out)


def mask_inline_code(text: str) -> str:
    """Blank paired backtick spans so example links are not checked."""
    out: list[str] = []
    index = 0
    while index < len(text):
        if text[index] != '`':
            out.append(text[index])
            index += 1
            continue
        end = index + 1
        while end < len(text) and text[end] == '`':
            end += 1
        close = _span_end(text, end, end - index)
        if close is None:
            out.append(text[index:end])
            index = end
            continue
        out.append(_mask(text[index:close]))
        index = close
    return ''.join(out)


def prose(text: str) -> str:
    result: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = FENCE.match(line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            result.append('')
        else:
            result.append(line if fence is None else '')
    return '\n'.join(result)


def link_text(text: str) -> str:
    return mask_inline_code(strip_html_comments(prose(text)))


def anchors(text: str) -> set[str]:
    clean = strip_html_comments(prose(text))
    found: set[str] = set()
    visible = mask_inline_code(clean)
    for tag in ANCHOR_TAG.findall(visible):
        found.update(ANCHOR_ATTR.findall(tag))
    counts: dict[str, int] = {}
    for line, visible_line in zip(clean.splitlines(), visible.splitlines()):
        if not re.match(r'^#{1,6}[ \t]+', visible_line):
            continue
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match:
            continue
        title = re.sub(r'<[^>]*>', '', match.group(1)).strip().lower()
        slug = ''.join(c for c in title if c.isalnum() or c in '_- ')
        slug = slug.replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        found.add(slug + (f'-{count}' if count else ''))
    return found


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    files: int = 0
    links: int = 0
    skills: int = 0
    skipped_anchors: int = 0


def validate(root: Path, selected: list[str] | None = None,
             known_paths: set[str] | None = None) -> Result:
    root = root.resolve()
    if known_paths is not None and any(not isinstance(item, str) for item in known_paths):
        raise ValueError('known paths must be strings')
    known = set(known_paths or ())
    result = Result()
    if selected is None:
        selected = sorted(str(p.relative_to(root)) for p in root.rglob('*')
                          if p.is_file() and p.suffix in {'.md', '.json'}
                          and not any(x in {'.git', 'node_modules'} for x in p.relative_to(root).parts))
    seen_names: set[str] = set()
    for relative in selected:
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
            text = path.read_text(encoding='utf-8')
        except (ValueError, OSError, UnicodeError) as error:
            result.errors.append(f'{relative}: cannot read within root: {error}')
            continue
        result.files += 1
        if '@UPSTREAM@' in text:
            result.errors.append(f'{relative}: unexpanded source placeholder')
        if path.suffix == '.json':
            try:
                data = json.loads(text)
                if relative == '.agents/baseline.json':
                    if data.get('record_kind') not in {'active-source-baseline', 'historical-source-baseline'}:
                        raise ValueError('invalid baseline record kind')
                    if not SHA.fullmatch(data['release']['commit']):
                        raise ValueError('release commit must be a full SHA')
                    ids = [s['id'] for s in data['sources']]
                    if len(ids) != len(set(ids)):
                        raise ValueError('duplicate source id')
                    for source in data['sources']:
                        if not SHA.fullmatch(source['commit']):
                            raise ValueError('source commit must be a full SHA')
                        blob = source.get('blob_sha')
                        if blob is not None and not SHA.fullmatch(blob):
                            raise ValueError('invalid source blob SHA')
            except (ValueError, TypeError, KeyError) as error:
                result.errors.append(f'{relative}: invalid JSON/metadata: {error}')
            continue
        if path.suffix != '.md':
            continue
        skill_root = path.parent if path.name == 'SKILL.md' else None
        if skill_root:
            result.skills += 1
            parts = text.split('---', 2)
            fields = {}
            if len(parts) == 3 and not parts[0].strip():
                for line in parts[1].splitlines():
                    key, sep, value = line.partition(':')
                    if sep:
                        fields[key.strip()] = value.strip()
            name = fields.get('name', '')
            if name != path.parent.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
                result.errors.append(f'{relative}: invalid or mismatched Skill name')
            if not fields.get('description') or fields.get('license') != 'MIT':
                result.errors.append(f'{relative}: description and MIT license are required')
            if name in seen_names:
                result.errors.append(f'{relative}: duplicate Skill name')
            seen_names.add(name)
            if not (skill_root / 'LICENSE').is_file():
                result.errors.append(f'{relative}: missing local LICENSE')
        for raw in LINK.findall(link_text(text)):
            try:
                url = urlsplit(raw.strip('<>'))
            except ValueError:
                result.errors.append(f'{relative}: malformed link {raw}')
                continue
            if url.scheme or url.netloc:
                continue
            result.links += 1
            try:
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
            except (OSError, ValueError) as error:
                result.errors.append(f'{relative}: malformed link {raw}: {error}')
                continue
            try:
                target_relative = str(target.relative_to(root))
            except ValueError:
                result.errors.append(f'{relative}: link escapes repository: {raw}')
                continue
            if skill_root:
                try:
                    target.relative_to(skill_root)
                except ValueError:
                    result.errors.append(f'{relative}: Skill requires a sibling/repository file: {raw}')
            exists_in_index = target_relative in known or any(
                p.startswith(target_relative.rstrip('/') + '/') for p in known)
            if not target.exists() and not exists_in_index:
                result.errors.append(f'{relative}: missing target {raw}')
            elif url.fragment and target.suffix == '.md':
                if target.is_file():
                    try:
                        target_text = target.read_text(encoding='utf-8')
                    except (OSError, UnicodeError) as error:
                        result.errors.append(f'{relative}: cannot read link target {raw}: {error}')
                        continue
                    if unquote(url.fragment) not in anchors(target_text):
                        result.errors.append(f'{relative}: missing heading {raw}')
                else:
                    result.skipped_anchors += 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--files', type=Path, help='JSON array of materialized paths to check')
    parser.add_argument('--known-paths', type=Path,
                        help='Partial-checkout only: JSON array from a verified tree; headings of absent files are not checked')
    args = parser.parse_args()
    try:
        selected = json.loads(args.files.read_text()) if args.files else None
        known = set(json.loads(args.known_paths.read_text())) if args.known_paths else None
        result = validate(args.root, selected, known)
    except (OSError, ValueError, TypeError) as error:
        print(f'Cannot start validation: {error}', file=sys.stderr)
        return 2
    for error in result.errors:
        print(error, file=sys.stderr)
    print(f'files={result.files} skills={result.skills} relative_links={result.links} '
          f'skipped_heading_checks={result.skipped_anchors} errors={len(result.errors)}')
    if args.known_paths:
        print('PARTIAL CHECKOUT: path-only index entries are not content or runtime verification.')
    return 1 if result.errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
