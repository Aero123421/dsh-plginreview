"""Regression fixtures for the offline document checker, not DSH runtime tests."""
import json
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


if __name__ == '__main__':
    unittest.main()
