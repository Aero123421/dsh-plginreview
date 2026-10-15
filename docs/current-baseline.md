# 現在のDSH開発基準

2026-10-15確認。基準は **DSH 0.2.1-alpha.3**、タグ `dsh-v0.2.1-alpha.3`、コミット `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`。これはプレリリースであり、安定版やnpmの `latest` と同義ではありません。

[公開Release](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.1-alpha.3)は2026-10-14 22:32:15 JSTに公開されています。別に取得した開発先頭は `571902028a75c64c1d767f4ae5fd099485f0ddf0`。公開版から16コミット先ですが、その差分を公開済みの契約へ混ぜません。旧基準alpha.2から公開版までの比較は852コミットです。件数は期間を揃えた開発速度の測定ではなく、比較APIのファイル一覧も全差分ではありません。

このページは今後の設計・レビューの入口です。2026-10-13の32リポジトリ調査、npm検査、自作7件の試験は当時の版に対する記録として残します。版を読み替えてalpha.3での検証済みにしません。適用先の版が違う場合は、対応するソースを読み直してください。

## 変更と再確認する経路

| 境界 | alpha.3で読む契約 | 狙う確認 |
| --- | --- | --- |
| インストールと更新 | HMR下で識別できる既存packageへの `installBundle()` は `already-installed`。削除・導入は別操作 | 同名再導入の拒否、削除後の新しい実行版、途中失敗、OFF維持 |
| 再構成と再起動 | 変更moduleを置換可能ならHMRで反映。Hostに固定されたmodule等は再起動が残る | 導入版だけでなく実行版・Client entry・workerを別々に観測 |
| 遠隔操作 | Hostが固定するprincipalと接続寿命のPeer、method/resource単位の認可 | owner、非owner、未登録principal、失効、直接Fetch、購読・一覧 |
| 認証情報 | storeがある構成は保存値優先。標準headlessはstoreを外す | 同名の保存値とenv、unset後のfallback、標準/変更済みprofile |
| Session | projectionによる読取り、参照所有、明示的なdurability checkpoint | 再開・fork・解除中の最終保存、古い読取り経路の新設禁止 |
| モデル入力 | プロセス固有値は記録されるruntime contextへ。既存履歴のprefixを保つ | 別port・別checkoutでresumeし、promptと送信payloadを比較 |
| UI | 390 CSS pxのviewportに加え実際のコンテナ幅、権限に合う操作表示 | 長い日本語、touch/hover、focus、拒否・保存中・結果不明 |

以下の確認は今回実行したruntime試験ではなく、更新する実装に合わせて選ぶ受入条件です。

## 更新を一回の成功に縮めない

[managerの契約](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/boot/plugin-manager/README.md)と[移行ガイド](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/docs/upgrade-guide/v0.2.1-alpha.2/plugin-install-over-installed/guide.md)を先に読みます。ガイドのディレクトリ名ではなく、参照コミットで所属する公開版を決めます。

既存のregistry名、local directory、保存済みのgit/tarball指定等を識別できるHMR経路では、上書き導入はpnpm開始前に拒否されます。未知のgit/tarballが後から同じpackageと判明する経路や、HMRなしの経路を一律に同じ挙動としません。削除不可のbundleへ自動削除を試す対策にもなりません。

削除→導入を採る場合は、削除されるpluginより長く生きる操作所有者、元の選択・設定、削除成功後の導入失敗、切断後の照合を設計します。これは自己更新のための設計判断です。自分のRPC内で自分を削除するコードを、移行ガイドから機械的に生成しません。詳しくは[更新ボタン](update-button.md)。

[再構成の実装記録](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/notes/implemented/architecture/2026-10-01-replace-changed-package-modules-on-recomposition.md)では、置換不能module、manifestだけの変更、worker内部cache等に条件が残っています。alpha.2のPWA再現を根拠に常にHost再起動を要求することも、alpha.3なら再起動不要と断定することも避けます。[実Loaderを使うテスト](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/boot/plugin-manager/tests/package-reload.spec.ts)は、評価された版と停止・公開・起動順を観測しています。今回このテストは読解のみです。

