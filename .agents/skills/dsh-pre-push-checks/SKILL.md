---
name: dsh-pre-push-checks
description: DSHプラグインのpushや検証報告の前に、live base/head、対象packageと差分から必要なローカル確認を選び、根拠を記録する。
license: MIT
---

# 差分に合う検証

remote、live base/head、未commit差分を確認します。対象 `package.json`、lockfile、CI、既存テストから実在するコマンドを選びます。参考は[alpha.3の本家手順](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-pre-push-checks/SKILL.md)ですが、本体専用scriptを独立pluginへ案内しません。

| 変更 | 選ぶ確認 |
| --- | --- |
| 型・runtime処理 | 型検査、lint、旧実装で失敗する回帰試験 |
| lifecycle・通信・保存 | generation、受付停止、consumerの最終保存、依存が残る解除順 |
| entry・exports・build・worker/bin | build、実packのentry、公開Loader経路のsmoke |
| Remote・mock | 生成宣言の鮮度、実際のHostの拒否結果、直接・代替呼出し |
| UI・locale | 実コンテナ、390 CSS px、明暗・日本語・focus・touch、変更した期待値 |
| provider・履歴 | keyless payload・resume、必要な実API。鍵不足は未検証 |
| 配布・更新 | 既存packageの拒否、削除後の失敗、OFF・保存値、実行版・Client反映 |
| 文書・Skills | 例と固定ソース、リンク、frontmatter、単独コピー後の参照・LICENSE |

全suite・全OS・CI新設を毎回要求しません。一方、型検査だけで生成物の起動成功を、mock成功だけで現行Host互換を代用しません。testの選択とcoverageの対象は別であり、失敗を隠すために対象を狭めません。

## 結果とpush

成功結果をcommit/pushのためだけに再実行しません。生成物、自動修正、base更新で結果が無効になった部分を確認します。選択されたtest件数も見て、フィルターが効いたことを確かめます。

環境由来と思う失敗は、同じbase・command・条件での対照を取ります。skip、鍵・OS・SDK不足、動作失敗、pendingを別に報告します。未実行のコマンドを成功と書きません。

履歴書換えが作業範囲ならremoteのOIDを記録し、必要な場合は正確なleaseで保護します。先行PRの変更やretarget後は、そのbaseで差分と検証の有効性を再確認します。公開したhead、実行command、結果、未検証を記録し、CIや公開版の到達をpush成功から推測しません。
