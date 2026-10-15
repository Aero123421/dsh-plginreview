# 更新確認・導入・反映

確認基準: DSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`。model catalog、外部binary、plugin package、DSH本体、ブラウザーの再読込みは別の更新です。小さいpluginへ独自updaterを一律追加しません。

## 候補と導入

[managerの契約](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/boot/plugin-manager/README.md)と[既存packageへの導入](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/docs/upgrade-guide/v0.2.1-alpha.2/plugin-install-over-installed/guide.md)を確認します。汎用 `update()` / `checkForUpdates()` を仮定しません。

HMR下の識別可能な既存packageへの `installBundle()` は `already-installed` になる経路があります。標準の削除→導入を利用する場合も、削除する相手より長く生きる操作所有者が必要です。自分のRPC内で自分を解除してから残りを実行する形を、未検証で採用しません。削除不可・拒否を権限緩和で迂回しません。

repository、package、channel、asset、対象DSH、registryをHost側で検査します。候補を見たregistryと導入先を一致させ、変更後の候補を別の操作へ取り違えません。通信失敗・不正metadata・互換性不明を「最新版です」に変換しません。

checksumを使う経路では候補と実byteを固定し、redirect、累積サイズ、timeout、archive内のpath・manifestを確認します。checksum一致は発行者認証や実行成功の証明ではありません。build承認、互換性の例外、package候補の選択も別の判断です。

## 保存と操作の寿命

元のON/OFF・依存指定・bundle選択・設定・資格情報を確認し、対象profileの現在値を導入直前にも照合します。削除成功後に導入が失敗する状態を扱い、復旧操作が新しい設定を上書きしないようにします。許可したinstall scriptの外部副作用までtransactionで戻ると説明しません。

profile identity、接続世代、操作ID、候補と結果を結びます。連打防止だけでは他Clientとの競合を止めません。通信切断やtimeoutでは要求を自動再送せず照合します。`waitForInstall()` は進行中の要求用で、nullは成功・取消の証拠ではありません。永続履歴が必要な機能だけ、所有者に適した記録を設けます。

取消要求、`too-late` / `not-running`、実処理が止まった `cancelled` を区別します。画面のAbortやdialogを閉じたことを導入取消としません。

## 反映を確認する

候補、installed、running、Client asset、保存ON/OFFを分けます。`applied` は対象版・機能を確認し、`restart-required` は起動管理側の手順へ進みます。[再構成の条件](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/notes/implemented/architecture/2026-10-01-replace-changed-package-modules-on-recomposition.md)には置換不能moduleやmanifestだけの変更等の限界があり、必ず再起動・必ずHMRのどちらにも固定しません。

旧版→新版、OFF維持、並行更新、削除後の失敗、自己解除、切断後の照合を変更に応じて選びます。実Loaderの[package-reload試験](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/boot/plugin-manager/tests/package-reload.spec.ts)を参考に、manifest値だけでなく新しいコードが実際に返した値を観測します。
