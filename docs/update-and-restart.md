# 更新後の反映と再起動

現在の基準はDSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`です。[Release](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.1-alpha.3)は、更新しても旧コードが動く問題への修正を含みます。ただし「全部HMRで済む」ことを意味しません。

## 導入版・実行版・画面を分ける

| 観測 | 証明できること | 別に確認するもの |
| --- | --- | --- |
| package manifest | 保存された配布物の版 | 実行中のHostコード |
| Running | componentが有効 | 新版か、追加Client entryがあるか |
| pluginが返す実行版 | 応答したコードの版 | Client asset、worker、対象操作 |
| 新しいUI・機能の実動作 | 検査した入口の動作 | 別OS、別profile、未確認の組合せ |

`application: applied` は実行版・対象機能の確認へ、`restart-required` は起動管理側の手順へ進みます。`failed`、`cancelled`、`overridden`、結果不明を成功へ畳みません。先に既存packageの導入が拒否された場合は、[更新ボタン](update-button.md)の操作を見直します。

## PWAで再現した条件

2026-10-13、alpha.2でPWA `0.1.0`→`0.2.0`を更新した再現は[当時の記録](update-and-restart-alpha2.md)に内容を変えず保管しています。Host再起動まで設定欄が出なかったという結果を、alpha.3で同じ再現を実施した結果にはしません。

## 原因を持つ側

[再構成の実装記録](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/notes/implemented/architecture/2026-10-01-replace-changed-package-modules-on-recomposition.md)では、profile内やlinked先の変更されたmoduleと静的なimport元を照合し、置換可能なものをevict・再構成します。古いmetadataも変更fileの所有関係に沿って無効化します。

一方、Hostに固定されたmodule、管理外のplugin、packageの移動、module比較の失敗等には再起動条件が残ります。manifestだけの変更、worker内の私有cache、動的import経路にも限界があります。manager外のCLI変更が即座に再構成されるとも限りません。旧コードへ必ず自動復帰するtransactionではありません。

したがって、常に再起動させる古い回避策と、再起動を不要とする新しい断言の両方を避け、実際の適用結果に従います。ブラウザーだけの再読込みとHostの再構成・再起動は別です。

## Web利用者への案内

1. 対象profile、導入結果、元の保存状態を確認する。導入拒否やpackage処理の失敗を再起動で直ると決めつけない。
2. 再起動が必要なら、実行中taskと保存待ち編集を確認し、そのDSHを起動したterminalまたは管理serviceから停止する。
3. 終了を確認して、同じprofileと必要な起動条件で起動する。元の資格情報・設定を消して作り直さない。
4. ブラウザーを再接続し、実行版・Client entry・設定・対象操作を確認する。

別PCのWeb利用ではサーバー側の再起動です。PWA shortcutを入れ直す操作では代用しません。認証URLのtokenをIssueへ貼りません。標準profileを再生成する操作は、保存設定や追加pluginを置き換える可能性があるため、通常の再起動案内へ混ぜません。

## 新しいClient entryを追加するときの検査

旧版実行中の更新と新規導入を別々に試し、導入版、Host実行版、Client entry、worker、実操作を記録します。同じ版番号でfileだけ変わる場合やmanifestだけの変更も、変更内容に応じて選びます。

HMRでは新版の起動に加え、旧版のtimer・listener・CSS・process・最終保存が正しく終了することを確認します。PWA/Glass UI併用は左右panel、Portal、片方OFF後の復元を対象範囲で見る必要があります。今回のalpha.3実機試験・7件共存は未実施です。

## 再起動ボタンを作る場合

停止要求は再起動の保証ではありません。DSH終了後も生きる起動役や既存管理serviceがなければ手動手順を表示します。profile・起動条件・readiness・再接続後の実行版を確認し、Clientから任意shellを受け取る方式にしません。

alpha.2の `appExit` を使う設計案と根拠は[当時の記録](update-and-restart-alpha2.md)にあります。この資料更新では、新しい再起動serviceや全Desktop対応を実装したわけではありません。
