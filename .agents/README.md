# DSHプラグイン開発用の指示とSkills

独立したプラグインrepoで使う22種のSkillsです。実行プラグインではありません。現在のソース基準はDSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`。2026-10-15に影響の大きい既存5 Skillsと参照資料を更新し、3種を追加しました。22種すべてを再実行・全API照合したという意味ではありません。

共通指示は [AGENTS.md](AGENTS.md)、現在の確認ソースは [baseline.json](baseline.json)、初回19種の導入元は [upstream.json](upstream.json)、調整と許諾は [NOTICE.md](NOTICE.md) にあります。

## プラグイン開発用

| Skill | 使う作業 |
| --- | --- |
| [cordis-plugin-development](skills/cordis-plugin-development/SKILL.md) | Host・UI・MCP、配布・更新・解除 |
| [cordis-composition-reference](skills/cordis-composition-reference/SKILL.md) | bundle patch、Loader、依存・scope・isolate |
| [editing-cordis-compositions](skills/editing-cordis-compositions/SKILL.md) | presetとHostへの配置 |
| [agent-experience](skills/agent-experience/SKILL.md) | tool名・説明・schema、情報発見とcontext量 |

## 本体開発用から調整したもの

| Skill | 使う作業 |
| --- | --- |
| [dsh-code-review](skills/dsh-code-review/SKILL.md) | 現行契約、差分、consumerと根拠のレビュー |
| [dsh-client-ui-ux](skills/dsh-client-ui-ux/SKILL.md) | slot、locale、保存・拒否・結果不明のUI |
| [dsh-error-handling](skills/dsh-error-handling/SKILL.md) | 部分失敗、取消、復旧、診断 |
| [dsh-pre-push-checks](skills/dsh-pre-push-checks/SKILL.md) | 差分に合う検証、base/headと結果の照合 |
| [dsh-ci-test-reliability](skills/dsh-ci-test-reliability/SKILL.md) | clock、port、process、並行試験の信頼性 |
| [dsh-doc](skills/dsh-doc/SKILL.md) | README、導入、設定、互換性 |
| [dsh-prose-standard](skills/dsh-prose-standard/SKILL.md) | 文書・comment・UI文言 |
| [dsh-trim-cot-leakage](skills/dsh-trim-cot-leakage/SKILL.md) | 作業中の語りや非公開参照の整理 |
| [dsh-translate-docs](skills/dsh-translate-docs/SKILL.md) | 依頼された翻訳と更新 |
| [dsh-create-upgrade-guide](skills/dsh-create-upgrade-guide/SKILL.md) | 利用者向けの移行案内 |
| [dsh-find-simplifications](skills/dsh-find-simplifications/SKILL.md) | 実利用を保った不要実装・依存の削減 |
| [dsh-speed-up-perf](skills/dsh-speed-up-perf/SKILL.md) | 平常時・障害時の負荷と意味を保つ最適化 |
| [dsh-archive-agent-notes](skills/dsh-archive-agent-notes/SKILL.md) | 設計記録の統合・整理 |
| [dsh-merging-stacked-prs](skills/dsh-merging-stacked-prs/SKILL.md) | 依存PRの検証・順序・merge |
| [record-browser-gif](skills/record-browser-gif/SKILL.md) | 必要なUI操作の録画 |

## 追加した3種

| Skill | 使う作業 |
| --- | --- |
| [dsh-lifecycle-audit](skills/dsh-lifecycle-audit/SKILL.md) | consumerの最終保存より先に依存が閉じないかを監査 |
| [dsh-responsive-ui](skills/dsh-responsive-ui/SKILL.md) | 390pxと実コンテナ幅、touch/hover、focus、省略 |
| [dsh-upstream-refresh](skills/dsh-upstream-refresh/SKILL.md) | Release・PR・consumerを照合して次の基準へ更新 |

## 別のリポジトリへ持ち込む

必要な `skills/<名前>/` を対象の `.agents/skills/<名前>/` へ、LICENSE・referencesを含めてディレクトリごとコピーします。Skill本文は隣のSkillやこのrepoの相対pathを必須にしません。コピー先のcommandやAPIは改めて確認します。

共通ルールも使う場合は `AGENTS.md`、`LICENSE`、`NOTICE.md`、`upstream.json`、`baseline.json` を同じ `.agents/` へコピーし、ルートAGENTSから参照します。既存のremote、branch、検証方針を維持し、一括上書きしません。

```markdown
DSHプラグインの実装・レビューでは `.agents/AGENTS.md` を読み、対象作業に合う `.agents/skills/` のSkillを使います。
```

全22種を毎回読み込む必要はありません。更新を設計するときはplugin-development、資源を持つ変更にはlifecycle、画面幅の変更にはresponsiveを選びます。呼出し構文や自動検出は使う開発エージェントに従います。
