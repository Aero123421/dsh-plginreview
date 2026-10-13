# Remote Webアクセスとcatalogの「検証済み」を分ける

候補の発見から導入までには、metadata検査、配布byteの一致、Hostへの登録、Client起動、実機機能、remote操作権限の確認が必要です。Pocket、Radar、Shopのソースを2026-10-13に固定し、取得・生成・取消・再起動の経路を比較します。[market・update章](marketplaces-and-updates.md)には、ほかのカタログと更新処理の比較があります。

| repo / 固定SHA | 実体とmanifest | 「使える」とされる根拠の範囲 |
| --- | --- | --- |
| shaobeichen/dsh-pocket / `e6424c3a2c7912075acb9f3746c584b2bcf422c2` | root `dsh-pocket 2.11.0`、Host `lib/index.js`、Client `client/client.js`、bundle patch | PIN proxy + tunnel + mobile補助。ネットワーク、browser、Host版の条件が別に残る |
| AdamPlatin123/dsh-plugin-radar / `d42875ea248fa0fdf82e5d4c39cde700a4152da3` | root DSH plugin manifest/bundleなし。公開catalog、site、server engine | 歴史runtime判定をcanonicalへ集約。公開test engine/逐条provenanceの範囲に限界 |
| LivXue/dsh-plugin-shop / `8db779bf1de6d3307803891c4b0e65fad4af6ef2` | rootはカタログ生成用workspaceでnpm公開しない設定（`private: true`）。実pluginは`packages/dsh-plugin-shop`の0.8.6、Host/Client/Remote/typert exports + bundle | 掲載は自動manifest/file検査。導入は読者Hostでmanager/CLIが実行し結果を分類 |

