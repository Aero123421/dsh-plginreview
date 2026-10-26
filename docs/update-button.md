# 更新ボタンの設計

現在の基準はDSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`です。この章は設計・確認手順であり、自作7件のalpha.3対応を実装・試験済みとする記録ではありません。2026-10-13の詳細な修正履歴は[alpha.2版のガイド](update-button-alpha2.md)に保管しています。

## まず標準の機能を確認する

[managerのREADME](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/boot/plugin-manager/README.md)と[既存packageへの導入ガイド](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/docs/upgrade-guide/v0.2.1-alpha.2/plugin-install-over-installed/guide.md)を確認します。標準UI、第三者market、plugin独自の更新処理は別の所有者です。存在しない汎用 `pluginManager.update()` を想定しません。

HMR有効時、識別できる既存packageへの `installBundle()` は `already-installed` で拒否される経路があります。以前の「同じpackageを導入すると常に再起動待ちになる」という前提では設計できません。削除→再導入が必要な経路では、元の選択・設定、操作所有者、途中失敗からの回復を先に決めます。

## 画面の状態と文言

| 状態 | 確認するもの |
| --- | --- |
| 未確認・確認中・候補あり | 実行版、候補版、channel、確認時刻 |
| 互換性不明・拒否 | 確認できない条件。更新なしと区別 |
| 削除中・導入中 | 操作ID、profile、取消可否 |
| applied | 対象版・機能・Client反映の確認へ進む |
| restart-required | 起動管理側の再起動手順と、再接続後の確認 |
| failed・cancelled | 実処理の確定結果と残る保存状態 |
| 結果不明 | 導入要求を再送せず、既存操作と状態を照合 |

HTTP成功、manifest版、Runningのどれか一つだけで「更新しました」にしません。詳しい再構成条件は[反映と再起動](update-and-restart.md)へ分けます。

## Host側で候補を固定する

repository、package、tag、channel、asset、対応DSH、registryを検査します。候補を見た配布先と実際の導入先を揃えます。Clientから任意のshellや未検証URLを受けて実行しません。

SemVer、draft/prerelease、互換性と配布形式を照合し、候補IDを固定します。通信失敗・アクセス不能・不正metadataは「最新版です」にしません。ローカル開発pathを無断で公開版へ置き換えません。

## ダウンロードを検証する

必要な配布経路ではHTTPS、正規redirect、累積byte上限、timeout、checksum、archiveのpath、実manifest・patch・entryを確認します。checksum一致は作者認証と同じではありません。独自installerでprofileを編集せず、検証済みの導入元をmanagerへ渡します。

build scriptの承認や互換性例外は候補選択と別操作です。拒否を勝手に外したり、private registryの名前を公開mirrorへ自動送信したりしません。

## 実際のDSH APIと結果

`installBundle()`、`removeBundle()`、`waitForInstall()`、`cancelInstall()` 等は対象版の型とREADMEを確認します。Host直呼出しの結果とClient Remoteの結果wrapperを混同しません。`changed` やprocessのexit codeだけで最終状態を決めません。

HMR下の既存package判定、HMRなし、識別できないgit/tarballの検査後、削除不可bundleでは条件が異なります。inspectで受理されたこともインストール・有効化・機能成功とは別です。

## 切断しても導入を二重にしない

要求前に操作IDとprofileを確定します。切断時は進行中の要求を照合し、`waitForInstall()` のnullを成功・失敗・取消に補完しません。このAPIは完了済み結果の永続台帳ではありません。

### 同じブラウザーから別profileへ接続する

originだけで操作記録を分けず、認証済みHostが示すprofile identityを照合します。古い要求が新しいprofileへ届いた場合は変更前に拒否します。未解決操作を、新しい候補が出たという理由で消しません。永続履歴が必要な機能だけ、所有者に適した保存を設けます。

## キャンセルと自己更新

UIを閉じる、HTTPをAbortする、導入を取り消す、実processの停止が完了する、という状態を分けます。`too-late` と `not-running` は取消完了ではありません。

自己更新はそのHost/Clientを解除する可能性があります。自分のRPCで `removeBundle(self)` を呼び、続く処理が必ず動くと仮定しません。標準manager・更新対象の外側の所有者に処理を委ねるか、対応する手動操作へ案内します。この所有者選択は設計判断であり、すべての環境で同じ外部updaterを新設する要件ではありません。

## 失敗時の保存状態

削除成功→導入失敗は一つのtransactionではありません。元のpackage指定・ON/OFF・設定・資格情報を確認し、復旧に使う配布物を特定します。別Clientの変更を古いsnapshotで上書きしません。

managerのmanifest・lockfile復元は、許可したinstall scriptの外部副作用の取消を保証しません。適用失敗後も保存変更が残り得るため、package、bundle選択、実行版を再照合します。`file:` が参照中の配布物を後片付けで消しません。

## 処理の分担例

```text
候補の検査と選択
  → profile・現在権限・現在版・元の選択を確認
  → 現行manager契約に合わせ、操作所有者が削除と導入を管理
  → 失敗時は残る保存状態・復旧条件を表示
  → appliedなら実行版とClientを確認
  → restart-requiredなら起動管理側へ案内
  → 切断時は同じ操作の照合を優先
```

これは擬似的な順序で、新しいDSH API名を定義するものではありません。更新対象のpluginより操作所有者が長く生きる必要があるか、実際の再構成経路で確認します。

## 旧Remoraの問題と修正後の参照先

旧版の問題、2026-10-13の修正PR、配布経路、検査条件は[alpha.2版](update-button-alpha2.md)と[当時の実装記録](update-implementation.md)を参照します。その成功をalpha.3の更新経路へ継承しません。

## 必要なテスト

新規導入と旧版更新を分けます。既存packageの拒否、削除成功後の失敗、自己解除、ON/OFF維持、同時操作、profile切替、途中切断、取消の時機を選びます。成功時は実行版・機能・Clientを、失敗時は保存された設定と依存を確認します。

manager mockの成功だけで現行Hostに準拠したと判断しません。[本家の実Loader試験](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/boot/plugin-manager/tests/package-reload.spec.ts)を参考に、変更した公開経路を通す必要があるかを決めます。今回、この受入試験は未実行です。
