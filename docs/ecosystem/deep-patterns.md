# 自作pluginへ持ち帰る契約と、先に狙う再現試験

外部実装から持ち帰る単位は、小さい契約と、その契約が破れる操作順です。Pi、日本語パック、PWA、Search、Remora、Glass UI、CFを同じ拡張として扱わず、資格情報、model入力、UI、外部process、配布のどこを変更するかを先に決めます。この章は[Provider/agent](deep-providers-agents.md)、[ブラウザー/記憶](deep-browser-memory.md)、[UI/更新](deep-ui-updates.md)、[Desktop/壁紙](deep-desktop-theme.md)、[アクセス/catalog](deep-access-catalogs.md)、[画像/研究preset](deep-vision-research.md)の6分析章を整理します。自作7件へ追加実装した結果や、全組合せの共存試験結果ではありません。

自作の現在の公開版と導入条件は[公開版一覧](../own-plugins.md)、既に実施した更新回帰は[更新実装](../update-implementation.md)を参照します。以下の試験は追加検査の提案で、今回実行していません。

## 1. 更新完了は、導入版と実行版を照合して決める

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| request IDを送信前に決め、profile identityと一緒に照合する。Pi/Japanese/PWA/Search/Remora/Glass/CF共通 | [自作更新の応答喪失・profile切替](../update-implementation.md)、[IMのprofile別intentと導入後再照合](deep-providers-agents.md#im-外部sender管理browserdsh-permissionを三つに分ける) | Marketのoperation IDやweb-allのjob IDはHost process内の記録で、再起動後の永続receiptではない | 開始応答を捨てる→同IDで再照合。URLを別profileへつなぎ直す→旧要求を届ける。新候補が出ても未解決IDを上書きしない |
| candidate、installed、running、saved ON/OFFを別に持つ。更新後はactivation結果に応じrefresh/restartを案内する | [Marketのoperation storeとClient queue](deep-ui-updates.md#dsh-market-更新を一つのボタンから一つの操作へ分解する)、[OFMのdisk/runtime復帰](deep-providers-agents.md#更新はdisk復帰とruntime復帰を別に記録する) | OFMのLoader内部cache purge、registry削除、新fiber関連付けは大きい所有範囲。一般更新ボタンへコピーしない | manager成功でもmanifest不一致、diskだけ復旧、runtimeだけ復旧、新fiber起動失敗、Host再起動でoperation消失を別々に与える |

更新check成功やHTTP 202は仕事の受付です。installerを開いたことも、更新後appが起動した証拠とは違います。CFのplugin更新にcloudflaredやTunnel/DNS/Accessの変更を混ぜず、Piのplugin更新とPi SDKの更新を別にします。

## 2. profileとaccountは、表示名ではなく実行する所有者に結び付ける

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| accountを含むcapability-bearing routeをprepare時に固定し、stream直前にもpolicyを確認する。Pi/Search | [SubscriptionsのunionとprepareCall](deep-providers-agents.md#一覧のunionは生成可能accountの証明ではない)、[Fast/tier/effortの分離](deep-providers-agents.md#fasttiereffortは同じ能力ではない) | 一覧のunionで同IDが一つに見えても、全accountが同plan/能力とは限らない。別名やclient_versionをentitlementへ変換しない | plan違いの二accountが同model IDを返す→一方OFF→prepared streamを開始。alias変更、独立account ID、fallback後effortも照合 |
| model modalityはroute所有者が実endpoint能力を確認して宣言する。Pi/Search | [Vision Router #671/#672のmetadata修正](deep-vision-research.md#671-安全境界を迂回せず修正した説明を届ける) | Host metadataがtext-onlyのrouteへ、adapter-firstという説明だけで画像を送らない。local画像解析後の主chat modelも送信先へ含める | 同endpointでtext-only/image宣言を切替、native adapter/HTTP fallback/local-onlyを比較し、どこへpixelsとdescriptionが出るか確認 |
| profile path、home、package-manager、manifest解決をlauncherの実factsから得る。更新7件、Remora/CFの外部process | [anywhere-labsのprofile identity](deep-ui-updates.md#desktop-profileの更新renderer回復製品更新を分ける)、[DataElementのdesired投影](deep-desktop-theme.md#dataelementdsh-desktop-generationのdesiredを次回起動へ投影する) | `link:`をすべて開発pathと見なしたり、default profileへpackageを足しただけでgenerationが替わると考えない | 同packageがprofile・app overlay・generationに三copyある状態で、互換checkとLoaderが同copyを選ぶことをassert |

OpenVikingのpeer、EverOSのcwd hash、MemOSのpreset/agentKind namespaceも同じscopeではありません。[記憶の比較](deep-browser-memory.md)で、project・profile・Session・accountのどれが保存先と検索先を決めるかを読む必要があります。

## 3. logoutとcancelは、遅い成功が状態を復活させないところまで設計する

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| login/import/cancel/logoutでclaim generationを更新し、code交換完了時に所有を再確認する。Pi、Remora enrollment | [Subscriptionsのcallback後claim](deep-providers-agents.md#login取消はcallback-serverの停止だけでは終わらない) | callback serverのcloseだけでは交換中の成功を止めない。OAuth claimがrefresh成功writeにも効くとは推測しない | callback到着→exchange保留→logout→exchange解放。加えてrefresh成功保留→logout/new login→saveを解放 |
| callerの待機取消と、共有仕事の取消を区別する。Search/Piのdiscovery、Glassのasset準備 | [Modlensの共有解析cacheと取消](deep-browser-memory.md#modlens-durable-imageとwire-evidenceの内容が一致するとは限らない)、[Subscriptionsのinflight catalog](deep-providers-agents.md) | 別callerのために残す解析は、取消後もprocess・通信・費用を持ち得る。raceでcallerが終わってもCPU処理が終わる保証ではない | 二callerが同じ仕事を共有→Aだけcancel→Bは成功。最後のcallerもcancelした時の停止方針とdispose後の結果writeを確認 |

解除時に値を消すだけでなく、解除前に開始した非同期結果がどのgenerationへ書けるかを決めます。

## 4. modelへ渡した変換結果も、後から再構成できる保存単位にする

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| 元入力ref、変換route/version、変換結果、実注入文を結ぶ。Pi/Searchのwire変換、Remora外部入力 | [Modlensのdurable imageとwire evidence](deep-browser-memory.md#modlens-durable-imageとwire-evidenceの内容が一致するとは限らない)、[OFM token saverとtool pairing](deep-providers-agents.md#生成が変更する範囲をpayloadごとに見る) | 元画像/URLを保存しても、cache退去後の再解析は当時のbyteと同じとは限らない。性能改善のつもりでtoken saverやcontext gateを暗黙追加しない | cold/warm/restart後のprovider payloadを比較。URL本文とgrep、画像入りtool-result、失敗文変動、provider変更をfixture化 |
| evidence keyをSession/attachment/prompt/runtime/contractへ結び、logical IDと保存path IDを分ける。Search/Pi/Remora audit | [Toolkit durable sidecar](deep-vision-research.md#vision-toolkit-evidenceを保存する単位がsessionpromptruntimeまで及ぶ)、[ClearAI material digest/path](deep-vision-research.md#clearai検索toolの追加ではなく結論を許すpreset) | sidecar失敗やprune時は再解析し得る。評価者modelの承認は外部事実の確認ではない。Searchのquery/provider/取得日時/引用範囲/hashを対象へ含める | credential/runtime更新後のcache miss、sidecar破損、Sessionなしcall、criteria変更、Windowsのlogical ID文字をfixture化 |
| 注入messageのID・producer・Session/turn/stepを保存契約に合わせる。Search/Remora | [Anchoredのrestart後hint ID](deep-providers-agents.md#修正事例-76と78は似た履歴障害でも所有者が違う)、[MemOS/EverOSのsource世代](deep-browser-memory.md) | UUID追加は新規注入の衝突耐性で、既存の壊れたSession logのmigrationではない。generic plugin sourceを現行producer契約へ適合済みとしない | 注入→保存→Host restart→resume→再注入。compaction/fork後もIDの意味とproducer所有を照合し、過去fixtureを読む |

日本語パックはUI辞書・明示言語設定の仕事です。modelのpersona、context suppression、graded loopを追加する理由にはなりません。外部presetの効果検証とUI翻訳の確認は分けます。

## 5. 登録成功から、実scopeのschemaとdispatchまで検査する

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| model-visible一覧と実呼出しを同じagent scopeで確認する。Search追加tool、Pi/provider、Remora操作 | [modlens #34のscoped shadow](../workflow/ecosystem-cases.md#6-modlens-34-register成功でもmodelから見えなかった)、[Routingのchild Sessionとrestrict](deep-providers-agents.md#段階ごとのツール許可リストとprompt側の子session除外が一致しない) | global register/get成功やLoader Runningは、own-scopeで見える証明ではない。BrowserSkillのprocess lifetime lazy公開はSession grantではない | 同名global/scoped toolを置く→実agentのschemaとdispatchを読む。親子Sessionでstage/restrictを交差させる |
| optional serviceは小さい機能だけ降格し、必須service不足はHost activationとして診断する。Japanese/PWA/GlassのUI、Piのprovider | [Sidebar terminalのoptional検出とwebRuntime pending](deep-ui-updates.md#better-sidebar-tabの住所内容terminal-processを別々に所有する)、[OFM匿名車線とchannel-pack fiber](deep-providers-agents.md#見えているpackageと実際に動くmoduleを分ける) | optional chainでCordis proxyの未宣言service読出しが安全になるとは限らない。manifestのpeerだけではinject充足を証明しない | service無し、遅れて出現、出現後消滅、rename版を用意。UIが残るがHost route未登録の405をpermission問題へ誤分類しない |

拡張SDKを使える操作はその契約へ委譲します。内部loadCache、registry、profile file、宿主install fileの上書きを使うと、上流の内部構造と復旧経路まで自分の保守対象になります。

## 6. 一つのwriterへ直列化しても、複数processのtransactionにはならない

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| read-modify-writeの全writerをpath別queueへ入れ、失敗tailを回復する。Pi/Search catalog、Remora audit、各設定 | [Subscriptions #129](deep-providers-agents.md#修正事例-129はrenameとread-modify-writeを分けた)、[Market共有mutation chain](deep-ui-updates.md#設定保存と更新の競合)、[web-all CLI/direct writeの共有queue](deep-ui-updates.md#plugin-managerの更新と永続化) | temp＋renameはpartial file対策で、lost updateの排他ではない。process内queueは別Host/CLIを排除しない。fire-and-forget成功はdisk保存成功ではない | provider-level＋account-level同path saveを並列化。rename EPERM retryとRMW競合を分ける。別process writer、保存失敗後の次操作も試す |
| derived projectionは自分が所有するfield/entryだけを書き換える。PWA/Japanese/Glass config、plugin更新 | [DataElement #665のoptional bundle保持](deep-desktop-theme.md#実修正-自分が所有しないoptional-bundleをprojectionで消す)、[Market #841のpayload/loader ID分離](deep-ui-updates.md#issueから実修正-loader行とpresetの中身を取り違える) | 列挙したidがすべてloader所有とは限らない。preset payload、group child、利用者のbare overrideを同じ集合へ入れない | 任意利用者field、同梱optional bundle、同名payload IDを残した再投影。config先頭やキー順を変え、実Loaderと比較 |

破損読込の方針もwriter契約とは別です。Whale Widgetはbackup/fresh ledgerを持ちますが、EACCESや良い第二candidateへのfallbackまで同じ回復とは言えません。

## 7. 接続を認証しても、sender・device・workspaceの操作権限は残る

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| bot/connector credential、remote sender/device、Session操作、tool approvalを別に評価する。Remora/CF | [IMのnew botとmigration policy](deep-providers-agents.md#認証済みbotから届いたmessageも操作権限は別)、[BrowserSkillのlogin済みbrowserと本人確認](deep-browser-memory.md#browserskill-login済みbrowserへ届くまでに三つの所有者を通る) | bot接続済みを全sender許可にしない。browser Host/Origin fenceをcredential認証と呼ばない。CFのedge admissionをDSH内操作権限の代わりにしない | unknown sender/device、direct/group/command、既存policy migration、別workspaceへのswitch、permission質問のowner違いを組み合わせる |
| remote proxyのPIN認証と、Hostに見せるauthority変換を明示する。CF/Remoraとの比較 | [Pocket PIN→loopback authority→launch token](deep-access-catalogs.md#二段階loginとfull-web権限) | PINでfull Webへ届く構成はRemoraのdevice/Session scopeと異なる。cf-connecting-ipの信頼は実Cloudflare入口に限る | 直LAN/Cloudflare/独自proxy、HTTP/WSの両admission、Host override、cookie rotation、未知domainを組み合わせる |
| 外部message ID、DSH Session、RPC/turn ID、送信receipt、audit flushを対応させる。Remora、Searchの外部request | [IMのinteraction先行とturn追跡](deep-providers-agents.md#sessionとmessageのidを結び再接続で再promptしない)、[Open Designのrequest/session/result](deep-browser-memory.md#open-design-接続テストと実行結果の完全性を分ける) | 1000件dedupは無期限exactly-onceではない。送信成功とmarkSeen保存の間、RPC acceptedと外部配信の間にcrash窓がある | external send成功直後に保存を止める→restart。interaction reconnect中cancel。別turn event、resume ID不一致、exit0/result無しを注入 |

この層には「解除すれば安全」以外に、「既に受け付けた仕事をどこまで完了するか」「誰が結果を受け取るか」という契約があります。

## 8. UIのdetach、process停止、engine破棄を別の解除にする

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| 取得した資源だけを停止し、借りた資源は返す。Remora/CF process、Glass media、PWA window | [Sidebar terminalのdetach/close](deep-ui-updates.md#fileとterminalの権限)、[EverOS既存serverのstop除外](deep-browser-memory.md#everos-本体から移転したleafとcaptureflushの分離)、[Tauri owned tree停止](deep-desktop-theme.md#起動更新終了のmutex) | DOM unmountはPTY終了ではない。healthが200でもserverを自分が起動した証明ではない。port競合だけでunknown processをkillしない | preexisting server/process、同contentIdでterminal復帰、tab閉鎖と隠す操作、old PID exit後のnew process、unknown port ownerを用意 |
| listener/observer/timer/RAF/style/media準備をfiberとgenerationへ結ぶ。Japanese/PWA/Glass | [Deep Whaleのownership付き撤回](deep-ui-updates.md#deep-whale-skin切替にも共有bodyの所有権がある)、[Wallpaper Engine prepared iframe/decoder解除](deep-desktop-theme.md#解除の具体経路) | iframe removeだけで全WebGL処理が解放されるとは推測しない。永久stdin移譲のNode内部APIを普通のUI cleanupへコピーしない | 準備中にOFF→遅い完了→ON、連続skin切替、未接続iframe、warm video、old disposer遅延。資源数と後続callbackを観測 |

BrowserSkillのexitとstdout close、TUIのremoveListenerとnative read停止は、表面上の終了後に残る別資源を示します。単純な「disposerがある」レビューではここが抜けます。

## 9. CSS namespaceに加えて、共有tokenとnavigation revisionの所有を決める

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| namespace、slot ID、body marker、CSS variableを一覧にし、old disposerが他pluginの後続writeを戻さない。Japanese/PWA/Glass | [Sidebar descriptor同一性の解除](deep-ui-updates.md#拡張apiと解除)、[Deep Whale CSS所有確認](deep-ui-updates.md#deep-whale-skin切替にも共有bodyの所有権がある) | same slot idでもpriority違いで二重表示するregistryがある。windowの一回markerはHMR全解除を証明しない | standalone＋aggregate二重mount、A→B→AとAの遅いdisposer、localStorage namespaceを二profileで使う |
| tokenの半透明化とblur carrier、Portal座標、IME、mobile/bfcacheを別に見る。Glass/PWA/Japanese font | [Wallpaper Engine shared alias tokenと#200/#204](deep-desktop-theme.md#issue対応を追ってもdefaultに残る設計がある)、[Whale Widget composer/IME依存](deep-ui-updates.md#whale-widget-namespaceがあってもpage-lifetimeが残る) | wallpaper OFFがglass OFFとは限らない。skin-center markerの一方向yieldを任意Glass pluginへ保証しない | 第三者panelがtokenだけを読む状態、fixed overlay内のbackdrop-filter、IME composition中body mutation、767/768px、pageshow復帰 |
| 内容の改名と真のnavigationをrevisionで区別する。PWAの再描画、Glassの再mount、file viewer | [Sidebar renameと同revision再配信](deep-ui-updates.md#issueの追加掘り下げ-rename後の再配信で旧pathへ戻る) | pathを更新したunitが通っても、次renderのhost再配信が旧pathへ戻すことがある | dirty buffer→rename→同revision再配信→保存、新revision navigation、背景Session、custom titleを同じ操作列でassert |

namespaceは衝突の範囲を減らしますが、共有alias tokenとhost navigationは名前を独自化しても残る契約です。

## 10. 有限retryとready barrierを、成功の所有者に合わせる

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| permanent expiry、transient transport、quota、protocol拒否、cancelを別に分類し、retry予算をrestartで戻さない。Search/Pi/Remora/CF | [IM #352のTTL/20回budget](deep-providers-agents.md#修正事例-352は再起動しても復活する永続retry)、[Subscriptions pool exhaustion](deep-providers-agents.md#修正事例-129はrenameとread-modify-writeを分けた) | TRANSPORT失敗をRATE_LIMITへ潰すと利用者がquota切れと誤診する。新規write OFFでも既存pending drainを止める契約とは限らない | expiry一回→原interval後→restartで再送無し。最大試行、future clock、policy変更、pending OFF、retry timerで最新entry再読込 |
| spawn、port、HTTP、Client module、native mount、first frameを別barrierにする。PWA/Glassのboot、Remora/CFのsidecar | [TauriのHTTP/module readiness](deep-desktop-theme.md#readinessの実修正-loopbackへbindできてもwildcard-listenerは生きている)、[Desktop healthy POSTとnative mount](deep-ui-updates.md#回復経路に残る公開報告)、[TUI attempt ACK](deep-ui-updates.md#queryrestartackの三つの状態) | 起動timeoutを増やすだけではmissing serviceやwildcard誤判定を直せない。並列probeの順序変化を進捗にしない | errorだけのspawn、exit後pipe保持、0.0.0.0 bind、healthy204/native未mount、同failure順序の揺れ、old attempt ACKを注入 |

回復が必要な状態を成功へ丸めるより、どのbarrierまで到達したかを短い診断へ出す方が、次の検査を小さくできます。

## 11. source、提案、配布物、利用者の確認を別の証拠として残す

| 契約・適用先 | 実経路の根拠 | そのまま移さない条件 | 狙う再現試験 |
| --- | --- | --- | --- |
| package名・版・entry・patch・Client生成物・peer・DSH leafを同じ固定artifactで照合する。更新7件、catalog連携 | [EverOS leaf移転とOpenViking shared生成copy](deep-browser-memory.md)、[web-all同じ0.4.6のdev修正](deep-ui-updates.md#issueから実修正-spawn失敗はclose待ちだけでは終わらない)、[DataElement内部版/製品版](deep-desktop-theme.md#調査境界) | repo rootがapp、Skill、MCP、集約bundleならnpm packageとは違う。same versionでもdefault/source/tarballのbytesは同じとは限らない | tgzを展開してidentity・公開entry・patch対象・生成Clientを確認。workspace dependency、isolated pnpm、明示Git tag、古いmirror latestを分ける |
| catalog metadata、配布hash、runtime判定、検証時刻/principalを分ける。Pi/Searchの外部catalog、導入候補 | [Radarの歴史runtime判定と生成CI](deep-access-catalogs.md#radar-歴史runtime判定の集約と公開証拠の欠けを残す)、[Shopのexact review pinとcatalog破損](deep-access-catalogs.md#reviewed-identityとcontent-hashは異なる信頼の層)、[15 tarballの独立検査](deep-package-checks.md) | generated_atは各pluginの試験時刻ではない。bot merge guardはvalidatorのprincipal/実行証跡ではない。pointer/data hash一致は固定署名鍵による発行者認証ではない | pass/fail conflictをpendingへ保つ、same-name fork/commit/rollback版、stale pointer、壊れたhash、欠落runner provenance、npm artifactとsource差を確認 |
| closed、merged、作者のtest報告、CI、publish、利用者追認、今回実行を別に書く | [Routing #117/#120 closed未merge](deep-providers-agents.md#段階ごとのツール許可リストとprompt側の子session除外が一致しない)、[context #139反証](deep-ui-updates.md#dsh-context-観測uiにもprojectionとcold-readの所有がある)、[Sidebar #917置換](deep-ui-updates.md#issueの追加掘り下げ-rename後の再配信で旧pathへ戻る) | test数/coverage/closeだけで原因や回復範囲を確定しない。提案branchの実機成功をfixed mainの結果へ移さない | 主張した因果を旧版・修正版とnegative controlで比較。実状態遷移からfixtureを作り、反証された前提を残す |

自作の検証記録も、どの版・profile・artifactを対象にしたかを残します。公開Releaseやinstallerがあることは、全利用者が取得できる証拠ではありません。[Next updaterの旧binary制約](deep-ui-updates.md#issueから実修正-release-serviceの302を追えないupdater)では、取得経路そのものを直すため一度手動導入が必要でした。

## 必要な観点だけを選ぶ

| 自作plugin | 優先して読む契約 | 別要求として扱う変更 |
| --- | --- | --- |
| Pi | 1/2/3/6/10/11: account固定、遅いcredential成功、catalog保存、更新照合 | context gate、token saver、agent persona変更 |
| Japanese | 1/5/8/9/11: locale登録、明示設定、font/CSS解除、Client生成物 | model応答言語やpromptの変更 |
| PWA | 1/5/8/9/10/11: scope/identity、reload/bfcache、mobile DOM、cache版ずれ | app installer・Host processの所有 |
| Search | 2/3/4/5/6/10: provider policy、wire/結果再現、tool scope、保存とHTTP分類 | 自動routing/presetの段階制限 |
| Remora | 1/2/3/4/7/8/10: device/Session/RPC対応、flush、取消、process所有 | bot接続成功を全sender権限へ広げる変更 |
| Glass | 1/3/8/9/10: 保存待ち編集、prepared media、CSS/token、first frame | shared aliasを第三者panelへ無条件適用する変更 |
| CF | 1/2/7/8/10/11: plugin/runtime/edge設定の分離、owned sidecar、接続診断 | plugin更新にTunnel/DNS/Accessの再構成を混ぜる変更 |

各番号は検査項目の優先候補です。変更していないproviderやOSを一律に再検査する指示ではありません。実際に触る経路と未解決の条件に合わせて、狙ったfixtureと必要な実環境検査を選びます。
