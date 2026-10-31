"""Regression fixtures for the offline document checker, not DSH runtime tests."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_docs import validate


class DocumentChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')

    def skill(self, tail=''):
        self.put('.agents/skills/test-skill/LICENSE', 'MIT License\n')
        self.put('.agents/skills/test-skill/SKILL.md',
                 '---\nname: test-skill\ndescription: Test skill\nlicense: MIT\n---\n\n# Test\n' + tail)

    def test_valid_standalone_skill(self):
        self.skill('[Details](references/details.md#詳細)\n')
        self.put('.agents/skills/test-skill/references/details.md', '# 詳細\n')
        self.assertEqual(validate(self.root).errors, [])

    def test_missing_link_rejected(self):
        self.put('README.md', '[Missing](missing.md)\n')
        self.assertTrue(any('missing target' in e for e in validate(self.root).errors))

    def test_sibling_skill_dependency_rejected(self):
        self.skill('[Bad](../other/SKILL.md)\n')
        self.put('.agents/skills/other/SKILL.md', '# other\n')
        result = validate(self.root, ['.agents/skills/test-skill/SKILL.md'])
        self.assertTrue(any('sibling/repository' in e for e in result.errors))

    def test_missing_license_rejected(self):
        self.skill()
        (self.root / '.agents/skills/test-skill/LICENSE').unlink()
        self.assertTrue(any('missing local LICENSE' in e for e in validate(self.root).errors))

    def test_empty_description_rejected(self):
        self.skill()
        p = self.root / '.agents/skills/test-skill/SKILL.md'
        p.write_text(p.read_text().replace('description: Test skill', 'description:'), encoding='utf-8')
        self.assertTrue(any('description' in e for e in validate(self.root).errors))

    def test_bad_json_rejected(self):
        self.put('data/bad.json', '{')
        self.assertTrue(validate(self.root).errors)

    def test_missing_heading_rejected(self):
        self.put('README.md', '# Good\n[Bad](#absent)\n')
        self.assertTrue(any('missing heading' in e for e in validate(self.root).errors))

    def test_fenced_examples_are_not_links(self):
        self.put('README.md', '# Good\n```markdown\n[Example](not-a-real-file.md)\n```\n')
        self.assertEqual(validate(self.root).errors, [])

    def test_duplicate_and_explicit_anchors(self):
        self.put('README.md', '# Same\n## Same\n<a id="explicit"></a>\n[Second](#same-1) [Explicit](#explicit)\n')
        self.assertEqual(validate(self.root).errors, [])

    def test_partial_index_marks_skipped_heading(self):
        self.put('README.md', '[Other](old.md#unavailable)\n')
        result = validate(self.root, known_paths={'old.md'})
        self.assertEqual(result.errors, [])
        self.assertEqual(result.skipped_anchors, 1)

    def test_historical_baseline_kind_accepted(self):
        self.put('.agents/baseline.json', json.dumps({
            'record_kind': 'historical-source-baseline',
            'release': {'commit': 'a' * 40},
            'sources': []}))
        self.assertEqual(validate(self.root).errors, [])

    def test_invalid_baseline_record_kind_rejected(self):
        self.put('.agents/baseline.json', json.dumps({
            'record_kind': 'unknown-baseline-kind',
            'release': {'commit': 'a' * 40},
            'sources': []}))
        self.assertTrue(any('invalid baseline record kind' in e
                            for e in validate(self.root).errors))

    def test_invalid_baseline_sha_rejected(self):
        self.put('.agents/baseline.json', json.dumps({
            'record_kind': 'active-source-baseline', 'release': {'commit': 'short'}, 'sources': []}))
        self.assertTrue(validate(self.root).errors)

    def test_repository_escape_rejected(self):
        self.put('README.md', '[Outside](../outside.md)\n')
        self.assertTrue(any('escapes repository' in e for e in validate(self.root).errors))

    def test_anchor_attribute_after_class(self):
        self.put('README.md', '# T\n<a class="x" id="explicit"></a>\n[E](#explicit)\n')
        self.assertEqual(validate(self.root).errors, [])

    def test_inline_code_and_comments_are_not_links(self):
        self.put('README.md', '# T\n`[nope](not-real.md)`\n<!-- [nope](not-real.md) -->\n[Yes](also-missing.md)\n')
        errors = validate(self.root).errors
        self.assertTrue(any('also-missing.md' in e for e in errors))
        self.assertFalse(any('not-real.md' in e for e in errors))

    def test_inline_code_uses_exact_backtick_run_lengths(self):
        self.put('README.md', '# T\n`code `` [Example](not-real.md) end`\n[Real](missing.md)\n')
        errors = validate(self.root).errors
        self.assertFalse(any('not-real.md' in error for error in errors))
        self.assertTrue(any('missing.md' in error for error in errors))

    def test_unclosed_long_backticks_do_not_start_shorter_span(self):
        self.put('README.md', '# T\n``unclosed `code` [Missing](missing.md)\n')
        errors = validate(self.root).errors
        self.assertTrue(any('missing.md' in error for error in errors))

    def test_inline_code_anchor_is_not_real_but_heading_code_is(self):
        self.put('README.md', '# `Visible`\n`<a id="hidden"></a>`\n'
                 '[Visible](#visible) [Hidden](#hidden)\n')
        errors = validate(self.root).errors
        self.assertFalse(any('#visible' in error for error in errors))
        self.assertTrue(any('#hidden' in error for error in errors))

    def test_comment_heading_is_not_an_anchor(self):
        self.put('README.md', '# T\n<!--\n# Hidden\n-->\n[H](#hidden)\n')
        self.assertTrue(any('missing heading' in e for e in validate(self.root).errors))

    def test_unclosed_comment_does_not_hide_later_link(self):
        self.put('README.md', '# T\n<!-- still open\n[Missing](missing.md)\n')
        self.assertTrue(any('missing target' in e for e in validate(self.root).errors))

    def test_single_quoted_title_and_angle_destination(self):
        self.put('README.md', "# T\n[A](missing.md 'title')\n[B](<missing file.md>)\n[C](there.md \"ok\")\n")
        self.put('there.md', '# T\n')
        errors = validate(self.root).errors
        self.assertTrue(any('missing.md' in e for e in errors))
        self.assertTrue(any('missing file.md' in e for e in errors))
        self.assertFalse(any('there.md' in e for e in errors))

    def test_null_byte_link_is_reported(self):
        self.put('README.md', '[x](foo%00bar.md)\n[y](missing.md)\n')
        errors = validate(self.root).errors
        self.assertTrue(any('malformed link' in e for e in errors))
        self.assertTrue(any('missing target' in e for e in errors))
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().with_name('validate_docs.py')),
             '--root', str(self.root)],
            capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('malformed link', proc.stderr)
        self.assertNotIn('Cannot start validation', proc.stderr)

    def test_undecodable_fragment_target_is_reported(self):
        self.put('README.md', '[x](bad.md#h)\n')
        (self.root / 'bad.md').write_bytes(b'\xff\xfe')
        errors = validate(self.root).errors
        self.assertTrue(any('cannot read link target' in e for e in errors))

    def test_known_paths_must_be_strings(self):
        self.put('README.md', '# T\n')
        with self.assertRaises(ValueError):
            validate(self.root, known_paths={1})


if __name__ == '__main__':
    unittest.main()
