# UI・更新・Hostの境界を実経路から調べる

## 調査境界

2026-10-13に8 repositoryの公開default branchを取得し、下表のSHAへ固定した。`dsh-web`のdefaultは`dev`、Desktopは`master`である。前回の[UI概説](ui-and-runtimes.md)と[更新概説](marketplaces-and-updates.md)に対し、今回は利用者の操作がどの状態を変え、誰がその状態を読み直すかを追う。

対象はtopic検索の上位から選んだ実装比較であり、topic全体19,027件を網羅しない。検索で取得した1,000件はGitHub検索上限で、starsは利用者数や品質点数に変換しない。小さい表示機能でもHost側の永続化やHTTP経路を持つため、画面の面積から権限や保守量を判断しない。

ここでの確認はソース・manifest・公開Issue/PR/commentの照合である。外部pluginのinstall、build、起動、認証、課金、OS操作は実行していない。作者が実施した検証、利用者の追認、今回の静的観測、今後実行する検査を分けて記す。package版は固定ソースの値で、registryの配布物と同一であることまでは保証しない。

## 比較表

| repository | 固定SHA / package版 | 実体・導入先 | 主な所有者 |
| --- | --- | --- | --- |
| [dsh-market/dsh-market](https://github.com/dsh-market/dsh-market/tree/9afd39d947f68e1299a327ead6ce1be7441cd4b2) | `9afd39d947f68e1299a327ead6ce1be7441cd4b2` / `dshmarket 1.66.20` | Host＋Web bundle | 更新操作・profile mutation、Client queue |
| [omdsh-dev/DSH-better-sidebar](https://github.com/omdsh-dev/DSH-better-sidebar/tree/d0a47bed1175e8214fc45bacf8535cc0b4d386a0) | `d0a47bed1175e8214fc45bacf8535cc0b4d386a0` / `dsh-better-sidebar 0.25.0` | Host＋Web bundle | tab/viewer registry、Host terminalの表示 |
| [zhu1090093659/dsh-web](https://github.com/zhu1090093659/dsh-web/tree/1ba416adaf54ee811c5c596307e82789a9bb9586) | `1ba416adaf54ee811c5c596307e82789a9bb9586` / `@linxin666/dsh-web-all 0.4.6` | family集約bundle | shell fiber、CLI job、互換DOM |
| [ccch1mneyyy/dsh-TUI](https://github.com/ccch1mneyyy/dsh-TUI/tree/d18dc5b0e27a5502c967349a78e4d535f31c9de2) | `d18dc5b0e27a5502c967349a78e4d535f31c9de2` / `@deepseek-harness-tui/dsh-tui 0.14.0` | terminal front door | stdin、backend、restart handoff |
| [anywhere-labs/dsh-desktop](https://github.com/anywhere-labs/dsh-desktop/tree/6bc000ba031700b2252cdb73c2b4f1d288a97c56) | `6bc000ba031700b2252cdb73c2b4f1d288a97c56` / `stable 2.0.17 / beta.2 / next` | Desktop app workspace | profile/runtime/shell/installer |
| [bowenliang123/dsh-context](https://github.com/bowenliang123/dsh-context/tree/a5438855d7bbc1ab9f1c36b20dbc45564716b052) | `a5438855d7bbc1ab9f1c36b20dbc45564716b052` / `dsh-context 0.69.1` | projection＋Web bundle | cold read、projection、slot |
| [MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/tree/5247dd6813d6e4430728f39ccc63d43cda046022) | `5247dd6813d6e4430728f39ccc63d43cda046022` / `dsh-whale-widget 0.4.2` | Host＋script injection | ledger、HTTP、page DOM/audio |
| [Small-tailqwq/dsh-deep-whale](https://github.com/Small-tailqwq/dsh-deep-whale/tree/bcb12f15a19590e6d0e9890bd498590fae3c58df) | `bcb12f15a19590e6d0e9890bd498590fae3c58df` / `manager 0.1.6 / skins 0.1.7` | skin packages＋manager | body/CSS/observer、skin registry |

## dsh-market: 更新を一つのボタンから一つの操作へ分解する

### 導入・登録・信頼境界

`dshmarket`はHostとWeb Clientを持つbundle。patchは`dsh-market`行をinsertし、Clientはlocale/settings/themeを要求する。Host peerはCordis、settings、schemasteryで、Clientのservice宣言と同じ集合ではない。公開更新APIはDSH共通APIではなくこのpackageのbeta契約である。[manifest](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/package.json#L1)、[patch](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/cordis.patch.yml#L1)、[Client登録入口](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/client/index.ts#L1)。

重要なのはprofileの選択と、package-manager/HMRを提供するHostの能力である。更新ボタンがprofileのpackageを変えられることと、そのHostが次回使うartifactを変更できることは別。既存の[generation管理の事例](../workflow/ecosystem-cases.md#1-dsh-market-497-更新できる状態の所有者が違った)と併読する。

### 更新APIとブラウザー復帰の別々の記録

`UpdateOperationStoreV1.create()`は`bootId-update-sequence`を採番し、beforeVersion、installedVersion、進捗、restart/refresh、rollback状態を持つ。registryはprocess内Mapで既定50件。画面の再接続に照合できるが、Host再起動を越える永続履歴ではない。`start()`と完了時のactivation判定があり、HTTP応答の受信だけを「新しいコードが実行中」にしない。[操作store](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/update-api-v1.ts#L149)、[完了・activationの記録](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/update-api-v1.ts#L207)。

一方Clientの`dshm-queue-v1`はlocalStorageへqueued操作を保存する。これはHost operation履歴と異なる。復帰時に読み直したqueued操作は、現在のinstalled・updates・catalogと照合し、適用条件を満たす対象について、Hostが空いたらdrainが実行する。既定動作では再度のクリックを要しない。更新チェックだけの自動実行と、すでに利用者が依頼してqueuedになった変更の自動実行を混同しない。[queue復元](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/client/MarketSection.tsx#L1809)、[drain](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/client/MarketSection.tsx#L4135)。

利用者が通る順序は「候補を確認 → 更新を依頼 → Hostのmutation lock／agent busyを照合 → 実行またはqueue → 導入版とactivation結果を確認 → 必要なら画面refresh／Host所有者によるrestart」である。別pluginが更新APIを使う場合は、capabilities取得、202のoperationId保存、GETによる終端状態照合を加える。processが変わってIDが見つからなければ、導入版・実行版の再確認が必要で、記録消失を成功扱いできない。[API storeの生成](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/routes.ts#L1848)。

### 設定保存と更新の競合

route群は共有`mutationChain`を持つ。軽い状態保存をqueueする経路と、busy時409を返すpackage変更経路がある。state全体を書く前のdisk再同期は、snapshot復旧や別writerの変更をboot時closureで消さないため。settings側では既存state.jsonと同じ値の第二writerを増やさない意図を明記する。これは一つのplugin内の直列化で、外部CLIや別processを含む分散lockの証拠ではない。[state再同期](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/routes.ts#L645)、[共有mutation chain](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/routes.ts#L780)、[第二writerを避ける理由](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/settings.ts#L15)。

### Issueから実修正: loader行とpresetの中身を取り違える

[Issue #841](https://github.com/dsh-market/dsh-market/issues/841)は、二つのpreset bundleを共存させると、presetの`config.plugins[].id`がloader行IDとして収集され、存在しない衝突を理由に後から入れたpackageが除去される報告。症状は「互換性判定で導入が失敗」だが、pnpmやregistryの失敗ではなく、所有する行を誤って推定した問題だった。

[PR #844](https://github.com/dsh-market/dsh-market/pull/844)は2026-10-13 05:01:37 UTCにmainへmerge。通常pluginのconfigをpayloadとして除外し、`group: true`かつlist configの子loader行は保つ。作者は2,219 tests、typecheck/build/restart smokeの成功と、修正前に失敗する用例を報告。[配布確認comment](https://github.com/dsh-market/dsh-market/issues/841#issuecomment-6138805786)は1.66.19のnpm生成物を作者が確認した記録で、今回のtarball検証ではない。

取得した1.66.20にも修正は入っている。ただし[PR #849](https://github.com/dsh-market/dsh-market/pull/849)はopenで、`- config:`を先頭に置くなど別の合法YAML形がscannerから漏れる追補を提案している。「#841 close」と「全YAML形の正しさ」は別である。[patch行scanner](https://github.com/dsh-market/dsh-market/blob/9afd39d947f68e1299a327ead6ce1be7441cd4b2/src/profile.ts#L877)。

もう一つの[PR #845](https://github.com/dsh-market/dsh-market/pull/845)は空queueでも2秒ごとに/statusを取得していた処理を、queue存在確認後のfetchへ変更した。固定版にその順序と`disposed`／clearIntervalがある。一方[Issue #838](https://github.com/dsh-market/dsh-market/issues/838)の手動queue実行設定はこの修正に含まれない。closeした報告の一部だけが実装された例である。

**持ち帰る契約:** 操作IDと実行版を分け、永続化するqueueとprocess内operationを分ける。衝突検査は実Loaderが解釈する行集合に合わせる。**狙った検査:** 同じofficial pluginをpayloadに持つ異なるpreset二つは許可し、group子行の同IDは拒否する。config先頭・キー順・余分な空白も変える。空queueで2秒tickを越えて/statusが増えず、queued時には増えることを確認する。これらは今回未実行。

## Better Sidebar: tabの住所、内容、terminal processを別々に所有する

### 拡張APIと解除

`dsh-better-sidebar 0.25.0`のbundleはWeb用。Clientにlocale、slots、conversation、sidebar-right、modulesを宣言し、HostにwebServer、sessions、webRuntime、toolsを要求する。Hostの必須service欠落はUI一部の欠落ではなく行全体のpendingになる。[manifest](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/package.json#L1)、[Host inject](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/index.ts#L113)。

`registerTab`／`registerFileViewer`は同IDを拒否し、返すdisposerはMap内の値が登録時descriptorと同一の場合だけ消す。古いfiberのdisposerが新しい登録を消さない契約である。登録IDのnamespaceは下流pluginの責任で、固有名にする必要がある。Client native surfaceもeffectでdisposeする。[identity付き登録解除](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/client/service.ts#L839)、[native surfaceの解除](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/client/index.tsx#L193)。

HostのrouteとWS upgradeはeffect登録。最後にagent-open registryとWebSocketServerをcloseする。ファイルwatch接続は接続単位の生存期間を持つため、server解除、既存socket、個々のwatchを別に確認する必要がある。登録disposerが存在することだけで、全接続が即終了するとは断定しない。[file watch登録](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/index.ts#L1593)、[Host teardown](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/index.ts#L1606)。

### fileとterminalの権限

`ensureWorkspacePath`はhistorical nameで、現在はlexical path解決。`~`展開、cwdへの相対解決を行うがworkspace containmentやrealpath制約は行わず、symlink経由のwriteも拒まない。OS userの権限を使うUI file操作であり、Session/model tool sandboxを自動継承すると説明できない。browser trust fenceはHost/Origin系のcross-site対策で認証ではない。[path権限方針](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/path-security.ts#L1)、[trust fenceの境界](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/trust-fence.ts#L1)。

HTML previewは共通sandboxにallow-same-originを含めず、編集viewerには設定によりsandbox解除がある一方、changes previewは常時sandboxとする。preview種類を分けて検査する。[sandbox契約](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/client/html-preview.ts#L1)。

terminalはplugin独自PTYではなくHostの`webTerminals`を構造的に読む。必須injectに入れず、そのserviceがない配置でもterminal tabだけ降格できる。`view(sessionId,key,contentId,...)`のcontentIdで復帰時に既存processを採用し、`mount()`の解除はDOM detach、`close()`がprocess終了。render revisionのackはemulatorの書込完了に合わせ、writableなattachmentだけinput/resizeを送れる。これらはpluginの消費するHost契約で、この調査ではHost実装全体を実行検証していない。[terminalの所有・復帰・ACK](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/client/terminal-client.ts#L1)。

利用者の操作は「会話を選ぶ → fileを開く／terminal tabを作る → 別会話や別carrierへ移る → 戻る」である。tabを隠す、DOMをunmountする、tabを閉じる、Hostをrestartするの各操作で残すものが違う。processを残すdetachを全解除とみなすと、使わなくなったshellや逆に消したくないshellを扱い損ねる。

### Issueから実修正: pendingをHTTP設定と誤認しない

[Issue #931](https://github.com/omdsh-dev/DSH-better-sidebar/issues/931)はDSH 0.2.1-alpha.2でwebRuntimeが消え、pluginがpendingのまま、ブラウザーに残ったUIからのPOSTが静的fallbackへ落ち405になる報告。利用者commentにはmacOSでも再現したことと三箇所の熱修後にAPI/filetreeが復帰した追認がある。これは当人の環境の記録で、今回の再現ではない。

[PR #932](https://github.com/omdsh-dev/DSH-better-sidebar/pull/932)はdev向けのrequest時service検出、[PR #943](https://github.com/omdsh-dev/DSH-better-sidebar/pull/943)はmain向けのargvからtrusted-hostを読む変更で、取得時はいずれもopen・未merge。固定mainにはhard injectと`ctx.webRuntime.trustedHosts`が残る。PRの動作報告を0.25.0全利用者へ届いた修正と書けない。[固定mainのfence参照](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/index.ts#L1199)。

### Issueの追加掘り下げ: rename後の再配信で旧pathへ戻る

[Issue #915](https://github.com/omdsh-dev/DSH-better-sidebar/issues/915)では、filetreeでa.mdをb.mdに改名してもnative右sidebarのeditorは旧pathを保持し、次の保存でa.mdを作り直す。[PR #917](https://github.com/omdsh-dev/DSH-better-sidebar/pull/917)はclosedだがmergeされていない。[置換理由のcomment](https://github.com/omdsh-dev/DSH-better-sidebar/pull/917#issuecomment-6111935919)は、#912には同revisionのnavigation再配信がplugin側retargetを戻さないgateと、renameを別fileへのreloadと誤認してdraftを捨てない保護がある、と説明する。

ここでの契約は「tabを列挙してpathを書き換える」だけではない。「同navigationを再配信しても修正を維持し、本当に新revisionのnavigationは採用する」「fileの名前だけ変わった場合は未保存bufferを維持する」まで必要になる。#917の作者が報告した列挙のnegative controlは、その再配信経路の検査にはならない。[PR #929](https://github.com/omdsh-dev/DSH-better-sidebar/pull/929)は背景会話のtabとcustom title保持の追補でopen。dev上の修正と固定mainの配布境界を同一視しない。

**狙った検査:** nativeとbottom両carrierで、会話Aのdirty editorを開く → 会話Bへ切替 → Aのfileをrename → 同revision再配信 → Aへ戻って保存。新path、buffer、custom titleをそれぞれassertし、次revisionはnavigationを通す。未実行。

## dsh-web: aggregateの一行成功からfamilyの起動成功へ進む

### packageとfamilyの構成

repository全体の`dsh-web`と導入する`@linxin666/dsh-web-all 0.4.6`は別。aggregate patchは`web-ui-*`の固有行とper-family subpathを使い、row configの`plugin`が実packageを指す。SSH/skill-explorerはopt-inで初期disabled。外部pet/skin/preset/community bundleもあり、すべてがaggregate自身の実装ではない。`dsh.engines.dsh`とpeerは>=0.2.0-rc.2、aggregate Client injectは空でもfamilyの要求は消えない。[aggregate manifest](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-web-all/package.json#L1)、[生成patch](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-web-all/cordis.patch.yml#L1)。

### fault shellの起動・設定変更・解除

shellは必須serviceなしでactivateし、import失敗、module shape不正、同期apply例外、fiberの遅いstartup失敗を別に捕捉する。degradedとactive-rowのledgerを公開する。degraded rowもactiveとして残し、UIを消して成功に見せず状態を案内する。これは障害の局所化であり、任意のsubprocess／globalイベントの未捕捉例外まで隔離するprocess sandboxではない。[shell入口](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-web-all/src/index.ts#L1)、[遅いstartupの監視](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-web-all/src/shell.ts#L351)。

設定変更は`loader/volatile-update`からtailへ直列化し、同package・同configなら再mountせず、変われば旧fiberをdisposeしてから新moduleをmountする。同期例外の捕捉と、後からinjectが満たされて起動するfiberのstatus監視の両方が必要。missing plugin keyを含むbare overrideは、patchがconfigを丸ごと置換する仕様に合わせて扱うため、利用者がfieldだけ上書きするつもりで`plugin`を落とすと実familyが消える。[config同期・replace](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-web-all/src/shell.ts#L394)、[volatile-update/status監視](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-web-all/src/shell.ts#L500)。

Client compat shimは旧DOM hookを現在shellへ付与する。namespaced loader行は共存を助けるが、standaloneとaggregateが同じslot/CSS/bodyを触る場合の二重mountを防ぐ証明にはならない。[Issue #1863](https://github.com/zhu1090093659/dsh-web/issues/1863)は創意工房の外部リンクで未宣言sidebarRightを読む例外の報告で、取得時closedで、修正内容や配布境界は今回追っていない。aggregate manifestだけを見てClient serviceが揃うと判断できない。[Client compat入口](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-web-all/src/client/index.ts#L1)。

### plugin-managerの更新と永続化

plugin-managerはinventoryをprofileから読み、install/removeをofficial CLIへ委譲し、enableはdisabled overrideへ書く。`CliGateway`はprocess内job tableとmutation queueを持ち、完了jobを100件保持する。direct profile writeも同じ`withMutationLock`へ入れる契約。拒否したtaskの結果は呼出元へ返し、queue tailだけを回復するため、一件の失敗で次の操作を止めない。Host再起動後もstatus(jobId)が残る永続storeではない。[official CLI委譲](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-plugin-manager/src/index.ts#L1)、[job table・mutation queue](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-plugin-manager/src/host/gateway.ts#L684)。

利用者の順序は「pluginページでupdateを選ぶ → id/source/npm候補/互換性を確認 → jobを開始 → statusをpoll → CLI exitと変更差分を確認 → 必要ならrestart」である。update routeは非npm直接依存を一律にnpmへ変換しない。SSHやgit操作などfamily別の権限を、このmanagerのloopback fenceから推測しない。[update route](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-plugin-manager/src/host/routes.ts#L321)。

### Issueから実修正: spawn失敗はclose待ちだけでは終わらない

[Issue #1857](https://github.com/zhu1090093659/dsh-web/issues/1857)はWindowsのPATHにSystem32がなくcmd.exe spawnが失敗し、error listener不在でHostごと終了する報告。[PR #1859](https://github.com/zhu1090093659/dsh-web/pull/1859)は2026-10-12 02:38:30 UTCにdefaultのdevへmerge。固定版には大文字小文字を吸収するComSpec/SystemRoot解決、spawn outletのguard、error/closeの両方でsettleするwaiterがある。[cmd.exe path解決](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-plugin-manager/src/host/gateway.ts#L330)、[spawn guardとwaiter](https://github.com/zhu1090093659/dsh-web/blob/1ba416adaf54ee811c5c596307e82789a9bb9586/packages/dsh-plugin-manager/src/host/gateway.ts#L454)。

作者はreal ENOENTを含む11用例、guardを外すnegative control、package 338 testsと全repoチェック成功を報告。今回はソースで変更を確認しただけ。0.4.6というmanifest値は据え置きなので、同番号の公開tarballへこのdev修正が届いたとは断定しない。

**狙った検査:** binary発見後に実行fileを消す、cmd.exeのbare lookupを失敗させる、errorだけを出すchild seamを使う。Hostが生存し、jobがerrorへ終端化し、次のqueue操作が実行可能なことをassertする。import/apply/pending→late-failureを個別に注入してdegraded ledgerも確認する。未実行。

## TUI: UI解除だけではterminal入力を渡せない

### bundle・backend・上流との境界

`@deepseek-harness-tui/dsh-tui 0.14.0`はterminal front door。packageにWeb Client宣言はなくbundle patchを持つ。patchはbaseのtool/sandboxなどを継承しつつ、system-prompt personaやprovider設定、preset構成を上書きする。画面skinだけの追加と同じscopeではない。公式packageへのimportはdsh-adapterへ集約し、backend capabilityはdeclared/staged/live/degradedを分ける。serviceを見つけたことだけでlive契約へ公開せず、probe evidenceと昇格の境界がある。[front doorと設定上書き](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/cordis.patch.yml#L1)、[adapter入口](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/src/index.ts#L1)、[capability公開barrier](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/src/adapter/kernel/lifecycle.ts#L1)。

peerは多数のofficial packageの列挙版を持ち、app-bootやcmdlineなどに0.2.0-rc.2固定を含む。版が大きければ自動的に互換ではない。[既存のpnpm/旧patchの履歴](../workflow/ecosystem-cases.md#4-tui-60-pnpm版の問題に見えて解決の起点が問題だった)に加え、Loader entry、patch、runtime module、backend SDKの解決起点を揃える必要がある。[package peerとexports](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/package.json#L1)。

### query、restart、ACKの三つの状態

`TerminalQuerier`はstdinを共有し、queryごとのresponse typeとDA1 sentinelで応答を束ねる。dispose/suspendで待っているqueryをundefinedへsettleしraw-mode leaseを解放する。dispose後のsend/flushはterminalへwriteしない。sentinelは最初のbatchまで解決し、後続batchを壊さない。terminalが順序どおりDA1に応答する前提もあり、あらゆるterminal環境でtimeout不要という保証にはしない。[send・flush・dispose](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/src/ink/terminal-querier.ts#L277)、[responseとbatch処理](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/src/ink/terminal-querier.ts#L363)。

restart/内核切替ではattemptIdを発行し、子processからfd 3へ`screen-adopted`／`first-frame`等のACKを返す。受信側はattemptId一致を確認する。spawn成功、画面採用、最初のframe、後からsessionが失敗する状態を分け、30秒ACK watchは診断で成功/失敗の判定に使わない。[ACK契約](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/src/handoffAck.ts#L22)、[attemptとACK照合](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/src/update.ts#L2229)。

### Issueから実修正: removeListener後も旧processが読む

[Issue #1508](https://github.com/ccch1mneyyy/dsh-TUI/issues/1508)はKittyで/dsh→/codexを切替後、画像queryが長時間停止し、追加の入力で復帰する報告。画像downloadの遅さではなく、旧processが移譲後もterminal replyを先読みするという診断である。[PR #1509](https://github.com/ccch1mneyyy/dsh-TUI/pull/1509)は2026-10-12 16:08:44 UTCにmainへmergeし、固定版に`detachHandoffStdin()`とspawn直前の呼出がある。

helperはreadable/data listenerを消し、`_read`の再充填を抑え、pause、内部`_handle.readStop()`、任意能力のunrefを呼ぶ。TTY handleをdestroyすると親のtermios保存値が子のraw modeを上書きするため閉じない。通常のeditorへの一時貸与は別のsuspend/resumeで扱う。[永久input移譲](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/src/ink/stdin-handoff.ts#L1)、[spawn前の移譲](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/src/update.ts#L2256)。

作者はLinux Kitty 0.49.2のfullscreen/inline反復、real PTY、pipe fallback、Node 22/24等を報告し、Windows ConPTYとBunは未実測と明記する。今回もそのplatform検証は追加していない。Node内部API依存を一般的なdisposer例として無条件にコピーできない。

**狙った検査:** 親がstdinを一度読み始めたPTYで移譲し、移譲後に親のread(0)を誘発し、子だけがDA1を受け取ることと親buffer空をassertする。query disposerのunitだけでは欠落する経路。[repositoryの検査script](https://github.com/ccch1mneyyy/dsh-TUI/blob/d18dc5b0e27a5502c967349a78e4d535f31c9de2/scripts/verify-handoff-pty-gate.mjs#L1)はそのための入口だが、今回未実行。Session復帰・保存profileの互換性は別に検査する。

## Desktop: profileの更新、renderer回復、製品更新を分ける

### appとして所有するもの

`anywhere-labs/dsh-desktop`はworkspaceと複数editionで、stable 2.0.17、beta 2.0.17-beta.2、next 2.0.17-nextを別packageとして持つ。Web Client注入、shell、配布runtime、market選択、profile overlayはappが所有する。単独UI pluginの責務を越える。[stable manifest](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-plugin-desktop/package.json#L1)、[beta manifest](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-plugin-desktop-beta/package.json#L1)、[next manifest](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-desktop-next/package.json#L1)。

`createDesktopProfileBoot`はpnpmのprofile名・dir・homeと起動済みprofileの一致を検査する。manifest解決もmodule loaderが選ぶoverlayのcopyを使い、packageManagerに同梱executable、pnpm、Node shim、Electron targetを提供する。`readPatches(profilePatches)`は設定editorが検証中のpending documentを受け、shell/platform overrideとoverlayを保った構成を作る。pluginが自分でCLI再構成するとこの文脈を落とす。[profile identityとpackage-manager](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-plugin-desktop/src/profile-context.ts#L12)。

ready通知は成功したbootだけで発行し、listenerとdisposed状態をeffectで解除。checkpointは3 slotの宣言的fileで、node_modulesをcopyせずpnpmも実行しない。「設定を戻す」と「以前のruntime binaryへ戻す」の意味が違う。[readiness解除](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-plugin-desktop/src/profile-context.ts#L72)、[checkpoint範囲](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-plugin-desktop/src/profile-checkpoint.ts#L1)。

### Issueから実修正: release serviceの302を追えないupdater

[PR #1343](https://github.com/anywhere-labs/dsh-desktop/pull/1343)はNext updaterの実download failureを扱い、2026-10-10 09:53:12 UTCにmasterへmerge。Electron net.fetchはmanual redirectで3xx responseを返さず拒否するため、release service→storageの302を辿れなかった。修正版は`net.request`でhopごとにHTTPS/default portを検査し、redirect時に旧requestをabort、新requestを発行する。

release selector headerは最初のhopだけ、storageにはAccept等だけを送り、非永続session partitionでcredentialを持たない。abortは先に外向きpromiseをsettleしてからrequestを止め、内部abort eventが利用者に見せるエラーを置き換えない。最終URLとbody streamをdownload verifierへ渡す。[abort・redirect・headerの所有](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-desktop-next/src/update-transport.ts#L45)、[artifact download検証](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-plugin-desktop/src/update-download.ts#L136)。

利用者の順序は「更新check → 対象releaseを確認 → download → bytes/digest/installer種別確認 → prepare → install/restart」。Nextのstateもchecking/available/downloading/preparing/ready/installing/errorを分ける。[download再checkとstate遷移](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-desktop-next/src/updates.ts#L96)、[UI stateとaction](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-desktop-next/src/update-state.ts#L1)。

PRはmacOSのreal Electron transport/local302、Windows packagingと依頼者によるcustom install dirからの更新drillを報告する。ただし修正前の2.0.16-next/2.0.17-nextは自力で修正版をdownloadできず、一度手動導入が必要という配布制約も記す。固定ソースに修正があることは、その旧binaryの自己修復能力を意味しない。今回はinstallerを取得・実行していない。

### 回復経路に残る公開報告

[Issue #1352](https://github.com/anywhere-labs/dsh-desktop/issues/1352)はrenderer recovery後のshowイベントでcontent webContentsが欠落し主processが例外終了する報告。[PR #1360](https://github.com/anywhere-labs/dsh-desktop/pull/1360)はopenで、固定masterのrevealはdisposed/window/minimizedを確認した後、content.webContentsを直接読む。したがって「renderer破棄を全部安全に扱う修正版」とは記せない。報告条件の独立再現もしていない。disposeはwindow listenerを解除するが、dispose到達前のwindow/content間の生存期間差が検査点になる。[reveal](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-plugin-desktop/src/compatibility-shell.ts#L146)、[window listener解除](https://github.com/anywhere-labs/dsh-desktop/blob/6bc000ba031700b2252cdb73c2b4f1d288a97c56/dsh-plugin-desktop/src/compatibility-shell.ts#L184)。

[Issue #1347](https://github.com/anywhere-labs/dsh-desktop/issues/1347)はplugin分割scriptと常駐SSEの接続競合により、rendererのhealthy POSTが204でもnative mount待ちが解消せずtimeoutになるという利用者の計測・仮説。取得時open。healthy受領、native mounted、app readyが違うbarrierであることを調べる入口になるが、この仮説を今回確認したroot causeとはしない。

**狙った検査:** update transportは302→HTTPS storage、HTTPへの降格、hop超過、途中abort、selector header不送信をassertする。renderer回復はcontentを除去した状態でrestore/showを発火し、主process生存と復帰導線を確認する。大量Client chunkとSSEを共存させ、各boot barrierのtimestampを分ける。いずれも今回未実行。

## 小さい表示拡張との対比

### dsh-context: 観測UIにもprojectionとcold readの所有がある

`dsh-context 0.69.1`はHost projectionとWeb Client。required `sessionProjections`の下でdurable logをfoldし、重いdetailは閲覧Clientごとのon-demand channelへ分ける。Host全体のFIFO cold-read gateをdetail/fleet/warm-upが共有する。小さい表示UIでも大会話を一括物化しない予算が必要になる。[Issue #121](https://github.com/bowenliang123/dsh-context/issues/121)のメモリー報告の数値を今回の測定結果へ転用しない。[projection・cold readの構成](https://github.com/bowenliang123/dsh-context/blob/a5438855d7bbc1ab9f1c36b20dbc45564716b052/src/host/index.ts#L1)、[manifest](https://github.com/bowenliang123/dsh-context/blob/a5438855d7bbc1ab9f1c36b20dbc45564716b052/package.json#L1)。

Clientはlocale namespaceを`dsh-context`とし、tab/sidebar/modal/insightsをslotへ登録しeffectで撤回する。二重mountはsame-idだけでは防げず、priorityが違えばledgerに共存するため、jump slotの既存markerを確認する。settingsはconfigFormsがservedされる範囲でattachする。[namespace・二重mount・解除](https://github.com/bowenliang123/dsh-context/blob/a5438855d7bbc1ab9f1c36b20dbc45564716b052/src/client/index.ts#L46)。

[PR #139](https://github.com/bowenliang123/dsh-context/pull/139)はclosed・未merge。作者はwire圧縮を別値で示す変更と2,256 tests等を報告したが、[maintainerの反証](https://github.com/bowenliang123/dsh-context/pull/139#issuecomment-6116772902)では実projectionのsample基準がrequestごとに更新され、提案の閾値がそのscenarioで発火しないと説明する。fixed mainにもwireGapはない。「検査数が多い」「coverageが高い」ことより、現実の状態遷移から生成したfixtureが重要な例である。観測したlocal breakdown、provider sample、projection、請求値を同じcontext sizeへ混ぜない。

### Whale Widget: namespaceがあってもpage lifetimeが残る

`dsh-whale-widget 0.4.2`はbundle patchとHost JSで、typed dsh.client宣言を持たずtapIndexやDesktop structured injectionからscriptを入れる。scriptはwindow markerで一回起動し、composer DOMを探してからbodyへ表示を足す。React Portalの画面を誤検出してDOMを変更しないための防御だが、composer selector変更への追従が必要。Host routeのeffect解除とブラウザーscriptのpage lifetimeは別である。[manifest](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/blob/5247dd6813d6e4430728f39ccc63d43cda046022/package.json#L1)、[script注入とHost解除](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/blob/5247dd6813d6e4430728f39ccc63d43cda046022/lib/index.js#L4903)、[window markerとcomposer検出](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/blob/5247dd6813d6e4430728f39ccc63d43cda046022/assets/whale-widget.js#L1)。

初期observerとfallback pollはcomposer発見時に解除されるが、発見しないpageでは無期限に残る。body node registry、styleのdata-owner、composition中のDOM mutation延期など、別pluginやIMEとの干渉に対応する処理が多い。UIの面積が小さいことはeffectの数が少ない証拠にならない。[observer・poll lifetime](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/blob/5247dd6813d6e4430728f39ccc63d43cda046022/assets/whale-widget.js#L55)、[style/body nodeの所有](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/blob/5247dd6813d6e4430728f39ccc63d43cda046022/assets/whale-widget.js#L1278)。

[Issue #232](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/issues/232)の壊れたledgerで読込・保存が永久失敗する報告に対し、固定版はbackup＋fresh ledger、temp＋renameのwriteを持つ。ただしread I/O failureもbackup/freshへ進み、先頭candidateが壊れた場合に良い第二candidateへ必ずfallbackする実装ではない。報告者の提案と実際の修正を同一にしない。backup失敗時やEACCES/EISDIRの扱いは別に検査する必要がある。[ledger回復・write](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/blob/5247dd6813d6e4430728f39ccc63d43cda046022/lib/index.js#L1383)。

### Deep Whale: skin切替にも共有bodyの所有権がある

`Small-tailqwq/dsh-deep-whale`は単一packageではなく、manager 0.1.6、orca-link/maid-atelier 0.1.7とassetsの構成。`skin.json`はid/package/bodyAttr/compatibility/wiringを宣言する。repository全体のstarsを各skinの導入数にしない。[skin宣言](https://github.com/Small-tailqwq/dsh-deep-whale/blob/bcb12f15a19590e6d0e9890bd498590fae3c58df/orca-link/skin.json#L1)、[manager package](https://github.com/Small-tailqwq/dsh-deep-whale/blob/bcb12f15a19590e6d0e9890bd498590fae3c58df/skin-manager/package.json#L1)、[maid package](https://github.com/Small-tailqwq/dsh-deep-whale/blob/bcb12f15a19590e6d0e9890bd498590fae3c58df/maid-atelier/package.json#L1)。

managerはsettings slotとregistryをeffectで登録・disposeする。maidはbody attributeとCSS variableの変更前値、owned node、observer、RAF/timer、resize listenerを保存しdisposerで戻す。名前空間は`data-dsh-maid-atelier`、`--maid-*`等。別のcustomization helperは値が自分の最後のwriteと一致する場合だけ元値へ戻す。この所有確認は、後から別pluginが変更した値を古いdisposerで巻き戻さないための参考になる。[manager登録と解除](https://github.com/Small-tailqwq/dsh-deep-whale/blob/bcb12f15a19590e6d0e9890bd498590fae3c58df/skin-manager/src/client/index.ts#L19)、[skin全体の撤回](https://github.com/Small-tailqwq/dsh-deep-whale/blob/bcb12f15a19590e6d0e9890bd498590fae3c58df/maid-atelier/src/client/index.ts#L563)、[CSS writeの所有確認](https://github.com/Small-tailqwq/dsh-deep-whale/blob/bcb12f15a19590e6d0e9890bd498590fae3c58df/maid-atelier/src/client/customization.ts#L35)。

skinは既存DOMのcarrierやbodyへ依存するため、native/Web、Desktop shell、layout変更への追従が必要。解除コードの存在だけで、すべての共有body variableにownership checkがあるとは言えない。skin A→B→A、Aの遅いdisposer実行、IME composition、resize連打、Host UI更新後を確認する。この比較枠ではIssue履歴やassetsの利用許諾全体、配布tarballは監査していない。

## 実例のフローを自作pluginへ適用する

| 利用者の操作 | 状態を持つ場所 | 成功の証拠 | 失敗時に維持すること |
| --- | --- | --- | --- |
| plugin更新 → page再接続 | Host operation/job、disk package、Client queue | 実際の導入版とactivation結果 | operation消失を成功にせず再照合 |
| dirty fileをrename → 同navigation再配信 | file、session別tab record、editor buffer、revision | 新pathとbufferが再配信後も維持 | 旧path再作成を避け、草稿を保持 |
| terminal tabを隠す → 戻る | Host process、contentId、DOM attachment | 既存process採用、snapshot後の順序付きoutput | detachとcloseを区別 |
| TUI内核切替 → 最初のframe | 親stdin、子stdin、attemptId、ACK | 同attemptのfirst-frameと入力独占 | old parentがreplyを盗まない |
| Desktop更新 → restart | release metadata、artifact、installer、edition/profile | download verifierと起動identity一致 | 旧updaterで取得不能なら手動経路 |
| skin切替 | body attribute/CSS、DOM node、observer/RAF | 自分の変更だけ撤回 | 他pluginの後続writeを戻さない |

小さい自作pluginへ採用するのは、必要な境界だけでよい。更新ボタンなら導入経路とoperation結果照合、slot追加ならnamespaceとdisposer、file viewerならpreviewとfile権限を確認する。巨大なmarket engine、TUI updater、Desktop recoveryを一つのボタンのために複製する必要はない。

採用する設計は、登録時descriptorと同一性を確認する解除、一つの設定writer、失敗を回復したqueue tail、Host提供profile/terminalの利用、実navigation revisionでの更新、spawn/error/closeの終端化、明示した版・capability・artifactの照合である。どれもサービス名やhelper名から保証を推測せず、実呼出元まで確認する。

注意する設計は、process内Mapを永続履歴と説明すること、closed PRをmergeと説明すること、GitHubソースと同番号の配布物を同一視すること、DOM markerだけで全二重mountを防げると考えること、reportされた原因を再現済みと扱うこと。今回の例では#139の反証、#917の置換、#849の追補、#1343の旧binary制約が、どこまで直ったかを決める。

## 確認範囲

確認したのは8 repositoryの固定checkout、package/bundle/Client宣言、上記主要呼出経路、選択したIssue/PR本文とcomment、merge metadataである。主要5件はいずれも具体的な修正履歴を照合した。全route、全family、全platform、全subprocess tree、全timer、全CSS selector、npm tarballやinstallerを網羅した検査ではない。

根拠snapshotのmanifestは`ui-updates/manifest.json`で、repo・default branch・SHA・package版・隔離directoryを記録した。Issue/PR/comment JSONも同じsnapshotに保存している。ソース引用リンクのfileと行番号は固定checkoutで存在確認した。公開コメントの動作報告を引用しても、今回それを再実行した結果としては扱わない。
