# Desktop実装の違いと、壁紙・glassが共有する境界

## 調査境界

[UI・更新・Hostの分析](deep-ui-updates.md)に追加して、2026-10-13のdefault branchを固定した3件を調べる。ここではアプリ全体の機能一覧を作らず、runtime/profileの所有、更新前後の停止、起動条件、media/CSSの解除へ絞る。公開ソースとIssue/PRを読んだ静的調査で、installer・runtime・外部plugin・Wallpaper Engine・GPU検査は実行していない。

| repository | 固定SHA | ソースの版 | 実体 |
| --- | --- | --- | --- |
| [dataelement/dsh-desktop](https://github.com/dataelement/dsh-desktop/tree/115a0b474cc2c4794316171c640a8898398591fe) | `115a0b474cc2c4794316171c640a8898398591fe` | private app manifest 0.1.1 / DSH 0.2.0-rc.2 | Desktop app＋runtime owner |
| [dsh-tauri/deepseek-harness-desktop](https://github.com/dsh-tauri/deepseek-harness-desktop/tree/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7) | `1a1411342593e8f260bd2ffe9ca2ddeafa9731c7` | private app 0.23.2-beta.1 | Desktop app＋runtime owner |
| [elysia395/dsh-wallpaper-engine](https://github.com/elysia395/dsh-wallpaper-engine/tree/0e7c806d7d3013597db909017f7d57bedd0e5a4a) | `0e7c806d7d3013597db909017f7d57bedd0e5a4a` | dsh-plugin-wallpaper-engine 1.3.2 | Web bundle＋media engine |

DataElementのpackage.jsonはprivate appの`0.1.1`である。Issueの製品版0.11/0.12を、この内部manifest値と同一にしない。Tauriもprivate appで、Webへ入れる一般pluginのpeer条件とは別にruntime選択・内部pluginの互換契約がある。

## dataelement/dsh-desktop: generationのdesiredを次回起動へ投影する

### 同梱runtimeと起動条件

Electron appは`@deepseek-ai/dsh 0.2.0-rc.2`などofficial依存を製品側に固定し、Host processを起動する。`HarnessRuntime.start()`は前runtimeを停止してからprofile、Desktop patch、市場を起動するprofileかどうか等を揃える。process stdout/stderr、起動URLとlaunch tokenを持ち、単にportが空いていないことをreadyとしない。[private appと固定依存](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/package.json#L1)、[runtime start](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/src/main/runtime/harness-runtime.ts#L450)、[readyのstability判定](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/src/main/runtime/harness-runtime.ts#L1017)。

stopはchild参照を抜き、SIGTERM後4秒をexitと競争させ、まだ生きていればSIGKILLを送る。ログ・URL・launchTokenを消してidleへ戻る。ここで確認できるのは保持するchildへのsignalで、一般pluginが起動するすべての孫processまで終了する保証をこのコードだけから追加しない。[stopとsignal escalation](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/src/main/runtime/harness-runtime.ts#L629)。

### generationと通常profileを二重管理しない

market installerはgenerationのdesiredを変え、launch側はHostが停止している時にstaging残骸と参照されないgenerationをsweepし、desiredに合わせてprofile linksを投影する。pluginが実行中のgenerationを削除しないための順序を意図している。ただし上記stopChildはSIGKILL送信後のexitをawaitせず返るため、この順序だけで旧processの終了確認まで保証したとはしない。初回起動ではofficial app-bootと同じprofile templateでmanifestを作り、空manifestの先行生成で同梱bundleを失わない。[desired・sweep・投影](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/src/main/state/generation-launch.ts#L17)。

利用者の操作は「marketで導入/更新を選ぶ → staging導入と検証 → desired変更 → appのrestart → 停止中にprojection → 実generationからboot」。通常の`pnpm add`だけでdesiredの所有者を迂回すると、次の起動で古いgenerationが復活し得る。逆にrecoveryで通常manifestだけからpackageを消しても、desiredが残れば再投影される。generation uninstallを明示的に分ける。[generation uninstall](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/src/main/state/generation-launch.ts#L87)。

[anywhere-labs Desktop](deep-ui-updates.md#desktop-profileの更新renderer回復製品更新を分ける)はlauncherのprofileContext、overlay、package-managerを拡張契約として渡す。DataElementはdesiredとgeneration投影を持つ。両方ともHostが起動artifactの選択を所有するが、同じprofile path、同じmarket操作を使える実装ではない。

### 実修正: 自分が所有しないoptional bundleをprojectionで消す

[PR #665](https://github.com/dataelement/dsh-desktop/pull/665)はnative PluginsページでautomationをONにしてもrestart後OFFへ戻る問題を扱い、2026-10-08 14:56:57 UTCにmerge。generation投影が`dsh.profile.bundles`を再構成し、profile dependencyを持たない同梱optional bundleを削っていた。

修正版はgenerationProjection markerと歴史的linkからmanaged bundleを決め、generationが所有する選択だけを増減し、Hostや利用者が持つbundle選択を残す。metadata-only publicationでもretired selectionを消し、所有markerが消えたあと「利用者の選択」として誤保存しない。固定mainでそのfilterとmarker更新を確認した。[ownership付きbundle投影](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/packages/dsh-desktop-market-installer/generations/projection.mjs#L503)。

作者はfocused 35項目とtypecheck/electron-vite等の成功を報告し、同時にOffice payload download timeoutにより正式full build/testが完了していないこと、別旧checkoutの全量成功を現在HEADの成功へ転用しないことを明記していた。merge記録は確認したが、配布installerにこの修正が届く境界や利用者の更新後追認は今回未確認。

[Issue #654](https://github.com/dataelement/dsh-desktop/issues/654)は0.11.0移行でpeer closureが見つからずgeneration migrationがfreezeしmarket変更不能になる報告で取得時open。asar内の同梱依存とprofileのpeer解決起点を照合する入口で、今回は原因の独立再現や全peer validatorの監査をしていない。公開報告にあるclosure不在を、自分が計測した事実として扱わない。

### 製品更新はplugin更新から独立

update-managerはcheck/download/installを別stateにし、同時checkやdownloadを制限する。downloadは利用者の受諾後に明示開始し、特定版のarchive feedは一度のcheck/download後にstableへ戻す。install時は`prepareToInstall`をawaitしてからelectron-updaterの`quitAndInstall`へ渡す。[受諾後download](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/src/main/update/update-manager.ts#L168)、[特定版feed](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/src/main/update/update-manager.ts#L189)、[更新前prepareとinstall](https://github.com/dataelement/dsh-desktop/blob/115a0b474cc2c4794316171c640a8898398591fe/src/main/update/update-manager.ts#L232)。

持ち帰るのは「停止中のprojection」「所有集合だけの再生成」「settingsの候補と次回bootの実artifactを分ける」ことである。狙った検査はoptional bundle ON→restart→ON保持、generation削除→再投影でも復活しないこと、migration freeze時の案内、Host child停止後にinstallerへ移る順序。今回未実行。

## DSH Tauri: shellとNode runtimeを別に更新し、所有するprocessだけを止める

### runtime選択・profile・shell

`deepseek-harness-desktop 0.23.2-beta.1`はTauri shell、Rust側service、React UI、内部DSH pluginsのworkspace。Tauriのversion/identifier/CSP/resourcesが製品配布を定義する。shellからloopback iframeへ接続し、frame-srcはloopback、shell script-srcはselfという別origin構成。Web pluginがCSPを追加すればこのshellも同じ変更を受けるとは言えない。[app manifest](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/package.json#L1)、[shell CSPと配布identity](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/tauri.conf.json#L1)。

Rustのworkflow launchはNodeのentry、`--profile`、Desktop patch、port、no-openを組む。unknown port ownerを殺して奪うのではなく、空port探索と旧owned processのport解放待ちを分ける。runtime本体はversion manifestからrecommended/minimumとplugin互換pairを読み、frontend dependency catalogと同じ版が導入されたと推測しない。[起動引数とport探索](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/launch.rs#L55)、[recommended/minimum DSH](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/config/manifest.rs#L480)。

### 起動・更新・終了のmutex

process ownershipはPIDとWindows handleを同じMutex内のOptionへ保存し、takeで一緒に取り出す。旧processの監視threadはPIDが一致するときだけ登録を消すため、新しく起動したprocessのhandleを旧exitが消さない。core directory swapとprocess起動登録は共通Tokio mutexで直列化する。単なるbool launch guardではswap中にDLLをロードするWindows lockを避けられない。[owned process](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/process.rs#L38)、[PID一致解除](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/process.rs#L102)、[core transition mutex](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/process.rs#L132)。

終了はowned processか保存PID/entry pathを確認した対象に限る。Windowsはtaskkill tree、Unixはlaunch時に作るprocess groupへのTERM/KILLで子treeを扱う。portが占有されるという理由だけで任意processを終わらせる契約ではない。[ownership付き終了](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/process.rs#L239)、[platform別tree終了](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/process.rs#L283)。

### readinessの実修正: loopbackへbindできてもwildcard listenerは生きている

[Issue #1021](https://github.com/dsh-tauri/deepseek-harness-desktop/issues/1021)はremote-web-uiのLAN設定でHostを0.0.0.0へbindすると、実HTTPは200でもshellが未listenと判定し起動timeoutになる報告。Windowsの具体address/wildcard bindの関係が報告条件である。

[PR #1028](https://github.com/dsh-tauri/deepseek-harness-desktop/pull/1028)は2026-10-12 11:41:40 UTCにmainへmerge。port占有判定をloopback/wildcardのいずれかのbind失敗で占有、両方成功で空きとする判定へ変更し、port release/available/heal判定も同じhelperを使う。固定mainに修正あり。作者は両bind方向と解放後の回帰・旧実装mutationでの失敗を報告するが、cargo全量は1,009成功/1失敗で、失敗をstashした同baselineでも確認したと記す。今回のWindows再現ではない。[両addressの占有判定](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/utils.rs#L188)。

さらにhealthは「port占有」からHTTP boot manifest取得、Client module URL一覧、bundleらしいbodyの全件検査へ進む。並列probeの結果を入力順に戻し、failure順序の揺れを「進展があった」と誤認してinactivity deadlineを伸ばさない。owned processが未登録でもlaunch guardが保持される間はstarting、guard終了後もownedがなければnot-ownedに分ける。[boot manifest probe](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/health.rs#L18)、[順序を保つbundle probe](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/health.rs#L86)、[ownershipとreadiness](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/workflow/health.rs#L141)。

### 外部installerへの引渡しは更新完了ではない

Desktop updaterはGitHub metadataのSHA-256がある時だけmirror fallbackを許す。digest欠落でもofficial直結は許すという契約で、全downloadが必ずdigest検査済みとは説明できない。downloaded installerはOS handlerへ渡し、Windows UAC、Linux package manager、AppImageを別に扱う。最近5件のinstaller保持もruntime rollback能力とは別。[download sourceとdigest方針](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/update/install.rs#L1)、[installer保持](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/update/install.rs#L33)。

`open_installer`はowned Harnessを先にstopし、installerがshellを強制終了して孤児Hostがportを保持することを減らす。stop失敗はwarningでinstaller openを止めない。pending markerを消すのはOSへ渡した後で、installer適用完了の証明ではない。Linux AppImageはsingle-instance lockを解除してexitし、新binaryを採用させる。[Host停止とOS引渡し](https://github.com/dsh-tauri/deepseek-harness-desktop/blob/1a1411342593e8f260bd2ffe9ca2ddeafa9731c7/src-tauri/src/service/update/install.rs#L766)。

[Issue #1042](https://github.com/dsh-tauri/deepseek-harness-desktop/issues/1042)はlocal Nodeを採用しbundled runtime取得をskipした時、npm/npx shimが不存在のbundleへ向き、PATH forwarderと再帰する報告で取得時open。shell更新、DSH core更新、Node/npm/shim選択を一つの最新版という状態へまとめない。

狙った検査はunknown processがportを占めても殺さないこと、old exit threadがnew PID登録を消さないこと、directory swapとlaunchの並行、localhost/wildcard readiness、installer失敗時のpending状態、local Node＋不存在bundle＋forwarding npmの組合せ。今回は実行せず検査条件を整理した。

## Wallpaper Engine: mediaのengine解除とglassのtoken解除を分ける

### package・配布・Host権限

`dsh-plugin-wallpaper-engine 1.3.2`はWeb用bundleでHostはwebServer hard inject、Clientはdsh-client-runtimeをimmediately要求する。Node>=18、DSH>=0.1.5-rc.1を宣言し、lib/client.jsやvendored WebWallGLをfilesへ含む。buildはsrc module群をClient bundleへinliningする。sourceを直して生成Clientを配布し忘れると、同じrepoのHost/Clientがずれる。npm runtime依存へengineを移す[PR #196](https://github.com/elysia395/dsh-wallpaper-engine/pull/196)は取得時openで、固定版はvendored配布。[manifestと同梱file](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/package.json#L1)、[Host hard inject](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/lib/index.js#L2843)。

Hostはinventory、settings、media/scene、upload、font/preset等のrouteを登録し、独立loopback media originも使う。一般skinと違い、local assetの読み出し、転码process、stream/file descriptorまで所有する。API一覧だけで全path/token/bodyの妥当性を確認したとはしない。

### 解除の具体経路

Host applyのdisposerはroute群、startup sweep timer、独立media serverを解除し、ACTIVE_FFMPEGへkill、処理中transcode jobをerrorへ置換、inflight Map、mediaMap、active streamをdestroyする。process.killを呼ぶことと、その孫treeまでreap済みであることは別。I/O中promiseは取り消せないため、旧finallyと新applyのmapの関係も検査点になる。[stream台帳とapply単位状態](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/lib/index.js#L2932)、[Host disposer](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/lib/index.js#L3190)、[media server解除](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/lib/media-origin.js#L179)。

Clientのeffect撤回はglobal listener、visibility/page lifecycle、rotation timer、準備media、video prewarm、FX/parallax/avatar、古いfade層、CSS/tokenを順に片付ける。切替の準備だけで実mountされなかったiframeもengineを持ち得る。`cancelLiveMount`は未接続iframeを画面外で一度documentへ接続しabout:blankへnavigate、後でremoveする。DOMからdetachしたiframeへsrcを書くだけではnavigationがcommitせずWebGL/RAFが残るという作者の観測を前提にした処理。今回GPU解放を計測したわけではない。[Client effect撤回](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/src/client.js#L5945)、[prepared iframeの中止](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/src/live-layer.js#L1478)。

warm videoはpause＋src除去＋loadでdecoderを手放す。live frameはonloadをfirst-frameと同一視せず、heartbeat/fpsなどの状態を待つ。hidden/pausedのframeにはsrcをまだ割り当てず、可視復帰後にpayloadを開始する。[video prewarm撤回](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/src/video-layer.js#L65)、[live frameの遅延開始とonload](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/src/live-layer.js#L1572)。

第三者Web壁紙はrender URLにstrict sandboxを指定し、内側HTMLをDSHのoriginへ昇格させない。sceneとwebのmedia originは同じ扱いではなく、remote browserではloopback mediaへ直接到達できないためapplication originへのfallbackもある。Outer iframeのautoplay許可とinner workshop sandboxは別の権限。[originとstrict sandboxの指定](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/src/live-layer.js#L164)。

### Issue対応を追ってもdefaultに残る設計がある

[Issue #176](https://github.com/elysia395/dsh-wallpaper-engine/issues/176)は、一度Electron UAのClientが接続するとprocess-wide adapter latchがdesktop判定になり、同じHostを開くFirefoxもdesktop向けpaintを使う報告。取得時closedだが、固定ソースには`adapterFenceSeen`/`adapterShellSeen`のonly-increase latchと「手選 > Host report > local detect」の優先が残る。手選browserで回避した報告は、request/client別の自動判定へ修正された証拠にはならない。[process単位adapter latch](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/lib/media-origin.js#L40)、[判定優先とClient側contract](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/src/adapter.js#L1)。

[Issue #200](https://github.com/elysia395/dsh-wallpaper-engine/issues/200)はshared alias tokenをglass用の半透明色へ変える一方、第三者panelにはblur carrierがないため前後の文字が重なる報告。取得時closedで、対処を提案する[PR #204](https://github.com/elysia395/dsh-wallpaper-engine/pull/204)はopen・未merge。PRはuser selectorを限定して::before carrierへblurを足す設計と41項の検査を報告するが、固定mainの提供機能としては扱えない。sourceにはpage glass gateが常時付き、面ごとのOFFとshared token全体のOFFが異なる。[page glass gate](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/src/glass.js#L34)。

[PR #195](https://github.com/elysia395/dsh-wallpaper-engine/pull/195)もclosed・未mergeで、X11 occlusion pipelineと「意図的pauseを転送失敗と誤認しない」修正を提案した。WebGLの非可視pause設計を考える参考にはなるが、Linux X11 occlusion対応がfixed 1.3.2へ提供されたと書かない。

### Glass/PWAへ持ち帰る干渉検査

Wallpaper Engineのglassは`--dsw-alias-*`等の共通tokenへ作用し、利用者が導入した第三者panelにも色が伝わる。一方blur/backdrop-filterはそのpanel自身に自動的には生えない。token変更のconsumerを列挙し、透明度だけが伝わる状態を調べる。backdrop-filter/transformをshared ancestorへ置くとfixed descendantsの包含ブロックが変わるため、overlayの座標とPortal先も確認する。

skin-centerの`html[data-dsh-skin]`があると壁紙、glass gate、rotationをyieldし、解除後に復帰する。これは特定markerの一方向協調で、任意のGlass pluginが同じmarkerを持つ保証はない。新しいpluginで採用するなら互いのnamespace・所有するCSS/token・解除時の値比較を決める。[skin interopのeffect登録](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/src/client.js#L6158)、[現行協調の限界](https://github.com/elysia395/dsh-wallpaper-engine/blob/0e7c806d7d3013597db909017f7d57bedd0e5a4a/docs/COEXISTENCE.md#L13)。

PWAではreloadだけでなくvisibility hidden→visible、pageshow/bfcache、offline→onlineを通る。準備iframeやdecoderを残してから復帰する場合、同selectionでも古いgenerationのpoll responseが新frameへ届かないことを調べる。Service Workerがplugin Clientをcacheする場合は、Host設定schema/API版とClient生成物が異なる更新状態も検査対象になる。ここは適用提案であり、特定のPWAとこのpluginの共存を今回再現した結果ではない。

## 操作と検査の比較

| 操作 | DataElement | Tauri | Wallpaper Engine |
| --- | --- | --- | --- |
| plugin更新 | desired→停止中projection→起動 | Node/profile/内部plugin互換とcore transition | npm/Client生成物とHost登録 |
| restart | 保持childのTERM→KILL、generation sweep | owned tree終了、port release、launch registry | 一般Hostへ委譲、apply解除が先 |
| 製品更新 | electron-updater、prepare→quitAndInstall | digest方針、OS installer open、owned Host停止 | app installerを所有しない |
| UI/media解除 | shell/Hostのlifetime | WebViewとNode Hostのlifetime | iframe engine、video decoder、FX RAF、CSSを別に撤回 |
| 未確認 | 実installer・peer閉包全体・孫process | Windows/Unix終了、実署名、Node shim再帰 | GPU、全asset境界、第三者Glass/PWA共存 |

再利用する契約は、derived stateが所有する集合だけを更新すること、old exitやold disposerが新状態を消さないこと、起動能力をport→HTTP→Client module→UI frameへ分けること、更新artifact検証とOS引渡しを分けること、mediaの停止とDOM removalを別に確認することである。

snapshotは`ui-updates/desktop-theme-manifest.json`とIssue/PR JSON。固定リンクのfile/行番号はcheckoutで存在確認した。公開作者の検証報告を当調査の実行結果にしていない。製品版・npm publish・installer配布の全境界は未確認。
