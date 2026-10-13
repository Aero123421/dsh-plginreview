# ブラウザー・画像・記憶・別アプリ接続の深掘り

2026-10-13にdefault branchのソースを固定して読んだ追補です。[既存の比較](browser-and-routing.md)、[providerとmemory](providers-and-memory.md)、[配布確認](package-checks.md)の紹介を繰り返さず、利用者の操作がmodel入力・保存・解除へ届く順序を追います。BrowserSkill、Modlens、Memsearchは前回と同じSHAでした。Open Designは前進しているため、前回の固定版と区別します。

本体repositoryのstarはDSH leafの利用数ではありません。EverOSはtopicを残したままDSH実装を別repositoryへ移しており、発見された本体と導入するbundleが一致しない実例です。この章では人気を品質や互換性の順位へ換算しません。

## 固定版と導入境界

| repository / 固定SHA | 実際のDSH package | 導入・buildとpeerの境界 |
| --- | --- | --- |
| Tencent/BrowserSkill / `4c8616b12273ac5a22ce4adb494cac941e20de2a` | `packages/dsh-plugin-browserskill`、`@wxg-prc-cpg/browser-skill-dsh-plugin@0.3.2` | native bundle。Host `lib/index.mjs`、Client `lib/client.cjs`はbuild生成。別にbsk CLI・daemon・拡張が必要。DSH peerは `^0.1.5-rc.3 \|\| ^0.2.0-rc.1` |
| liustack/modlens / `1d8b20fc97a33b456e0d500037d4d66febaeb80a` | root `@liustack/modlens@3.26.6` | native bundleとCLI/Skillを併有。DSH entryは`dsh/index.js`、CLIは`dist/main.js`。DSH peer宣言なし |
| zilliztech/memsearch / `09e07d86b31ff81938b4f44a57099b6a9fc8723f` | `plugins/dsh`、`@zilliz/memsearch-dsh@0.1.6` | native bundle、plain JSとClient。npm runtime依存は空でも別Python CLI・bash・Milvus/embeddingが必要。`dsh-llm:*` |
| volcengine/OpenViking / `6c1107527af4243055640fbb0d7d7bdcb54dc75c` | `examples/dsh-memory-plugin`、`@openviking/dsh-memory-plugin@0.5.24` | native bundleからstdio MCP proxyとSkillをmount。OpenViking HTTP serverは別資源。共有moduleはprepack同期。DSH peer `>=0.1.0-rc.6 <1.0.0-0` |
| MemTensor/MemOS / `a7367d07e55db61099f7b4e2c1108bc5831a24f3` | `apps/memos-local-plugin`、`@memtensor/memos-local-plugin@2.0.16-beta.1` | native bundleのpatchはcompiled DSH adapter subpathを指定。SQLite native module、local embedding、viewer・postinstallを持つ。DSH peer `>=0.1.0-rc.5 <0.2.0` |
| EverMind-AI/EverOS / `a345d08e5cdfc8db77504da89fffaf3aee43018b` | **本体に現行DSH leafなし** | 現行の導入元は次行。serverの記憶機能とbundleの対応を別々に調べる |
| EverMind-AI/plugins / `3318dc1a2afcef3d3d804963941e8ce0bf9a3879` | `dsh`、`@everos-ai/dsh-plugin@0.1.0` | native bundle。`lib/index.js`はprepareで生成。DSH peer `>=0.1.0-rc.6 <0.2.0-0`。serverは別起動 |
| nexu-io/open-design / `1343f374c63d7866f4f3ff5d48ef038eba647f1b` | `packages/dsh-runtime`、`@open-design/dsh-runtime@0.1.0` | native bundleを別アプリの専用profileから起動。`dist/index.js`はbuild生成。cmdline直接依存は`0.1.1-rc.2`、peerは下限中心で上限なし |

