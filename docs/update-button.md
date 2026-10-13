# 更新ボタンの設計

この章は、第三者プラグインに更新機能を追加するときの設計指針です。DSH `0.2.1-alpha.2`の実APIと、自作7プラグインの更新実装・修正を材料にしています。実装ファイルと公開版は[一覧](own-plugins.md)、再現した競合と検証は[実装記録](update-implementation.md)へまとめています。

基本の処理は、Hostが更新候補を調べ、検証した配布物をDSHのplugin managerへ渡し、実行結果に応じて画面を更新する形です。プラグイン自身でpnpm起動・profile編集・tar展開を実装し直す必要はありません。

PWAにはタグ付きReleaseと更新UIが入りました。CFはプレリリースのソース配布、Remoraはworkspace内のbundleをtgzで配布するため、同じ候補取得・導入指定を全プラグインへ当てはめません。

## まず標準の機能を確認する

確認版の標準プラグイン画面は、Hostから`installTarget`が提供され、`availability`が`installation`ではない項目を更新対象にしています。更新前の`enabled`を次のインストールへ渡します。

これは、任意のGitHubプラグインの最新Releaseを調べる共通機能ではありません。`pluginManager.update()`や`checkForUpdates()`という汎用APIがある前提で設計しないでください。

第三者プラグインに独自の更新確認を付けるなら、候補取得はそのプラグインまたは更新サービスが担当し、導入はDSHに委譲します。

根拠: [標準画面のupdate処理](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/client/ui-plugin-manager/src/client/manager-store.ts)。

第三者の`dshmarket`には、plugin自身の更新ボタンが使うAPIがあります。確認版は`beta`で、DSH標準の汎用APIではありません。採用する場合のcapability確認と、操作記録の残る期間は[マーケットの比較](ecosystem/marketplaces-and-updates.md)にあります。

## 画面の状態と文言

更新確認とインストールを別操作にします。確認ボタンを押しただけではコードを差し替えません。

| 状態 | 表示・操作 |
| --- | --- |
| 未確認 | 現在の実行版と「更新を確認」 |
| 確認中 | 「更新を確認中…」。同じ確認の重複送信を防ぐ |
| 更新なし | 確認時刻と「更新はありません」 |
| 更新あり | 現在版 → 候補版、変更内容、対応DSH、「更新する」 |
| 互換性不明・非対応 | 理由とReleaseへのリンク。成功扱いで導入しない |
| ダウンロード・検証中 | 進行状態。キャンセルの可否を実処理と合わせる |
| 導入中 | 「インストール中…」。連打を防ぐ |
| 導入済み・再起動待ち | 「更新を適用するにはDSHを再起動してください」。Webではサーバー側の再起動を案内 |
| 実行版の反映を確認 | 「更新しました」と新しい実行版 |
| 失敗 | 失敗段階と対処。再試行はこの操作を起点にする |
| 通信切断・結果不明 | 「結果を確認中…」。導入要求を再送せず照合する |

HTTPやRPCが成功しただけで「更新しました」にしません。再読み込みボタンと更新確認ボタンのアイコンが同じでも、文言と処理を区別します。

標準詳細の導入版・Running表示も、設定UIが反映された証明ではありません。旧版の「Client packageではない」判定がHostに残るケースは、[更新後の反映と再起動](update-and-restart.md)を参照してください。

## Host側で候補を固定する

更新対象のrepository、package名、asset名の規則はHostの設定またはコードで管理します。Clientから任意URLやshell文字列を受け取り、それを管理者権限で実行する形にしません。

1. 固定したrepositoryの公開Releaseを取得する。
2. 応答のschema、タグ、版、draft・prerelease、assetを検査する。
3. 対象package・配布形式・DSH対応範囲を確認する。
4. 候補のRelease ID、版、URL、digestなどをHost側に保存する。
5. Clientには候補の表示情報と識別子を返す。
6. 「更新する」ではその識別子を受け取り、Host側の候補を再検査して使用する。

