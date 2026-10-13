# 更新後の反映と再起動

DSH `0.2.1-alpha.2`では、プラグインの新しいファイルが導入されても、動いているHostやClientに反映済みとは限りません。Web版では、DSHサーバーを再起動してからブラウザーを再読み込みし、実行版と設定欄を確認します。

## 導入版・実行版・画面を分ける

| 確認するもの | 分かること | それだけでは分からないこと |
| --- | --- | --- |
| profileのpackage manifest・標準詳細の版 | 新しい配布物が導入された | 新しいHost/Clientが動いているか |
| Host componentのRunning表示 | Hostのプラグインが有効な状態 | 新しく追加したClient entryや設定欄が登録されたか |
| プラグイン自身が返す実行版 | その応答を返したHostのコードの版 | Clientの設定欄・assetも正常か |
| 設定欄・更新操作・機能の実動作 | 新しい画面と対象機能が使える | 未確認のOS・API・他プラグインも使えるか |

HTTP要求が成功したことや、標準詳細の版が新しくなったことだけで「更新しました」と表示しません。`restart-required`は、新しい実行版の確認前の状態です。

## PWAで再現した条件

2026-10-13に、隔離したWeb profile、DSH `0.2.1-alpha.2`、LinuxのChromiumで次の順序を確認しました。旧版は[0.1.0のコミット](https://github.com/Aero123421/dsh-pwa/tree/135828c05e8fe5fc4af2fefdf891564c686638a9)、更新先は[v0.2.0](https://github.com/Aero123421/dsh-pwa/releases/tag/v0.2.0)です。

| 操作順 | 確認結果 |
| --- | --- |
| PWA `0.1.0`を導入してDSHを起動 | PWAの独自設定欄はない。旧版はClient entryを持たない |
| サーバーを動かしたままCLIで`0.2.0`へ更新 | profileのpackage manifestは`0.2.0`になる |
| ブラウザーを再読み込みして設定を開く | PWAの独自設定欄はまだ出ない |
| DSHサーバーを終了し、同じprofileで起動し直す | PWA設定欄、実行版`0.2.0`、「Check for updates」を確認できる。ページ例外はない |

利用者の画面でも、標準詳細は`0.2.0`・Runningなのに設定欄がない状態でした。上の操作順は別の隔離環境で確認したもので、利用者のサーバーを操作した記録ではありません。最新`0.3.0`では設定名が「PWA・モバイル」に変わりますが、この再現結果を`0.1.0`→`0.3.0`の再試験結果とは扱いません。

## 原因を持つ側

確認版のHostは、packageのClient metadataをLoader specifierと所有ツリーのbase URLごとにキャッシュします。「Client packageではない」という判定も、再起動まで残ります。同じソースのfiberを再起動しても、metadataの再走査にはなりません。

そのため、旧版に`dsh.client`がなく、新版で初めて設定UIを追加した場合、ブラウザーの再読み込みだけではHostの判定が変わりません。新しい配布物にClient entryがあるかを確認したうえで、Hostプロセスを再起動します。無効化・再有効化や、ブラウザーキャッシュの削除を代わりの操作として案内しません。

根拠はDSHの[Client modulesの仕様](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/docs/subsystems/client-modules.md)、[metadataキャッシュ](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/client/modules/src/index.ts)、[既存packageの差し替え結果](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/index.ts)です。

読み込み仕様はDSH本体にあります。プラグイン側では、初めて設定UIを追加するReleaseの再起動条件をREADME・Releaseノートへ書き、既存利用者の更新を試す必要があります。

## Web利用者への案内

1. 導入結果と対象profileを確認する。`ERR_PNPM_ADDING_TO_ROOT`なら、まず[導入条件](update-implementation.md#dshとpnpmの導入条件)を確認する。
2. 実行中のタスクと保存待ち編集を確認する。停止は、そのDSHを起動したターミナルまたは管理サービスから行う。
3. 終了を待ってから、同じprofile・環境変数・公開URL・portで起動し直す。
4. ブラウザーを再読み込みし、プラグインの実行版、独自設定欄、更新操作、保存設定を確認する。

別PCで動かしているDSH Webでは、再起動するのはサーバー側です。ブラウザーを閉じる操作や、PWAショートカットを入れ直す操作では代わりになりません。新しい認証URLが必要になった場合は起動側の案内に従い、token付きURLをIssueへ貼りません。

## 新しいClient entryを追加するときの検査

新規導入と、旧版からの更新を別々に試します。旧版が動いている間に更新し、ブラウザー再読み込み前後・Host再起動後の導入版、実行版、設定欄を記録します。新しいClient entry・`dsh.client`・inject・同梱assetの変更をしたときは、この経路を含めます。

7件の初期公開版の共存結果は[実装記録](update-implementation.md)にあります。PWAのモバイル表示とGlass UIの後続変更を併用する場合は、左右ドロワー、設定ナビ、Portal、片方のOFF後の復元も改めて確認します。

## 再起動ボタンを作る場合

ここからは未実装の設計案です。確認版には、プラグインから終了を依頼する`ctx.appExit`があります。CLIの[終了API](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/cmdline/src/index.ts)は[起動処理のshutdown](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/apps/cli/src/profile-boot.ts)へつながっています。これは停止の仕組みで、Webサーバーを起動し直す共通APIではありません。

Web版の再起動ボタンには、DSH終了後も動く起動役または既存の管理サービスが必要です。認証済みの管理操作から要求し、現在のprofileと起動条件を維持して終了・再起動・readinessを確認します。ブラウザーは再接続後に実行版を照合します。任意のshell文字列をClientから受け取る仕組みにはしません。

再起動を担う仕組みがない環境では手動手順を表示します。単に`appExit`を呼ぶボタンを「再起動」と表示すると、DSHが停止したままになるためです。Electronの再起動はアプリ側の起動管理に属し、このWeb向け設計だけで対応済みとは扱いません。