根拠は各manifest: [BrowserSkill manifest](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/package.json#L1)、[Modlens manifest](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/package.json#L1)、[Memsearch manifest](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/plugins/dsh/package.json#L1)、[OpenViking manifest](https://github.com/volcengine/OpenViking/blob/6c1107527af4243055640fbb0d7d7bdcb54dc75c/examples/dsh-memory-plugin/package.json#L1)、[MemOS manifest](https://github.com/MemTensor/MemOS/blob/a7367d07e55db61099f7b4e2c1108bc5831a24f3/apps/memos-local-plugin/package.json#L1)、[EverOS leaf manifest](https://github.com/EverMind-AI/plugins/blob/3318dc1a2afcef3d3d804963941e8ce0bf9a3879/dsh/package.json#L1)、[Open Design manifest](https://github.com/nexu-io/open-design/blob/1343f374c63d7866f4f3ff5d48ef038eba647f1b/packages/dsh-runtime/package.json#L1)。表のpeerは宣言の転記であり、全版での起動成功を意味しません。MemOSはソースmanifestがbeta版なのにIssueはnpm 2.0.19/2.0.20を扱います。同じ数字の版を前提にして比較しません。OpenVikingはソースleafにgenerated shared moduleがないため、checkout単体のimportと配布tarballを分けます。配布物の追加調査では公開npm tarballのintegrity・具体entry・patchを照合しました。これは起動・実通信の検証とは別です。

## BrowserSkill: login済みbrowserへ届くまでに三つの所有者を通る

呼出しは「model tool → DSH session queue → bsk childのJSON出力 → daemon RPC → extension/CDP →既存profile」です。DSHはbrowser本体を所有せず、pluginが作成したtask sessionとborrowしたtabの返却を管理します。profileを選ぶ操作は、接続中のbrowser instanceを選ぶ操作であり、空の隔離browserを起動する契約ではありません。login状態を使うtoolではページ内容だけでなく、書込み・download・uploadもユーザーのbrowser権限を通ります。[CLI runner](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/runner.ts#L77)、[Session registry](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/sessions.ts#L1)

lazy toolは既定で有効です。成功した`browser-skill`呼出し、または履歴の成功記録を検出してsuiteを登録します。重要なのは**process lifetime**で公開する点です。一つのSessionで解禁したtoolが同じHostの別Sessionにも見える設計であり、Sessionごとの権限grantではありません。schema節約とアクセス制限を同じ仕組みとして取り込まないことが条件です。[公開範囲と履歴の検出](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/lazy-tools.ts#L1)

取消には異なる三段階があります。待機中taskはqueueがrejectし、実行中taskはrunnerがCLIへ停止を伝え、CLIはRPC cancelでbrowser側の完了と突き合わせます。Windowsではstdin EOF、他OSではSIGINTを送り、その後に強制killします。実行期限とは別に、`exit`後のstdout drainにも上限を置くのは、daemon孫processがpipeを保持して`close`が来ない条件の対策です。取消完了を「クリックが起きなかった」と同一視しない設計が必要です。[CLI runner](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/runner.ts#L77)

start journalは`process.cwd()`とbsk pathをhashしたscope、PIDとUUIDのowner directory、request IDを保存し、死んだownerのdirectoryをrenameでclaimします。PID再利用は保守的にlive扱いです。これは起動応答を失ったSessionの回収を助けますが、別profileで同じcwd/pathを使う場合のscopeも検査対象です。秘密のbrowser profileをコピーするjournalではありません。[start journal](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/start-journal.ts#L33)

観測thumbnailはmodel向けattachment storeとは別のmemory ringに置き、生成途中のfileを読んで削除します。観測SSEの接続数が撮影需要を持ち、model操作が撮影より優先されます。UIを閉じる、観測をOFFにする、taskを止める、modelが保存したscreenshot/export fileを削除する操作は同一ではありません。観測HTTP routeはloopback Host、同Host Origin、cross-site拒否、JSON POSTを検査します。これはDSH Webのthumbnail境界であって、daemonのWS本人確認ではありません。[ephemeral thumbnail](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/observation.ts#L317)、[HTTP fence](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/observation-http.ts#L47)

daemon側のOrigin検査は、32文字のa〜pからなるChrome extension形式を受け入れます。固定拡張IDの照合ではありません。extensionのlocal接続にはremote pairingのtokenを付けない分岐が残ります。[Issue #402](https://github.com/Tencent/BrowserSkill/issues/402)はlocal daemonの本人確認を求め、関連pairing PR #424〜#430は取得時openでした。実機攻撃は再現していません。固定ソースの条件を、修正済みや安全確認済みと書かないための照合です。[daemon Origin gate](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/crates/bsk-cli/src/daemon/ws.rs#L36)、[local/remote socket](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/apps/extension/src/transport/remote-endpoint.ts#L79)

### 修正が届いた例と、まだ残るhelper条件

[Issue #370](https://github.com/Tencent/BrowserSkill/issues/370)は、archive済み祖先からforkしたactive conversationがbrowserを開始できない報告です。所有lineageは「新しいarchive時に子のbrowserも止める」ために必要でしたが、開始許可にも同じ祖先setを使って永続拒否になっていました。[PR #371](https://github.com/Tencent/BrowserSkill/pull/371)は開始時だけcaller本人を検査し、cleanupのlineageは維持しました。09-29にmergeし、mock host/CLI境界の回帰6ケース、plugin446test、buildの成功を作者が報告しています。報告中の142件/86件は一台のSession配置の数で、一般的な発生率ではありません。

配布は別段階です。[#373](https://github.com/Tencent/BrowserSkill/issues/373)は0.2対応peer修正がmainにあってもnpm0.3.1にはない問題を追い、[release PR #375](https://github.com/Tencent/BrowserSkill/pull/375)で0.3.2を用意しました。前回の公開npm0.3.2確認は、現行manifestと同版です。CLI・extension・DSHのtag/ストア提出は別工程なので、package版だけで三者更新済みとは言えません。

一方、前回見つけたqueue同期throwは現行SHAでも残っています。`fn().then(...)`が内側`previous.then`で同期throwするとcallerのPromiseがsettleせずtailも止まります。今回Node22.23.3で**queue.tsだけ**を別processへ読み、同期throwと後続callbackを与えて、50ms後に`caller=pending / later=false / unhandled=['sync']`を再観測しました。async callback rejectとは違う条件です。実DSH/browserを起動していないため、production callerからの到達と利用者障害は未確認です。[同期throwの境界](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/queue.ts#L17)

持ち帰れる小さい部分は、許可判定とcleanup lineageを分けること、退出時pipeの上限、所有resourceのjournalです。queueを移すなら同期throwをPromise拒否へ変換する境界を先に加えます。

## Modlens: durable imageとwire evidenceの内容が一致するとは限らない

基本経路は「text-only modelのvision twinを選択 → request-timeのimage変換 → attachment読出し →0600のtemp画像 →CLI/provider解析 →structured evidenceをtext化 →元providerへstream」です。toolによる`modlens_read_image`は別入口で、path/URLとfocusがcache identityに入ります。native vision modelはwrapper対象から除き、元providerのretryPolicy・prepareCall・model能力を取り直します。登録済みかどうかだけでなく、元routeの消失や能力変更でもwrapperが古い選択を拒否する必要があります。[wrapper登録とstream](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/index.js#L768)、[tool解析とcache](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/index.js#L233)

wrapperはSession logの画像を保持し、wireだけをOCR/layout/semantics/uncertaintyへ変換します。nested tool-result内の画像も再帰変換します。`autoRead`は既定OFFの別経路で、pre-stepでenter messages自体を置換します。両経路を混ぜて「ログは常に同じ」と説明しません。解析promptには画像内指示に従わない規則がありますが、OCR結果の事実性を保証するものではありません。providerへ画像が出ること、text modelには推定を含む解析結果が出ることを設定として説明します。[再帰画像変換](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/index.js#L1395)、[pre-step autoRead](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/index.js#L1436)、[解析prompt](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/src/prompt.ts#L24)

evidence cacheは全wrapperとautoReadで共有し、成功は保持、失敗は60秒cooldownです。attachmentのkey順をcanonicalizeし、同時walkの参照countでentryをpinします。cancelされたcallerは待機を止めますが、共有解析は続きます。これは別callerの結果を殺さない代わりに、取消後も画像解析のprocess/通信/費用が残り得る選択です。上限256は常に厳密な最大件数ではなく、全entryがpinされたときはevictできません。[evidence cache](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/index.js#L1192)

**ログ再現の限界**はrequest-time変換の成功evidenceがprocess cacheにある点です。durable画像だけでは、再起動・cache退去後に別vision model/設定で生成されるOCRが同じbyteになる保証がありません。元画像の保持は再解析の材料であって、当時text modelが読んだevidenceの固定記録の代わりにはなりません。自作provider bridgeなら、画像ref、解析route/version、結果hash、実際の注入文を保存単位として設計する条件が残ります。これは静的読解からの推論で、保存データ喪失の実機再現ではありません。

[Issue #68](https://github.com/liustack/modlens/issues/68)は画像解析失敗時、毎stepの変動したエラー文が同じ履歴位置へ入りprovider prefix cacheを外す報告です。現行実装と[3.21.1 changelog](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/CHANGELOG.md#L99)は、安定した失敗文、cooldown、共有cache・walk pinへ変えています。Issueは08-18 closeですがchangelogの3.21.1は08-19なので、closeを配布完了時刻としません。費用曲線やcache missは報告者の条件であり、今回課金APIで再計測していません。

[#81](https://github.com/liustack/modlens/issues/81)ではattachment変換をcacheしても明示toolが繰り返しCLIを起動する入口が残りました。現行toolにはlocal stat identity・focus・remote60秒TTL・cloneした戻り値が加わっています。cacheが減らすのは解析実行であり、modelの重複tool decisionや思考loop全体を止める保証ではありません。[tool解析とcache](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/index.js#L233)

[#93](https://github.com/liustack/modlens/issues/93)のcompact失敗は、plain object adapterが新しいbase-class default `imageRequestPricing`を持たなかったことが所有境界です。現行は同defaultを実装しています。DSH peerを宣言していないことは、この内部契約の追従を免除しません。成功生成、取消、履歴再送だけでなくcompactをwrapper適合試験へ入れる価値があります。[wrapper登録とstream](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/index.js#L768)

## Memsearch: Markdownを保存できても次turnに検索できるとは限らない

取得はpre-stepのstep1で最初の非空textをqueryにし、memory fileがあるprojectのcollectionへCLI searchします。`next()`後のmessagesを使いますが、OpenViking/MemOS/EverOSのようなhuman sourceだけへの明示filterはこの場所にありません。他pluginが前に置いたcontextがqueryになる組合せをtargeted testへ含めます。searchはbash subprocessにtimeoutを持つ一方、同じagent AbortSignalを渡していないため、取消後も期限までは検索が続く条件があります。[pre-step injection](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/plugins/dsh/index.js#L1300)

保存は`turn/end` →snapshotEventsからそのturn抽出 →plugin全体のcaptureChain →要約 →日別Markdownへanchor付きappend →detached indexです。Session.cwdでprojectを選び、collectionはgit-common-dirを基に分けます。要約失敗時はraw transcriptを大量に記憶へ流さずunavailable noteとanchorを保存します。headless要約は別profileを起動し、`MEMSEARCH_DSH_SUMMARIZE=1`でcapture/inject/Skillを停止します。循環防止が別agent起動の必須条件です。[capture chain](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/plugins/dsh/index.js#L1342)、[turn reconstruction](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/plugins/dsh/index.js#L776)、[headless summarizer](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/plugins/dsh/index.js#L1056)

captureChainは同Hostで要約を直列化しますが、他Hostと日別fileを共有するfile lockではありません。`captureExists`のscan→writeも別processとatomicではありません。保存成功とindex成功はtransactionではなく、indexはdetached/unrefでHost終了後も続く設計です。直後のturnが新記憶を見ない可能性、古いindexとMarkdown削除の同期、embeddingを重複実行するprocessを分けて検査します。[anchorとappend](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/plugins/dsh/index.js#L857)、[detached index](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/plugins/dsh/index.js#L382)

inject OFF、capture OFF、plugin OFFは別状態です。capture済みMarkdown、Milvus index、headless要約履歴、すでにSessionへ注入された`plugin:memsearch` snapshotは残ります。削除を設けるなら元file、検索index、過去Sessionのどこを消すかを明示します。embeddingはCLIの設定に依存し、ONNX localでも初回model取得とCPU・memory費用、外部providerならembeddingと要約の課金が加わります。autoRecallで追加されるtext tokenは別の費用です。

[Issue #763](https://github.com/zilliztech/memsearch/issues/763)→[PR #762](https://github.com/zilliztech/memsearch/pull/762)はV4が旧`kind:'plugin'`を拒否し注入turnが失敗する問題です。10-09 11:47 UTCにmergeし、同日11:51 UTCに[release PR #789](https://github.com/zilliztech/memsearch/pull/789)をmerge。新しい`plugin:memsearch` source、CIへのDSH test追加、0.1.6を用意しました。#789はDesktop0.2.0-rc.2のend-to-endとV4 row確認を作者が報告します。公開npm0.1.6の存在は前回確認済みですが、この調査で再導入していません。schema変更と保存履歴のproducer identityを結んだ例です。

[#735](https://github.com/zilliztech/memsearch/issues/735)→[#737](https://github.com/zilliztech/memsearch/pull/737)は`session.events`からsnapshotEventsへの移行とstdin EOFを直した例です。PRはNode recorderで子がEOF後に終了する試験を報告し、既存Windows12失敗は別に記載しています。関連成功を全OSの成功へ拡張しません。

maintenanceはSession disposalとboot projectのtimerから起動します。[#788](https://github.com/zilliztech/memsearch/issues/788)はO_EXCL lockが強制終了後に残り、dead PIDを検査せず永久lockedになる報告です。固定版の`_file_lock`にもその分岐が残ります。40日停止という数値は一台の報告であり、今回の再現ではありません。memory本体のrecallが動いてもPROJECT/USER更新やSkill蒸留だけ止まるため、検索成功をmaintenance正常の証拠にしません。[maintenance lock](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/src/memsearch/maintenance.py#L700)

## OpenViking: runtimeとMCP子processのscopeが違う

leafはnative bundleです。pre-step recall、Session event capture、token threshold commit、startup profile/Skill catalog注入、URI tool guardを持ち、別にDSH MCP clientからstdio proxyを起動します。したがってMCPを設定するだけのSkillではなく、model-visible入力とtoolを自動で増やします。startupは新旧DSH lifecycleを分岐し、MCP mountを最後に待たずに置くことでtools/listが詰まってもcapture登録を妨げない設計です。[DSH lifecycle](https://github.com/volcengine/OpenViking/blob/6c1107527af4243055640fbb0d7d7bdcb54dc75c/examples/dsh-memory-plugin/index.mjs#L12)

HTTP runtimeはSession.cwdからpeerを決め、`dsh-<session-id>`と`viking://~/memories`を使います。default recallPeerScopeは`all`なので、peerをproject別にしても自動recallがprojectを越えることは設定された動作です。MCP proxyはprofileごとのprocessでboot peerを持ち、`remember`はlive DSH Session streamとは別server sessionへ保存します。runtime actorとMCP actorを同一視すると、toolで書いた記憶の所有先・recall先を説明できません。[runtime/MCP scopeの説明](https://github.com/volcengine/OpenViking/blob/6c1107527af4243055640fbb0d7d7bdcb54dc75c/examples/dsh-memory-plugin/README.md#L149)

turn同期OFFは新規writeを止める一方、ON時にpending queueへ入ったwriteは復旧drainerが再送します。ユーザーがOFFにした後のwriteを一律に不具合としませんが、取り込み済みqueueを撤回するUIが必要かは別の選択です。60秒drainerはsingle-flightで、health復旧後に再送します。削除tool`forget`、buffer/pending撤回、server extraction後の派生memory削除は別の対象です。[pending drainer](https://github.com/volcengine/OpenViking/blob/6c1107527af4243055640fbb0d7d7bdcb54dc75c/examples/dsh-memory-plugin/runtime.mjs#L329)

[#5970](https://github.com/volcengine/OpenViking/issues/5970)→[#5973](https://github.com/volcengine/OpenViking/pull/5973)はproxyのSSE分割がCR行末を認識せずtools/list等を空応答へ変える問題です。10-13 03:26 UTC merge、共有moduleと生成copy・DSH manifest0.5.24まで同期しました。作者はWindows/WSLで各156関連ケース、loopback HTTP、UTF-8境界試験を報告します。重複するmatrixの件数を加算せず、性能の証拠にもしません。PR本文はその検証時点でnpm未publishと明記していました。その後の今回の配布調査では公開registryから0.5.24 tarball（101,120 bytes、通常41file）を取得し、integrity・entry・patchを照合できました。PR時点の未publishと現在取得できる配布物を分けます。

[#5988](https://github.com/volcengine/OpenViking/pull/5988)は、gateway extra headersがMCP経路だけへ届きruntime capture/recallへ届かないこと、HTMLの200を成功空結果にする条件を扱うopen提案です。固定版HTTP helperはJSON parse失敗をnullへ落とし、requireJsonBody設定次第で2xxを空結果として返せます。これは診断条件の静的確認で、gatewayへ接続した再現ではありません。credential chainを一つにしても**利用するprocessごとのheader**とJSON契約の検査が必要です。[HTTP response判定](https://github.com/volcengine/OpenViking/blob/6c1107527af4243055640fbb0d7d7bdcb54dc75c/examples/memory-plugin-shared/lib/ov-http.mjs#L60)

## MemOS: localという名称でもHost modelとsystem promptを使う

DSH patchはcompiled adapterを呼び、SQLite/embedding coreを起動して、pre-step recall、session capture、memory tools、viewer、systemPrompt sectionを登録します。hostLlmEnabledは既定trueです。direct-user turnが選んだprovider/modelのrouteを捕捉し、記憶側のLLM処理にも使います。local storageは、外部modelへ会話や記憶が出ないという意味ではありません。[recallとprompt登録](https://github.com/MemTensor/MemOS/blob/a7367d07e55db61099f7b4e2c1108bc5831a24f3/apps/memos-local-plugin/adapters/deepseek-harness/index.ts#L377)、[host model bridge](https://github.com/MemTensor/MemOS/blob/a7367d07e55db61099f7b4e2c1108bc5831a24f3/apps/memos-local-plugin/adapters/deepseek-harness/host-llm.ts#L118)

bridgeは`next()`が確定したuser inputを検索し、turnごとに一回、絶対deadlineとagent signalを使います。ONNX初期化等が取消不能でもcallerの待機時間はraceで制限します。ただしlosing promiseを観測して終了を待つことと、全CPU処理を即時停止することは違います。namespaceはagentKindとprofile/presetを使い、cwdはcontextHintsにも入ります。project directoryが常に保存namespaceになると推測せず、同presetで複数workspaceを使う検索契約を検査します。[bounded recall](https://github.com/MemTensor/MemOS/blob/a7367d07e55db61099f7b4e2c1108bc5831a24f3/apps/memos-local-plugin/adapters/deepseek-harness/bridge.ts#L220)

Session disposalはdetachし、plugin解除がqueueをdrainする境界です。toolsEnabledを切ってもrecall/capture/hostLlmは独立しています。systemPrompt guidanceは自動recall済みであること、searchの再質問、記憶の古さをmodelへ指示する変更です。表示追加だけのpluginとして流用できません。[recallとprompt登録](https://github.com/MemTensor/MemOS/blob/a7367d07e55db61099f7b4e2c1108bc5831a24f3/apps/memos-local-plugin/adapters/deepseek-harness/index.ts#L377)

[#2405](https://github.com/MemTensor/MemOS/issues/2405)にはV4 source拒否の報告があります。自動PR #2406はcloseされてもmergeされず、[#2408](https://github.com/MemTensor/MemOS/pull/2408)と[#2455](https://github.com/MemTensor/MemOS/pull/2455)は取得時openです。固定mainのrecallとhost LLMにはなお旧`kind:'plugin'`が残ります。#2455のlive確認は提案branchの作者報告でありmainや公開版の結果ではありません。manifest beta版と報告npm版が違うことも、修正済み判定を難しくします。[recallとprompt登録](https://github.com/MemTensor/MemOS/blob/a7367d07e55db61099f7b4e2c1108bc5831a24f3/apps/memos-local-plugin/adapters/deepseek-harness/index.ts#L377)、[host model bridge](https://github.com/MemTensor/MemOS/blob/a7367d07e55db61099f7b4e2c1108bc5831a24f3/apps/memos-local-plugin/adapters/deepseek-harness/host-llm.ts#L118)

[#2437](https://github.com/MemTensor/MemOS/issues/2437)はturn/start後約3msで0stepの取消、後からrecall完了という報告です。報告はHost CPU観測を使ってfreezeとturn取消を区別しますが、これだけでV4 source問題と同じ原因に統合しません。時計、turn/inboxイベント、signal発火元を追う追加証拠が必要です。embeddingが成功したことから、Host lifecycleが正常だったとは判断できません。

## EverOS: 本体から移転したleafと、capture/flushの分離

[EverOS PR #416](https://github.com/EverMind-AI/EverOS/pull/416)は08-25にmergeし、22fileのDSH leaf・専用CIをEverMind-AI/pluginsへ移しました。topicは残したため本体のstarsで発見できますが、現行leafのコード参照は**pluginsのSHA**です。本体にDSH bundleがあるとしてrootをinstallしないことが最初の導入条件です。

現行leafは`agent/turn-stopping`でcaptureし、server memorizeへ`defer_extraction:true`で保存します。抽出は30秒idle、約12k token、50message、5分max delay、Session切替、disposeでflushします。入力の耐久保存とembedding/extractionの可視化を分けた設計です。同projectの別Sessionへ移る前にflushを待ちますが、失敗時はwarnしてrecallへ進むので、直前記憶が必ず検索できる契約ではありません。[EverOS lifecycle](https://github.com/EverMind-AI/plugins/blob/3318dc1a2afcef3d3d804963941e8ce0bf9a3879/dsh/src/index.ts#L33)、[capture/flush/drain](https://github.com/EverMind-AI/plugins/blob/3318dc1a2afcef3d3d804963941e8ce0bf9a3879/dsh/src/memory-runtime.ts#L173)

user/agentの二trackを独立検索し、user profile、agent case/skillを文字数上限で注入します。project IDはabsolute cwdのhash、user IDは環境/OS名、agent IDはpresetから導きます。同じrepoのclone/worktreeは別projectになる場合があり、同じユーザー名の別machineを共有serverで使う場合もexplicit IDを検査します。OpenVikingのoriginベースpeerと同じscope設計ではありません。[identity scope](https://github.com/EverMind-AI/plugins/blob/3318dc1a2afcef3d3d804963941e8ce0bf9a3879/dsh/src/identity.ts#L35)、[二track recall/source](https://github.com/EverMind-AI/plugins/blob/3318dc1a2afcef3d3d804963941e8ce0bf9a3879/dsh/src/recall.ts#L179)

autoStartはhealthを見て、loopbackのみspawnし、already-running serverをstop対象にしません。pluginがspawnしたchildだけを解除時に止めます。health成功は接続先の所有者や認証の証明ではないので、remote/多tenant運用ではその契約を追加確認します。[owned server起動](https://github.com/EverMind-AI/plugins/blob/3318dc1a2afcef3d3d804963941e8ce0bf9a3879/dsh/src/provision.ts#L76)

[PR #410](https://github.com/EverMind-AI/EverOS/pull/410)は、Session disposalにしか依存しないとconversation切替でbufferが抽出されず、毎turn抽出にするとLLM費用が増える問題を説明し、このbatch設計を08-17にmergeしました。作者はDSH19testとserver38test等を報告しています。これは処理回数を減らす設計理由であり、検索品質やtoken削減率の実証ではありません。本体Issue #406の97.5%等は別製品の提案なのでEverOSの実測として使いません。

現行leafのrecall sourceは旧`kind:'plugin'`で、peerも0.2より前です。V4へのnew row適合を独立検査すべきソース条件が残ります。今回DSH起動はしていないため、実際にどのHostがどのstageで拒否するかは未確認です。memory内容を保存できても、modelへ届けるmessage admissionが通るとは限りません。[二track recall/source](https://github.com/EverMind-AI/plugins/blob/3318dc1a2afcef3d3d804963941e8ce0bf9a3879/dsh/src/recall.ts#L179)

## Open Design: 接続テストと実行結果の完全性を分ける

別アプリdaemonが専用`open-design` profileのDSH childを起動し、stdio JSONでprobe/models/ready/execute/cancel/resultを扱います。probeはちょうど一つのframe、runtime identity、capabilityを照合します。executeは一processに一回で、resumeは保存Session IDと受信session/result IDを突き合わせます。stdoutへログが混じること、exit0なのにterminal resultがないことを別のfailureにします。[probe parser](https://github.com/nexu-io/open-design/blob/1343f374c63d7866f4f3ff5d48ef038eba647f1b/apps/daemon/src/agent-protocol/dsh-profile/probe.ts#L8)、[session/result照合](https://github.com/nexu-io/open-design/blob/1343f374c63d7866f4f3ff5d48ef038eba647f1b/apps/daemon/src/agent-protocol/dsh-profile/session.ts#L127)、[stdio一回実行](https://github.com/nexu-io/open-design/blob/1343f374c63d7866f4f3ff5d48ef038eba647f1b/packages/dsh-runtime/src/index.ts#L380)

取消latchはchild spawn/handshake前に届いたrequest IDも保持します。killは結果受付と競合するため、Session作成前取消、作成後取消、tool副作用後取消のfixtureが必要です。profileの再起動とresumeは別で、profile/DSH runtime更新が保存Sessionへの互換性を保証しません。sourceのpeerが広くても直接cmdline依存は0.1.1-rc.2なので、model catalogの成功と新DSH event shapeの一致を別試験にします。

現行event転送は`assistant/chunk`のtext/reasoning deltaをframe化し、`assistant/message`はusageだけ送ります。result.outputもchunkから組み立てます。[PR #8615](https://github.com/nexu-io/open-design/pull/8615)は非stream routeの完全文を失う問題を修正提案し、stream済みstepをtrackして二重表示を避ける案です。作者はRouteLLMと専用profileで成功したと報告しますが取得時openで、固定mainにはそのfallbackがありません。課金usageが見えたことを本文転送の成功とみなせない例です。[event転送とoutput](https://github.com/nexu-io/open-design/blob/1343f374c63d7866f4f3ff5d48ef038eba647f1b/packages/dsh-runtime/src/index.ts#L207)

[Issue #8625](https://github.com/nexu-io/open-design/issues/8625)は0.2.xの接続テストがexit0で失敗する別報告です。本文は添付文書へのリンク中心で、その添付は今回取得していません。PR #8615の非stream問題と同じ根因と決めません。両方とも公開版へ届いた修正は確認できず、前回のnpm404を今回の再確認結果としても扱いません。

## 次に行う検査を小さく分ける

| 対象 | keyless fixtureで先に確認すること | 実環境で残ること |
| --- | --- | --- |
| BrowserSkill | queued abort、同期throw、exitとcloseの分離、取消後start応答、SSE切断後thumbnail停止、caller archiveと祖先cleanup | login済みprofile、borrow/return、download副作用、WS本人確認 |
| Modlens | wrapper wireの固定byte、cache cold/warm/restart、同attachment concurrent cancel、tool-result再帰、compact/新adapter method | 画像が出るprovider、OCR誤り、課金、native vision切替 |
| Memsearch | human/他plugin text順序、capture→index失敗、二Host同file、snapshotEOF、死んだlock、shutdown前capture drain | Milvus Lite/remoteでの競合、embeddingと要約品質、古いindex削除 |
| OpenViking | per-session actorとboot MCP actor、sync OFF前後pending、SSE各行末、200HTML、MCP遅延とstartup | server抽出完了後の検索、tenant/auth、forgetの派生物 |
| MemOS | deadline後完了、route変更、producer source admission、preset/workspace namespace、viewer port占有、dispose drain | native SQLite/ONNX、実Hostのsignal、host LLM費用 |
| EverOS | defer captureとflush、Session切替flush失敗、ID collision、preexisting serverのstop除外、V4 admission | server抽出遅延、認証、rebuild/削除と検索index |
| Open Design | 非stream/stream本文、nested event、stdout汚染、handshake前cancel、resume不一致、terminal resultなしexit0 | 専用profileの更新・復元、実providerのtool/usage |

この章で実行した動作確認はBrowserSkill queue helperだけです。外部bundleのinstall/build、実browser、login、課金API、embedding/server、Open Design実行は行っていません。Issue/PRにあるtest数と実環境報告は作者の報告として分け、close/merge/package版を相互に置き換えていません。取得したIssue一覧は各repositoryの最新100件で、古い全履歴やcomment全件の監査ではありません。
