# 権限・保存・外部通信

Host pluginはDSHプロセスの中で動きます。Sessionのtool sandboxだけで、インストールしたHostコードやその依存のすべてが隔離されるとは考えません。導入するpackageと、それが提供する管理操作の境界を確認します。

## 現在の権限で判断する

Clientの表示や要求開始時の権限だけではなく、Hostが処理する時点の権限を検査します。待機する処理では、結果取得・通知時に権限を縮小されている場合もあります。

Remoraでは、`task.get`・`task.wait`、所有者の操作、緊急停止、scheduleの解除を同じ境界で調べました。権限を縮小したら、既存の待機処理や実行対象にどう反映するかも決めます。

読み取り、変更、権限拡大、停止を区別します。「停止できる」と「新しい権限を付与できる」は同じではありません。

## ローカル判定とreverse proxy

`Host: localhost`は要求者が指定できる値です。Remoraでこの値だけによる判定をやめ、socketの実接続元も検査しました。

Origin、Host、forwarding header、実接続元、DSH側の認証を、配備方法に合わせて扱います。remote addressがloopbackでも、SSH forwardやreverse proxyを通した遠隔ユーザーの場合があります。ヘッダーの組合せだけで、端末の物理的な所有者まで証明できるとは説明しません。

DSHの既存WebServer・認証・routeを使える機能に、別の無認証サーバーを追加しないようにします。PWAの静的manifestやiconを公開することと、操作APIを公開することは区別します。

UI向けのファイル操作も、Sessionのworkspace制限を自動で引き継ぐとは限りません。[Better Sidebarの調査](ecosystem/ui-and-runtimes.md)では、workspaceという関数名を残しながら、Host userの到達できるpathへ広げている仕様を確認しています。名前と実際の権限を照合します。

## 保存を完了させる境界

設定や資格情報は、所有するサービスの保存APIを使います。原子的なファイル置換と、複数processによるread-modify-writeの排他は別です。

```text
ロック取得
  → 最新の保存データを読み直す
  → 入力・権限・形式を検査
  → 変更して保存
  → 必要なflushを待つ
ロック解放
```

ロックの外で読んだ古いsnapshotを、そのまま書き戻すと更新を失います。ロック待機中の解除、所有processの異常終了、保存失敗、teardownも確認します。

監査ログなど「書いた後に読める」契約のRPCでは、非同期queueへの追加だけで完了にしません。読み取りが必要な保存完了を待つようにします。

## 資格情報の保存先を変える

keychainとfallback fileが両方ある場合は、優先順位、移行、更新、ログアウト、古い値の削除を一緒に決めます。新しいrefresh tokenを保存しても、次回起動で古いkeychainを優先すると壊れます。

OFFと資格情報削除を分けます。診断やsnapshotには、値ではなく「設定済み」「有効期限」「保存先の種類」など必要な状態を返します。URLにもtokenや個人情報が入る場合があるため、custom URLを無条件に診断へ含めません。

OS別のkeychain処理は、Linuxで通っただけでWindows・macOSも確認済みにしません。

## 再送と冪等性

ネットワークの再送で同じ操作を重複実行しないよう、安定した操作IDを持ちます。同じIDで本文が違う場合は拒否します。再起動をまたぐ必要がある操作は、メモリー上のMapだけで済ませません。

ただし、別サービスの処理と記録保存が別transactionなら、その間の異常終了が残ります。「exactly once」と表現する前に、途中停止からの復旧・照合・重複処理まで確認します。

削除や復旧処理は、pluginが所有する対象だけに限定します。フォルダー名の一致だけで、利用者の既存ディレクトリを消しません。cloneなど時間のかかる処理では、実際に作成する直前にも配置先を検査します。

## URLと外部API

ユーザー指定URLについて、誰がアクセスするかを確認します。DSH Hostが直接fetchする場合と、外部のextract APIへURLを渡す場合では、ネットワーク境界と情報の渡り先が違います。

ローカル・private IPに見えるURLを文字列で拒否するだけでは、DNS解決やrebinding、redirect先まで検査したことにはなりません。Hostが直接fetchする経路でSSRF対策が必要なら、名前解決後の接続先とredirectにも同じ制約を適用します。

検索プラグインの`publicUrl()`は構文上の検査です。これだけを完全なSSRF防止機構として案内しません。

外部APIにはtimeout、累積responseサイズ、同時要求数の上限を設けます。待機queueでキャンセルされた要求も取り除きます。失敗・切断後にreader、timer、socket、processが残らないことを確認します。

## 解除時に確認する資源

| 資源 | 確認 |
| --- | --- |
| Cordis service・event・tool | 登録が解除され、再有効化で二重にならない |
| 通信・待機要求 | Abortと完了待ち。解除後のcallbackが状態を書き戻さない |
| timer・watcher・observer | 停止し、非同期処理から復活しない |
| subprocess | 親だけでなく所有するprocess treeが終了する |
| 保存queue | 必要な保存・flushが終わるか、失敗が報告される |
| DOM・CSS | pluginが追加したものだけを戻す |
| lock・temporary file | 解放する。まだ依存指定が参照する配布物は消さない |

## 根拠

- [Remoraの14件修正](https://github.com/Aero123421/dsh-remora/pull/1)
- [監査ログの保存待ち修正](https://github.com/Aero123421/dsh-remora/pull/2)
- [検索プラグインのHTTP処理](https://github.com/Aero123421/dsh-search-providers/blob/ca7a1e484cd25e1812fc333c85b0185a40659e49/src/http.ts)
- [DSH plugin managerの権限と失敗処理](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/README.md)