## 認証と認可を別に追う

[remote-access](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/api/remote-access/README.md)は、非ownerのRemote呼出しをprincipal、action、resourceで判断します。globalへの許可はSessionやWorkspaceへ自動継承されません。UIのaccess snapshotは引数を持たないため、表示上の許可だけで実行が許されるとは限りません。Host側の検査を残します。

[Peerの契約](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/notes/implemented/architecture/2026-10-12-peer-principal-and-remote-access.md)では暗黙のoperatorへのfallbackを外し、呼出し側がPeerを明示します。遠隔から送られた `principal` を信用してownerを作りません。Peerの破棄は後続呼出し・streamに効きますが、既に走るunary処理の取消を保証しません。既存のHTTP routeすべてがGatewayを通るわけでもありません。

CF、Remora、IM等は、この境界への接続を個別に確認する対象です。今回それらの現行実装をalpha.3対応済みと判定していません。remote操作の可否を一律に変更する指示でもありません。

## 資格情報はprofileの構成で変わる

[保存値優先](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/notes/implemented/architecture/2026-10-09-stored-credential-precedence.md)では、storeを持つ構成の参照解決は `.credentials.yaml` → process env → 起動cwdの `.env` → DSH_HOMEの `.env` です。piのprovider recordと名前付きreferenceも区別します。値の削除でenvの値が再び有効になることがあり、unsetと全経路のログアウトは同じではありません。

[標準headless](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/notes/implemented/architecture/2026-10-12-headless-environment-auth.md)はcredentials・authorization・deepseek-accountの行を無効にし、対話用storeを読み書きしません。storeを戻したcustom profileでは保存値優先に戻ります。Web、SDK、ACPへheadlessの省略を一般化しません。store不使用は、toolからのfilesystemアクセス禁止ではありません。試験には隔離したDSH_HOMEを使い、利用者の資格情報を削除して再現しません。

## 会話の意味と保存完了を守る

[Session](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/core/session/README.md)では、新規のproductionコードで `eventAt()`、`snapshotEvents()`、`ownEvents()` を追加する方針ではありません。Session由来の表示・計算は[projectionの規約](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/docs/defensive-patterns/conversation-and-session.md)を確認します。cache missを無条件の全履歴読取りへ変換せず、unknown等の状態を明示します。Hostに必要なcold readまで一律禁止する意味ではありません。

`appendPluginRecord()` は本体のexperimental package用で、独立pluginの保存入口ではありません。必要な保存は公開された所有serviceへ委譲します。`ctx.sessions.flush(session)` はawait可能なdurability checkpointですが、全イベントに追加するのではなく、保存完了を約束する操作で使います。保存serviceの解除前に、最終結果を出すconsumerを終える必要があります。

[動的なprompt値の修正](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/notes/implemented/bug-fix/2026-10-11-process-specific-prompt-values-in-runtime-context.md)は、portやcheckout変更で既存会話のprefixが変わり、署名付きthinkingの再開が失敗する例です。runtime contextへ移すだけでなく旧会話の記録済み段落を保っています。履歴・thinkingの削除、能力flagの水増し、無断のprompt固定を一般的な修復策にしません。

## 今回の適用範囲

更新したのは文書と開発用Skillsです。ソース、公開Release、PR状態、選んだ差分とテストコードを読みました。DSHや外部pluginのinstall script、実OAuth、モデル生成、実OS別UI、公開tarballの再検査は実行していません。自作7件の再導入・更新・共存試験も未実施です。

優先する追加検証は、7件共通の更新経路、CF/Remoraの呼出し元と権限、Piのprofile別認証とresume、PWA/Glass UIのClient反映と狭い画面です。実装修正は各リポジトリで別に扱います。

調査方法と最近の事例は[開発・不具合の分析](workflow/upstream-2026-10-15.md)、再調査用の基準は[baseline.json](../.agents/baseline.json)にあります。
