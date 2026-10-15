# 公式からの調整とライセンス

共通ルールとSkillsは公開されたDeepSeek Harnessの資料を独立plugin向けに調整したものです。公式版そのものでも、公式の互換性認定でもありません。

## 初回の導入元

2026-10-14に、DSH `0.2.1-alpha.2` / `d743267388641bc76f17c45ce8b4c231aed1d32c` のplugin向け4種と本体開発向け15種を調整しました。元file・blob SHA・参照資料は [upstream.json](upstream.json) に内容を変えず残しています。これは現在の実行基準ではなく、初回の導入元です。

公式のagent-experienceのsymlinkは、製品内の実体を一つだけ同梱しています。日本語化、独立repoのmanifest・command確認、配布物・更新後の反映、共存の観点を加え、本体専用gate、承認者、stack、翻訳pair/hash、全UIの録画必須化は持ち込みませんでした。

## 2026-10-15の更新

[baseline.json](baseline.json) のDSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c` を新しいソース基準とします。公開Releaseとmasterは分離します。旧19種のすべてを新しい公式blobへ置き換えた記録ではありません。

- `cordis-plugin-development` と更新・共存の参照資料を、manager、Remote access、Session、再構成の契約に合わせて更新しました。
- `dsh-code-review`、`dsh-pre-push-checks`、`dsh-client-ui-ux`、`dsh-speed-up-perf` を、上流契約・反例・障害中の処理・実際の表示範囲を確認する形へ更新しました。
- `dsh-responsive-ui` は[本家の同名Skill](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-responsive-ui/SKILL.md)から調整しました。
- `dsh-lifecycle-audit` は[本家cordis-styling-nitpicking](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/cordis-styling-nitpicking/SKILL.md)を基にしました。P0の一律分類は移さず、到達可能な失敗と影響から判断します。
- `dsh-upstream-refresh` は[review](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-code-review/SKILL.md)、[pre-push](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-pre-push-checks/SKILL.md)と公開事例の調査からの独自整理です。本家に同名のSkillがあるという意味ではありません。

残る14種は初回の調整を維持しています。参照元の更新と、実DSHでの試験は別です。今回のruntime・実OAuth・全OS・全plugin共存試験は実施していません。使うAPIや版が異なる回には、その所有するソースを読み直します。

## ライセンスの保持

公式資料のMIT許諾とDeepSeekの著作権表示を [LICENSE](LICENSE) と各SkillのLICENSEに保持しています。新しい3種にも同じ許諾文を同梱します。根拠となる公開ソースへの参照は記述の出典で、外部pluginのコードや全文を再配布するものではありません。

個別SkillをコピーするときはLICENSEとreferencesを、共通ルールもコピーするときはNOTICE・upstream.json・baseline.jsonを一緒に保ちます。元repoの指示を機械的に上書きせず、利用先の目的と運用を優先します。