GitHubの`/releases/latest`は、公開された正式Releaseを取得するAPIです。任意のtag一覧やDSH互換版の自動選択ではありません。最新Releaseが非対応なら、その理由を表示するか、互換候補を選ぶ別の方針を実装します。[GitHubの仕様](https://docs.github.com/en/rest/releases/releases#get-the-latest-release)を参照してください。

版はSemVerとして検証・比較します。文字列比較では`0.10.0`と`0.9.0`を誤ります。不正な版を「更新なし」にせず、metadataの問題として表示します。prereleaseとbuild metadataの扱いも[SemVerの規則](https://semver.org/)に合わせます。

同じ候補確認はまとめ、短いキャッシュを使えます。明示的な再確認ではキャッシュを無効化します。APIの回数制限や通信失敗で候補が取れなかった場合を、「最新版です」に変換しません。404も、Releaseがない・repositoryがない・アクセスできない場合を区別できるとは限りません。

## ダウンロードを検証する

Host側で次を確認します。

- URLはHTTPSで、repositoryとassetの関係を確認したものに限る。
- redirect先も検査する。GitHub assetの正規redirectを考慮し、無関係な任意Hostへ転送しない。
- タイムアウトと、実際に読み込んだ累積byte数の上限を持つ。
- checksumファイルの上限、形式、対象ファイル名を検査する。
- tarballのSHA-256を照合してから、installerへ渡す。
- 保存先はHostの管理領域に限定し、パストラバーサル、symlink、同名ファイルの競合を防ぐ。
- 同じ名前のassetが複数ある、必要なassetがない、タグとpackageの版が違う場合は失敗にする。

`Content-Length`は上限確認の補助です。`arrayBuffer()`で全体を読み終えてから長さを確認する方法では、読み込み中のメモリー使用量を制限できません。streamを読みながら累積サイズを検査します。

tarballとchecksumを同じ侵害されたReleaseから取得できる場合、両方が置き換わる可能性があります。checksumは破損・取り違えの検出に使い、発行者確認まで保証するものとは説明しません。attestationを使う場合は検証するrepository・workflow・subjectも固定します。

独自のtar展開・package実行は避け、検証済みのファイルをDSH installerに渡します。bundleやpeer依存の判定もDSH側の結果を確認します。

## 実際のDSH APIと結果

確認版のHostサービスには、主に次のAPIがあります。

```ts
installBundle(spec, options): Promise<ChangeResult>
waitForInstall(requestId): Promise<ChangeResult | null>
cancelInstall(requestId): Promise<PluginInstallCancellation>
listBundles(): Promise<BundleInfo[]>
```

上の記述はAPIの要点です。実際の型、引数、exportは[DSHの型定義](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/types.ts)と[サービス実装](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/index.ts)に合わせてください。

`installBundle()`では、少なくとも更新前のbundleの`enabled`と、操作を識別する`requestId`を扱います。`enabled`を省略すると新規導入向けの有効化が既定になるため、OFFだったbundleを勝手にONにしないようにします。

`requestId`はDSH側のbranded型です。SDK・remote宣言の型に合わせて生成し、型の不一致を二重castで隠しません。build scriptの許可は更新候補の選択と別の判断です。`approvedBuilds`を自動で埋めて、無条件に許可しないでください。

| `ChangeResult`の値 | 意味・表示判断 |
| --- | --- |
| `changed` | 保存済み状態が変わったか。成功判定そのものではない |
| `application: applied` | 適用結果。errorと対象版を確認し、実行版の取得へ進む |
| `application: restart-required` | 現在のプロセスへの適用には再起動が必要 |
| `application: overridden` | 上位の設定などにより、期待した状態になっていない |
| `application: failed` | errorと失敗段階を表示 |
| `application: cancelled` | installer側でキャンセルが確定した状態 |
| `version` | 導入されたbundleのmanifest版。候補版との一致を確認 |
| `packageResult` | package処理の終了状態・診断。exit codeだけで最終成功を決めない |

`ctx.remote.pluginManager`経由のClient応答は、`ok`と`value`またはerrorを持つremote結果です。Hostでサービスを直接呼んだ戻り値の`ChangeResult`と混同しません。

新規導入の`inspect()`は更新確認APIではありません。registry/pathの同名パッケージには`already-installed`が返る場合があります。git/tarballの検査が受理されても、その段階でbundle metadataや互換性が判明しているとは限りません。

## 切断しても導入を二重にしない

Clientの状態は、接続と要求の世代で管理します。古い確認・失敗応答が新しい接続へ戻らないようにします。

導入中にClientの接続が切れたら、同じ`installBundle()`を送信し直しません。まず`requestId`で`waitForInstall()`を使い、必要に応じてbundle一覧、導入版、現在の実行版を照合します。

確認版の`waitForInstall()`は進行中の要求を待つAPIです。完了済みの結果を永久に保存する機能ではありません。返り値`null`は結果を取得できない状態で、成功・失敗・取消の証明にはなりません。

確実な履歴表示が必要なら、更新処理を所有するHostサービスに操作記録を残す設計が必要です。同じ版が入っていることだけでも、今回の処理が成功した証明にはならない場合があります。

`plugin-manager/install-state`・`output`の通知はrequestIdと照合します。画面全体の一覧再取得で、進行中操作の結果まで捨てないようにします。

### 同じブラウザーから別profileへ接続する

導入要求を送る前に操作IDを決め、保存します。ただし、originだけで保存先を分けると、同じURLでprofileを切り替えた際に別profileのIDを持ち込みます。認証済みHostの不透明なprofile識別子を取得してから、そのprofileの保存記録を読みます。

導入要求にも期待するprofile識別子を含め、Hostで一致を確認します。古いprofile向けの遅延要求・成功・失敗は、新しい接続の状態へ反映しません。保存記録には操作ID・候補・結果を置き、資格情報や個人のpathを混ぜません。

Hostが保持する最新操作を優先し、ブラウザーの古いIDで上書きしないようにします。最初の応答を失った場合は、同じprofileの保存IDで照合します。未確定操作は候補版が変わっても先に照合し、新しい導入で消しません。実際の修正は[Pi #11](https://github.com/Aero123421/dsh-pi-login/pull/11)、[Search #4](https://github.com/Aero123421/dsh-search-providers/pull/4)、[日本語パック #4](https://github.com/Aero123421/dsh-japanese/pull/4)にあります。

### 導入直前と結果受信後に確認する

receiptの保存など、最後の非同期処理を待つ間にも、別Clientが新しい版を入れる場合があります。installerを呼ぶ直前に導入元・導入版・ON/OFF・解除状態を読み直し、既に同じ版または新しい版なら古い候補を導入しません。

結果を受け取った後は、`application`に加え、対象packageのmanifest版、`installed`、`error`、`readOnly`を照合します。不一致を再起動待ちや更新完了にせず、結果不明として扱います。installerが取消を確定した場合は、取消に伴うpackage processの非ゼロ終了より`application: cancelled`を優先します。

## キャンセルと自己更新

ダイアログを閉じること、HTTP要求をAbortすること、Hostの導入をキャンセルすることを分けます。`cancelInstall()`の`too-late`や`not-running`を「キャンセル完了」に変換しません。

自己更新では、そのプラグインのClient・Hostが解除される場合があります。更新操作の所有者を、解除される画面コンポーネントだけに置くと、結果の照合ができなくなります。DSH managerや、更新対象より長く生きるサービスに導入状態を持たせます。

確認版では既存パッケージの差し替えは再起動要求になります。将来のHMR挙動が変わっても、RPCが必ず最後まで返る前提を置かず、再接続して実行版を確認できる設計にします。

## 失敗時の保存状態

DSH installerは、一部の失敗・取消時にprofileのmanifestとlockfileを復元します。ただし、ダウンロード済みファイルや、許可したlifecycle scriptの副作用まで一括で巻き戻す機能ではありません。後段の適用失敗では保存変更が残る場合もあります。

結果に従い、保存された依存指定、bundle選択、導入版、実行版を再確認します。検証済みtarballをローカルパスで渡し、profileの依存指定がその`file:`を参照する場合、まだ必要なファイルを掃除しないでください。

## 処理の分担例

次は設計上の擬似コードです。`updates.*`は、この章で提案する自前サービスの操作名で、DSHに存在するAPI名ではありません。

```text
Client: 更新を確認
  → Host updates.check()
    → 固定repoのmetadata取得・検査
    → 候補IDと表示情報を返す

Client: 候補IDを選んで更新
  → Host updates.install(candidateId, operationId)
    → 現在の権限・候補・bundle選択を検査
    → assetを上限付きで取得・checksum検証
    → DSH installBundle(verifiedPath, { enabled, requestId })
    → ChangeResultを記録・返却

Client: 切断後に再接続
  → Host updates.reconcile(operationId)
    → 進行中操作・導入版・実行版を照合
    → 失敗／結果不明／再起動待ち／適用確認を表示
```

更新を許す場所は、DSHの権限モデルと配備方法に合わせます。URLが`localhost`だからという理由だけで管理操作を許可しません。Remoraのローカル限定処理は、そのプラグイン固有の方針です。

## 旧Remoraの問題と修正後の参照先

旧`0.1.1`の[updates.ts](https://github.com/Aero123421/dsh-remora/blob/ed7e99736b0cc8e72a956722fb6fc72fda927239/packages/dsh-remora/src/core/updates.ts)は、固定repositoryのRelease取得、配布名の照合、SHA-256検証、Host側への保存を実装していました。一方、導入結果を待たずに返す問題などがありました。以下は旧版のレビュー項目です。

- 無効な版を「同じ版」と扱う比較。
- 全体読み込み後にサイズ検査するダウンロード。
- metadataとredirect先の検証範囲。
- [installUpdate()](https://github.com/Aero123421/dsh-remora/blob/ed7e99736b0cc8e72a956722fb6fc72fda927239/packages/dsh-remora/src/core/remora.ts)が、installerを待たずにpathを返す処理。
- `ChangeResult`の失敗・再起動要求と、更新前のbundle状態の扱い。

pathが返ったことは「ダウンロードが用意できた」の確認であり、「新しい版が動いた」の確認にはなりません。

[PR #6](https://github.com/Aero123421/dsh-remora/pull/6)で結果照合、profile別の記録、導入済み版との比較、上限付きの取得と実manifestの検査を修正し、`0.1.3`で公開しました。現在の例には[updates.ts](https://github.com/Aero123421/dsh-remora/blob/b7d6d85436806f6b6ac16736e5fb9df2f82cf406/packages/dsh-remora/src/core/updates.ts)と[remora.ts](https://github.com/Aero123421/dsh-remora/blob/b7d6d85436806f6b6ac16736e5fb9df2f82cf406/packages/dsh-remora/src/core/remora.ts)を参照します。過去の指摘を、現在も未修正の問題として案内しません。

## 必要なテスト

候補なし、無効metadata、非互換、asset欠落、checksum不一致、redirect拒否、サイズ超過、タイムアウト、二重クリック、OFF状態の維持、導入失敗、再起動要求、切断後の照合、自己解除を確認します。

成功経路では、再起動後にプラグイン自身が返す実行版まで確認します。失敗経路では、旧版の設定・資格情報・選択状態がどう残ったかも確認します。
