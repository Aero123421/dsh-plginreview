---
name: dsh-upstream-refresh
description: DSH本家と関連プラグインの更新を調べ、公開版・開発版・PR・実行結果を分けて、独立plugin向けSkillsと文書の基準を更新する。
license: MIT
---

# 上流に追従する文書・Skillsの更新

本家のReleaseと、利用するAPIの所有package、関連する外部実装を調べます。調査依頼だけなら他repoの実装・公開や利用者のprofileを変更しません。更新対象が指定された場合に、そのrepoのbranch/PRへ反映します。

## 基準を確定する

公開Releaseのtag→commit、実配布経路、開発branchのcommit、確認日時を別々に記録します。prereleaseを安定版と呼ばず、npm dist-tagも推測しません。旧調査のSHA・tarball・試験結果を最新版で上書きしません。

比較は変更fileの所有契約から読みます。Skill本文が不変でも参照APIが変わるため、README・型・実装・回帰試験まで追います。比較APIの上限、検索の欠落、取れないPRは記録し、空の結果を活動ゼロと解釈しません。

## 開発の進み方を調べる

Issueの症状、修正diff、反例を捕まえるtest、追加PR、merge先、公開物、利用者確認をたどります。forkや先行PRの検証を別のheadへ継承しません。PR本文にあるテストは作者報告です。件数・stars・closedだけで品質や加速を判断しません。

外部は必要な分野を選び、DSH adapterと本体全体の変更を分けます。同名APIの形だけでなく、identity、source、保存時点、解除、権限、fallbackの意味を比較します。

## 更新する

現行契約、過去の再現、提案、未実行を分けます。古い回避策を不要にする変更も探し、ルールを増やすだけにしません。本家専用command、役職による承認、全CI、全操作の録画や独自台帳を独立pluginへ機械的に移しません。

必要なSkillとその同梱参照だけを変えます。追加Skillは単独コピーで読める構成にし、frontmatter、相対リンク、LICENSEと元ソースを確認します。実行互換性を確認していない場合はソース基準更新と明記します。

## 受渡し

確認した基準、変更したルール、根拠となる固定ソース、PR状態、実行した検証、残る実機確認を報告します。公開前にlive base/headの変化を見直します。継続集計をする場合はrepo集合と期間を固定し、今回の選択調査から成長率を推測しません。

手順の参考: [レビューの証拠](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-code-review/SKILL.md)、[差分に合う検証](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-pre-push-checks/SKILL.md)。このSkill自体はそれらと公開事例からの独自整理で、本家に同名のSkillがあるという意味ではありません。