根拠: [Pocket manifest](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/package.json#L1)、[Radar site manifest](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/site/package.json#L1)、[Shop registry root](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/package.json#L1)、[Shop plugin manifest](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/package.json#L1)。SHAは調査時点のdefault branchです。starsは利用者数・品質を示すものとして使いません。トピック検索19,027件のstars順1,000件上限から選んだ候補で、全件を網羅していません。

## Pocket: PIN proxyがDSHのbrowser authorityを肩代わりする

### 二段階loginとfull Web権限

`apply`はwebServerの実portとconnectionのlaunch tokenを読み、proxyを0.0.0.0へ開始し、LAN/Quick/Named入口を用意します。Pocket PINとDSH browser launch tokenは別です。public/LAN PINは別fileへ`0600`で保存、ランダムPINはCSPRNG、customは8〜64 alphanumericです。Pocket cookieは`sha256(PIN:sessionKey)`、HttpOnly/SameSite=Lax/30日。module apply時のrandom sessionKeyでHost再起動後に古いcookieは失効します。

認証経路は、Hostをpublic/LAN/loopbackへ分類 → LAN switchとauth switch → POSTまたはquery PIN/cookie検証 → loopbackのHost/Origin/Referer/sec-fetch-siteに書換え → root GETへDSH launch token補完 → DSH auth cookieとAPI/WSへ進む順です。publicは任意未知domainもpublic判定、LAN authはユーザーが解除できます。手動LAN IP overrideは分類より優先します。

根拠: [PIN fileとrotation](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/index.js#L46)、[proxy/auth/launch token配線](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/index.js#L285)、[cookie/query認証](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/proxy.mjs#L416)、[loopback authority書換え](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/proxy.mjs#L468)、[HTTP admission](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/proxy.mjs#L711)、[WebSocketにも同じ認証](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/proxy.mjs#L1021)。

この方式ではremote browserの要求を宿主がloopback authorityとして受けます。proxy認証が新しい入口の境界で、PINを知ることは特定Sessionだけのread権限とは違います。DSH Webが公開する操作面へ届く構成です。Remoraのdevice enrollment、workspace/session scope、read/write権限と同一のモデルではありません。Host field/forwarded headerを使う分類は、直LAN、Cloudflare、独自reverse proxyごとに実配備のauthorityと一致させる必要があります。実攻撃や権限迂回を今回再現したという主張ではありません。

rate limiterは同一IPの60秒5失敗で60秒lock、global 50失敗で30秒lockを持ちます。query PINとWSのqueryも失敗数へ入れ、成功時にIP数を消します。memory状態はrestartで消えます。`cf-connecting-ip`優先というsourceの前提はCloudflareがそのheaderを書いたときのものなので、独自proxy/直LANでも同じ信頼を自動付与する契約にはしません。

根拠: [throttleの状態とIP前提](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/proxy.mjs#L119)。

### tunnelの開始・手動停止・disposeの意図を分ける

`startTunnel`はproxy確保 → single-flight Promise → AbortController → named token/hostnameまたはquick binary → ready → onExit監視 → auto marker書込み → public PIN rotation callbackです。stopはAbortとkill、active refsを消し、手動停止ならmarker削除、dispose/Host restartならmarker保持です。auto markerのwrite/rmはqueueに入れ、遅いwriteで手動停止の意図を復活させない設計です。古いattemptのfinallyは、自分がまだtailの場合だけPromise参照を消します。

proxyはHTTPだけでなくupgraded WS socketを追跡し、closeでそれらをdestroyしてserver.closeが待ち続けないようにしています。disposerはRPC cleanup後service.disposeをawaitします。一方、tunnelのkillはchild.kill呼出しで、stopは旧tunnelPromiseのsettlement/child exitをawaitしていません。rapid stop/start、spawn遅延、Host restart時に子processが消える実証は別に必要です。[Issue #167](https://github.com/shaobeichen/dsh-pocket/issues/167)は2.6→新版後の孤児process報告で取得時open、環境と原因は公開本文だけでは確定できません。

根拠: [marker queue](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/service.mjs#L239)、[start single-flight](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/service.mjs#L295)、[stopとrestore](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/service.mjs#L363)、[dispose](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/service.mjs#L434)、[全socket cleanup](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/proxy.mjs#L1126)、[Cordis disposal](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/index.js#L394)。

cloudflaredはexplicit path/PATH/cacheから探し、なければplatform assetをofficial latestと複数mirror、macOS bottle sourceから取得します。120秒download deadline、サイズ1 MiB未満の拒否、tar展開、rename/chmodはあります。固定SHA/checksum/署名検証がこのdownload経路にあるとは確認できません。OFMの導入済みEd25519 trust rootと同じ更新検証にはなっていません。既存binaryを管理された配布から用意してpath指定する条件が別にあります。Quick/Named childは`--no-autoupdate`、固定HTTP/2でspawnし、named tokenはenvへ渡します。cloudflared外部通信・downloadは実行していません。

根拠: [binary配布元](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/tunnel.mjs#L80)、[downloadと検査](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/tunnel.mjs#L228)、[single downloadとpath解決](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/tunnel.mjs#L354)、[named child起動](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/tunnel.mjs#L452)。

Pocket自体の更新はDSH CLIへ任せ、loadedVersionと現在disk versionを分けます。Desktop判定時はupdate/restartを止め、Desktopのownerへ委ねます。これも全desktop実装を検証した保証ではありません。根拠: [running/disk version](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/index.js#L31)、[Desktop所有の境界](https://github.com/shaobeichen/dsh-pocket/blob/e6424c3a2c7912075acb9f3746c584b2bcf422c2/lib/index.js#L261)。

### 修正事例: #147はmainとnpm版の時差が診断を混乱させた

[PR #124](https://github.com/shaobeichen/dsh-pocket/pull/124)は09-16にmerge。plugin productionではtest-only `internals.home`がundefinedとなり、serviceがautoStatePathをnullにしてmarkerを書かない/読まない原因でした。呼出し側にDSH_HOME/ホームfallbackを足し、service helper自体は暗黙に実ユーザーhomeへ触れないようにしています。作者は174test、isolated実DSHで3回起動、local cloudflared fixtureによるrestoreを報告し、Cloudflareへは接続していません。[merge SHAのtest job](https://github.com/shaobeichen/dsh-pocket/actions/runs/35120021291/job/104875131078)はsuccessです。

その後[Issue #147](https://github.com/shaobeichen/dsh-pocket/issues/147)はnpm 2.10.6で同じ症状を報告。利用者コメントは修正済みmainと未発版の差を指摘し、maintainerの後の返信はまだ未mergeと述べており、説明が一致しません。PR metadata、現在source、[v2.11.0](https://github.com/shaobeichen/dsh-pocket/releases/tag/v2.11.0)（10-12 14:42 UTC）とrelease botが#124を含むと示した記録を優先します。Issue closeだけを修正完了とせず、古いnpm版のfailure、mainの修正、公開版への到達を分けます。今回実tunnel restoreを再実行していません。

### 直ったと書かない二つのremote経路

[PR #151](https://github.com/shaobeichen/dsh-pocket/pull/151)はHTML gzipのためpolyfill/transport shimが注入されない問題に、HTMLだけAccept-Encoding identityを要求する案です。作者は実Chromiumとlocal DSH proxy、55関連testを報告しますがclosed未merge。fixed SHAのgzip gateを提案済みだから修正済みとは扱いません。[PR #169](https://github.com/shaobeichen/dsh-pocket/pull/169)もremote model settingsの修正案でopenです。動くhelper、HTMLに実際に含まれるscript、remote privileged requestがHostに届くことは三つの確認になります。

[Issue #160](https://github.com/shaobeichen/dsh-pocket/issues/160)は低帯域で大きなWS snapshotがheartbeatを遅らせ、11秒周期の再接続と再snapshotが起きる報告です。maintainerは上流gatewayの心拍期限/初期snapshotの問題としてcloseし、PocketのHTTP gzipではWSを直せないと説明しています。closedを「全remote性能問題を解決」に読み替えません。Remoraでは短いheartbeatを加えるだけでなく、large frame、backpressure、reconnect後のsnapshot量、同linkの他通信も試験対象になります。

## Radar: 歴史runtime判定の集約と公開証拠の欠けを残す

### DSH bundleのregistryではなく複数出所を合わせるengine

公開sourceはdiscovery → aggregate/normalize/canonical → render → snapshot/PR delivery → data/siteの段階を持ちます。root DSH bundleはなく、`site/package.json`はsite build用です。topical repo、npm、履歴report、手動登録、repo mappingを合わせるため、「一行のcatalog」は一回のinstall結果と同じ粒度ではありません。

canonicalはrepoのstable identity/aliasを使い同repoの重複をまとめます。pass/fail等のconflictはpendingへ落とし、その後別の第三recordが来てもconflictを消さない設計です。exportはcanonicalのprecomputed rowsを読む経路になり、Markdown正規表現から再構成するlegacy pathは対照用です。`ok/incompatible/pending/untested/gone/ambiguous/unlocated`、stars nullが未知という契約を持ちます。

根拠: [engine所有域](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/engine/README.md#L5)、[履歴conflict仲裁](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/engine/aggregation/build_canonical.py#L133)、[canonical exportとschema](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/scripts/export-data.py#L1)、[repo identity](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/engine/lib/radar/repository_identity.py#L1)。

公開flat rowsはrepo/name/verdict/stars/desc等を持ちますが、各rowへplugin commit、install artifact hash、Host/Node/OS、実行時刻、logとassertionを完全に結び付けていません。固定したlatest.jsonには`generated_at: 2026-10-13T05:30:43Z`、snapshot `20261013T053001Z`、`runner_versions: {}`です。これは現在DSH全版で8,214件が動く証拠ではありません。README自身も歴史の可用判定、逐条provenance不足、性能/安全auditとの差を記載します。

根拠: [可用の読み方と限界](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/README.md#L46)、[公開pointer](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/data/latest.json#L1)、[flat export行](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/engine/aggregation/build_canonical.py#L392)。

runtime testingの一plugin一pod、L0–L3、input_hashによる重測は公開engineに含まれていません。private component manifestはsnapshot generator、runtime aggregate、bot、driver、stateの契約と欠落時WARN/skipを示します。公開copyのscriptが起動すること、欠けたprivate validatorまで再現できることは別です。

根拠: [validator未公開の境界](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/engine/README.md#L44)、[private入力/出力契約](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/engine/ops/private/MANIFEST.md#L8)。

### runner-smokeとdata freshnessはruntime再試験ではない

runner-smokeはPython compile、deterministic tile生成、README/data export、schema validation、identity/render/site regressionを通します。pluginを全件installしてmodel/tool操作するjobではありません。readme-renderはsnapshotを読んでPRへ進み、merge guardがhead SHA、bot author、file allowlistを照合します。これは更新pipelineの制御で、各plugin codeの検証ではありません。

根拠: [実CI命令](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/.github/workflows/runner-smoke.yml#L24)、[snapshot renderとmerge guard](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/.github/workflows/readme-render.yml#L27)。

[Issue #939](https://github.com/AdamPlatin123/dsh-plugin-radar/issues/939)はlatest.jsonのgenerated_atが26.9h古いと自動作成され、途中71.9hまで遅延し、10-12 23:15:48のpointerが公開された後「4.6hへ復帰」でcloseしました。monitorはmain raw pointerを外から読んで、取得/parse失敗も不可用として告知する設計です。原因候補はserver snapshot/sync/renderの停止ですが、Issueにはroot cause確定や修正commitがありません。更新復帰は確認できても、原因を創作しません。

[PR #946](https://github.com/AdamPlatin123/dsh-plugin-radar/pull/946)の05:30 snapshot renderが現行SHAへmergeしたことはAPIで確認できます。merge SHAにはfreshness successに加え別`fetch` failureもあり、全workflow greenとは表現しません。公開pointerのfreshness回復と、外部probe/validatorの健全性を分けます。根拠: [消費者側monitor](https://github.com/AdamPlatin123/dsh-plugin-radar/blob/d42875ea248fa0fdf82e5d4c39cde700a4152da3/.github/workflows/data-freshness.yml#L1)。

今回`python3 scripts/test_repository_identity.py`をオフラインで実行し8/8成功しました。alias/rename/conflictのunitとtemporary fixtureの生成であり、runtime判定の再現ではありません。

## Shop: 自動掲載gateと読者Hostの導入結果は別

### discovery・registry・runtime packageの三つの入口

registryはnpm keywordとGitHub topicから候補を取得し、publisher/change-feed/previous manifest lockも使い、検索漏れ/消失を記録します。GitHub repo rootにbundleがなければsubpackageを探す経路があります。npm packageとGitHub forkが同じbundle名を持つことがあるため、identityは単なるnameではありません。

GitHub掲載gateはbundleの有無、prepare/prepack、workspace dependencies、patch/module生成物の存在、license/metadata、denied/typosquattingを見ます。commit-pinned treeでpatchが参照するfileが無ければrequires-build、packed Release tarballのrescueは別channelです。npm掲載はmanifest検査が中心で、全tarballの中身やtransitive activationを実行しません。catalog生成成功はinstall成功の証拠になりません。

根拠: [harvestとdeparture](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/registry/scripts/src/build.ts#L162)、[GitHub gate](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/registry/scripts/src/repo-gate.ts#L198)、[掲載と生成説明](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/README.md#L92)。

### reviewed identityとcontent hashは異なる信頼の層

`verified.yml`は取得時空、全communityです。reviewはnpm exact version、GitHub repo+exact commit、Release rescueはrepo+tarball sha256へ固定します。別版（新しい/古い両方）はverified-staleで、nameが同じforkへreviewを移しません。HostのvalidateInstallはcurrent catalog、要求identity、installedSpecとの衝突、acknowledgedを再確認します。Browserから任意shell specを受け取るのではなく、Hostが検証済みrowからspecを構築します。

根拠: [review記録の現在値](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/registry/verified.yml#L1)、[exact review pin](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/registry/scripts/src/tier.ts#L23)、[Host installation gate](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/install.ts#L79)、[spec構築](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/index.ts#L1397)。

catalog loaderはuser npm registry/npmmirror/npmjs/Pagesをprobeし、first successful pointerにcommitします。probe10秒、pointer bulk/read30秒。probe/pointer取得のTransportErrorなら次originへ進み、選んだoriginにcommitした後のdata取得失敗はdisk staleへ進みます。schema/version/hash/coherence不一致はcacheに隠さずthrowします。data file hash、same-origin/plain filename、cached bytesの再検証を行い、stars sidecarだけはadvisoryで欠落を許容します。保存順はdata→pointer→freshnessで、cache write failureは現在verified snapshotの表示を落としません。

根拠: [transportと破損を分けるrace](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/catalog.ts#L560)、[hash/coherence/stars](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/catalog.ts#L639)、[cache保存順](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/catalog.ts#L689)、[default origins](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/catalog.ts#L716)。

pointerとdataのhash一致はpublisherから取ったsnapshot内部の一致です。OFMの固定release鍵の署名とは別で、publisher/registry/originの信頼を置き換えません。Release rescueではHostがtarball hashを事前検査してからpnpmがURLを再取得するため、sourceが明示するTOCTOU windowがあります。今回そのwindowを攻撃・再現していません。

根拠: [tarball事前検査と再取得](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/index.ts#L1419)。

### managerに渡した後も実行と再起動を分ける

required methodsをすべて持つ`pluginManager`があればinstall/remove/toggle/bundle selectをDSHへ委ね、なければ旧Host向けCLI pathです。service半分だけでinstall成功・uninstall失敗にしないcapability detectionです。Hostはawait前にmanagerを一回解決し、Desktop gateと実操作で同じserviceを使います。

manager runnerはprofile queue、requestId別stream log、deadline→cancelInstall、結果fieldのvalidation、once settlementを持ちます。cancelが同期throwしてもmicrotask rejectionへ変え、queueを止めません。`application: applied`、disk changed、build pending、alreadyImported、Client halfを使い、restart/reload理由を分けます。Nodeが同じmoduleをcacheしたままの再導入、self-update、Client HMRは「installBundle成功」だけで新実行版になりません。

根拠: [capabilityと結果field](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/plugin-manager.ts#L15)、[deadlineとsettle](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/manager-runner.ts#L129)、[install委譲](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/host/index.ts#L1638)。

client restart monitorはtab effectより長寿命のpage `Symbol.for`状態/timerを持ち、HMR中のremote call喪失を新carrierへ再送します。Hostは同じcommit済みrestartを返し、tab sessionStorageへbootId/pidを残します。新Hostへreconnectしたらversion/installed/catalogを再問合せし、同じbootIdなら「restartしなかった」を表示します。tab navigation、old-client/new-host、複数tabでreceipt/ownerをどう持つかが自作更新へ持ち帰る条件です。

根拠: [page lifecycleとboot判定](https://github.com/LivXue/dsh-plugin-shop/blob/8db779bf1de6d3307803891c4b0e65fad4af6ef2/packages/dsh-plugin-shop/src/client/restart-monitor.ts#L1)。

### 修正事例: #79と#91は「掲載」と「実行」の差を縮めた

[PR #79](https://github.com/LivXue/dsh-plugin-shop/pull/79)は10-08にmerge、registryのみの修正でplugin releaseを要求しません。作者はcommit-pinned 7,817件中654件でpatch/module fileがなく、107件がRelease rescueで残せたと報告しています。今回この全件計測を再実行していません。buildはprevious lockからnpm departureを照合し、deprecated/search漏れ/unpublishedを区別、GitHub unbuilt markerを持ってbudget内でbackfillする修正です。掲載件数の減少をpluginのruntime回帰と読み替えない条件が得られます。

最新の[PR #91](https://github.com/LivXue/dsh-plugin-shop/pull/91)（10-13 10:41 UTC、現行SHA）はカードのcommit/tag/npm版表示を分けました。`v<7桁>`の一律表示でtagを別版のように切り、commitもsemverに見せていた原因です。さらに「掲載したがinstall/loadしない」ケースを、peer、patch、npm tarball欠損、required service、activation error、pnpm scripts、unpublish/fork別に文書化しています。作者は実DSH 0.2.0-rc.2 fresh homeのprobeを報告します。merge SHAのUbuntu/Windows × 3 host legsとsuitesはsuccessをAPIで確認しましたが、今回shop install/再起動は実行していません。v0.8.6 Releaseは10-10で#91より前のため、同じmanifest版でもこのUI/source改良がnpm配布済みとは保証できません。

[PR #77](https://github.com/LivXue/dsh-plugin-shop/pull/77)も、更新確認後に旧macOS processが残り同版UIを再表示した報告へbootId/reconnect refreshを追加しました。作者のLinux3host live probesは成功、しかしmerge SHAの[Windows/0.2.0-rc.2 job](https://github.com/LivXue/dsh-plugin-shop/actions/runs/37488314532/job/112354074008)はplugin test stepでfailure、build/typecheckはskipです。後続現行SHAの同leg成功と分け、失敗原因を取得したstep名以上に推測しません。

## 自作へ持ち帰る条件と未確認

| 単位 | Pi / Search / Remoraで使うなら確認する条件 |
| --- | --- |
| remote browser proxy | PINの権限範囲、raw launch tokenを補完するowner、Host/Origin変換、直LAN/独自proxy/Cloudflare、WSも同じadmission |
| tunnel intent | 手動stop、Host dispose、process crash、single-flight完了、marker write/rm、child exitを別stateにする |
| ecosystem verdict | repo/commit/artifact/Host/OS/time/logの個別根拠を保つ。historical okをcurrent usableへ昇格させない |
| catalog source race | network errorとschema/hash破損を分ける。同一origin snapshotへ固定し、stars欠落をplugin欠落へ広げない |
| package identity | name、repo stable identity、commit/tag/content hash、installedSpecを別値として照合する |
| update/restart | metadata上の新版、disk版、running版、Client版、bootId/receiptをそれぞれ比較する |

今回の実行はPocket exported pure helpers7assertion、Radar offline identity8testのみです。Pocket server/tunnel/childのstart、Radar private runtime validator、Shop build/install、external API、IM送信、deploy、投稿は行っていません。source file/固定SHA/行番号を照合し、選択Issue/PRのAPI metadataとcomments、check-runsをsnapshotに保存しました。

targeted acceptanceは、Pocketのcookie rotation・Host override・WS guess throttle・compressed HTML・large snapshot/backpressure・rapid stop/start・child exit、Radarのpass/fail conflictと逐条provenance欠落・stale pointerとruntime anchor・rename/fork、Shopのdamaged pointer/hash・offline旧cache・same name fork・reviewed版rollback・Release asset差替え・manager cancel失敗・HMR中restart応答喪失・同一boot再応答を分けて設計します。機能成功と配布/診断だけの成功を同じbooleanにしないことが、この3件に共通する採用条件です。
