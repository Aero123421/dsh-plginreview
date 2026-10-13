# Provider・routing・agent・IM の実行境界を追う

既存の[モデル・認証章](providers-and-memory.md)と[ブラウザー・routing章](browser-and-routing.md)から、失敗の順序、状態の所有者、配布済み修正を掘り下げます。2026-10-13に公開default branchを取得し、APIで取得したSHAとcheckoutのHEADを照合しました。人気トピックは候補選定の入口です。starsからDSH利用者数、接続成功率、品質は判断しません。トピック検索は19,027件中stars順1,000件の検索上限があり、全件網羅ではありません。

実認証、課金API、IM送信、install/build script、クラウド作成は実行していません。ソースの経路、公開Issue/PR、限定したkeyless helper実行を分けて記載します。Issueの症状や作者の実機結果を、今回再現した結果には置き換えません。

## 固定した入口と責務

| 対象・manifest版 | 固定SHA | Host / Client / 配布入口 | modelへの変更 |
| --- | --- | --- | --- |
| Our Free Model 2.1.0 | `ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68` | `index.js` / `client.js`、bundle patch、Git導入と署名manifestによる独自更新。private package | wire変換、tool pairing修復、token saver、継続回復、comboによるmodel切替 |
| Subscriptions 0.9.9 | `9930c5ee5e3fa239db9031f47a0f6f30f7ffc443` | `lib/index.js` / `lib/client/index.js`、bundle patch、npm/Git | provider wireへの変換、account pool、画像offload。通常のsystemを受け取り、空ならCodex fallback指示 |
| Routing Suite injector 0.3.3 / preset 0.3.0 / graded 0.0.1-rc1 | `195273352f23bff7f9023ebe2ec0cdbdf9c98f10` | root bundleはinjectorのみ。preset別導入とruntime注入・profile登録・reload | persona、段階別tools、追加message、graded承認protocol |
| Anchored Standard 0.1.0 | `dda23ef119e3715f417d73f72eca407732846d1a` | privateなpreset source集。rootに`dsh.bundle`/exportsなし | complete persona、context suppression、tool catalog縮小、compaction後の再bootstrap、別think route |
| AgentTeams 0.1.23 | `1094b84add6f2fb19edf659367fe2fd5f7f14154` | `lib/index.js` / `lib/client.js`、bundle patch、npm/Git | captain/member persona、coordination tools、durable task/mailbox、子model選択 |
| IM 4.39.0 | `f6a9dd0abbeae605e459a660a9922c9a703e6aa0` | `lib/index.js` / `lib/client.js`、bundle patch、npm。Web profile対応宣言 | IM由来context、Session prompt/steer、permission質問の橋渡し |

入口の根拠: [OFM manifest](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/package.json#L1)、[Subscriptions manifest](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/package.json#L1)、[Routing root manifest](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/package.json#L1)、[Anchored manifest](https://github.com/xiaobright/dsh-anchored-standard/blob/dda23ef119e3715f417d73f72eca407732846d1a/package.json#L1)、[AgentTeams manifest](https://github.com/NanmiCoder/dsh-agent-teams/blob/1094b84add6f2fb19edf659367fe2fd5f7f14154/package.json#L1)、[IM manifest](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/package.json#L1)。

同じrepoの一番新しいmanifest版と、利用者が取得したtag/tarball/commitは別です。Routingのroot peerには裸名`cordis`/`schemastery`、injector子manifestにはscoped名があり、rootの広い`>=0.0.1-rc <2`条件は内部Loader互換を証明しません。SubscriptionsとAgentTeamsの宣言にはDSH `0.2.1-alpha.2`が含まれず、IMは`0.2.0-rc.2`とWeb profileの対応宣言です。今回のソース読解を現行DSHへの導入合格とは扱いません。

## Subscriptions: catalogの選択と生成accountを同じ時点に固定する

### login取消はcallback serverの停止だけでは終わらない

`/subscriptions-auth` RPC → controllerの`login` → provider別OAuth/device flow → code交換 → `saveAccountSession` → `authChanged` → catalog/pool invalidation、という経路です。OAuthはPKCE/stateを作り、loopback複数familyの同じportを確保し、settleでtimerとserverを閉じます。不一致stateのredirectは正常attemptを終了させず400を返します。

callbackがcodeを渡した直後には、flow managerのpendingからattemptが消えます。しかしtoken交換はまだ完了していません。controllerはproviderごとのclaim番号を持ち、login/import/cancel/logoutで番号を進めます。古い番号の交換完了は保存しません。`cancel()`がpending serverを止めるだけだったら防げない、取消→遅い交換完了→credential復活の順序を扱っています。`logout`はローカルaccount削除と通知であり、外部providerのtoken失効APIを呼んだ保証ではありません。

根拠: [callback所有とsettle](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/auth/oauth-flow.ts#L184)、[claim番号](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/index.ts#L375)、[cancel/logout](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/index.ts#L656)、[保存直列化](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/auth/store.ts#L445)。

auth storeは`0600`のtemporary file + renameとpath別Promise chainです。旧single-accountを移行し、identityがない旧credentialのrefresh-token hash keyからcanonical identityへのaliasも扱います。これは同じprocessのread-modify-writeを直列化する設計です。OS共通file lock、secret暗号化、複数Host間のtransactionとは同一視しません。

refreshはaccount別TokenManagerのinflightを共有します。永久失効時は保存値を再読込みし、新しいloginのrefresh tokenと違えば新credentialを返して削除しません。成功refreshの`doRefresh`は取得後にsaveへ進むので、**refresh成功がlogout後に戻る順序**について、OAuthのclaimと同じ保証があるとは今回確認できません。ソース上の確認課題であり、実credentialで再現した不具合ではありません。

根拠: [account別managerとalias移動](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/accounts.ts#L197)、[refresh失敗時の再照合と成功write](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/common.ts#L386)。

### 一覧のunionは生成可能accountの証明ではない

model IDはbackendの`slug`を保ち、表示名は別fieldです。account catalogはdefault優先のunionを作り、同じIDは先着metadataを保持、priorityで整列します。一つのaccountが失敗しても残りの一覧は取得できます。異なるplanの能力をIDだけで混ぜないため、生成側には別の固定が必要です。

登録routeは`AccountPreferencesAdapter` → poolまたはaccount fallback → `resolveOwnModel` → `prepareCall`でcapability-bearing accountを保持 → stream直前にそのaccountのpermission/catalogを再確認 → `streamAccountWithReplay`です。独立accountは`~account:<encoded account>:<encoded model>`を使い、canonical round-tripを検証します。rename表示がwire IDを変えません。pool facadeも同じaccount policyを通るため、pickerから外したaccountがexplicit tierの裏から呼ばれる経路を制限しています。

準備後にaccountを除外した場合、別accountへ黙って切り替えず失敗することがコードの意図です。選んだprovider rowをconfigの`providers`から外すことと、`logout`でcredentialを削除することも別です。providerを非登録にしてもauth storeを自動消去する処理にはなっていません。

根拠: [unionとtimeout](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/accounts.ts#L83)、[独立ID](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/account-preferences.ts#L10)、[生成policyとprepareCall](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/account-preferences.ts#L62)、[実登録route](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/index.ts#L803)。

### Fast・tier・effortは同じ能力ではない

| 表示・設定 | ソースが決める値 | 保証しないこと |
| --- | --- | --- |
| Codex Fast | catalogの`service_tiers: priority`またはlegacy `additional_speed_tiers: fast`を確認し、requestへ`service_tier: priority` | 一覧にある全modelのFast利用、価格・plan・実速度 |
| effort | backendのsupported levelsを使い`ultra`を除外。旧保存値`ultra`はwireで`max`へ | Codex CLI側の自動subagent動作の再現 |
| account pool / tier | memberごとのprovider/account/modelとpolicyを解決 | 表示先provider一つだけへの通信、全memberの同じcontext能力 |
| 別名 | provider/modelの表示fieldのみ | backend IDやcredential所有の変更 |

Fast状態はSession別process memoryにあり、再起動でstandardへ戻ります。古いFast選択をcapabilityのないmodelへ送らないgateがあります。catalog取得に使う`client_version` overrideは、account entitlementを増やしません。

根拠: [catalog能力](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/codex.ts#L494)、[effort loweringとrequest body](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/codex.ts#L711)、[Fast状態の寿命](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/index.ts#L794)。

### 修正事例: #129はrenameとread-modify-writeを分けた

[Issue #129](https://github.com/V1ki/dsh-plugin-subscriptions/issues/129)の利用者はWindows、0.9.6、6 accountで60並行saveの一部がEPERM、account section喪失を報告しました。作者はmacOSでも旧版で喪失を再現し、原因所有者を共有`models.json`のwriterへ絞りました。Windowsだけの症状ではありません。

[PR #127](https://github.com/V1ki/dsh-plugin-subscriptions/pull/127)は10-08にpath別queueをmerge。さらに094f2b0でWindows share-modeによるEPERM/EBUSY/EACCESのbounded retryと回帰を追加しました。作者のコメントは新版0 lost/0 failed、[v0.9.9](https://github.com/V1ki/dsh-plugin-subscriptions/releases/tag/v0.9.9)は10-09公開です。今回このTS suiteを実行していません。

現行writerのqueueは失敗Promiseを回復して後続を通し、tailがまだ自分ならMapを削除します。ただしcatalogの保存自体はfire-and-forgetで、失敗するとruntime一覧は使えても次回restartに最後の正常catalogが残らないことがあります。「pickerがすぐ開く」「diskに保存できた」は別の成功です。根拠: [rename retryと更新queue](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/catalog-store.ts#L162)、[catalog saveの非同期境界](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/common.ts#L730)。

[Issue #139](https://github.com/V1ki/dsh-plugin-subscriptions/issues/139)も参考になります。単一memberのTRANSPORT失敗をpool exhaustionが一律RATE_LIMITへ変えていたため、実原因が読めませんでした。作者はfafd737で最後のmember/code/messageとcooldownを分け、0.9.9配布を報告しています。quotaの実測なく「pool exhausted＝使い切った」と診断しない設計をSearch/Piのfallbackにも持ち帰れます。

## Our Free Model: 匿名車線と資格情報を持つchannel-packは別所有者

### 見えているpackageと実際に動くmoduleを分ける

Hostはadapterを登録し、membershipの変化をregistration handleの`replace`で通知します。匿名車線に加えて、`credentials/commands/llm`が揃う別fiberで`vendor/channel-pack/pack.js`をdynamic importします。serviceがないheadless構成ではchannel-packを待つ/失敗することと、匿名車線が残ることが分離されています。

vendored TypeScriptの出所はGitee `dsh-codearts-auth`、吸収commit `345f0a07b22713c0ae189ca7d8b97ec4f64626c6`とNOTICEに記載されています。runtimeはそのsourceを直接読みません。build済み`pack.js`とQoder WASMが実配布物で、今回bundleと全sourceの再build一致までは確認していません。

根拠: [adapter登録とmembership](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/index.js#L434)、[channel-pack fiber](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/index.js#L1020)、[vendor来歴とruntime実体](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/vendor/channel-pack/NOTICE.md#L1)。

CodeArtsの例ではaccount entryはcredentialRefを持ち、secret本体は`ctx.credentials`へ置きます。定時refresh、usage、account RPCが同じrefresh tokenを使うため、ref別SerialQueueを使い、待っている間に他経路が更新していたら保存credentialを再確認します。これを13 channel全部の同じ取消保証と読むことはできません。storeの`state.json`、permanent lock、dead-model、token ledgerは別ファイル/所有者です。ledgerのsource自体がread→merge→renameを複数processのatomic transactionとみなさず、single-process運用の条件を明示しています。

根拠: [CodeArts refreshの並行経路](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/vendor/channel-pack/src/service.ts#L125)、[ref指定refresh](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/vendor/channel-pack/src/service.ts#L291)、[account indexとcredentialの分離](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/vendor/channel-pack/src/channel-pack-store.ts#L324)、[複数store/process境界](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/vendor/channel-pack/src/token-ledger-store.ts#L1)。

### 生成が変更する範囲をpayloadごとに見る

生成はmembership/model entryを解決 → off/unknown拒否 → tool pairing修復 → effort/token budget → wire payload → recovery時はtool choiceをnone → token saver → 匿名車線のみtool fingerprint rename → channel別通信、という順です。aggregateは設定されたgatewayのprovider/modelへ、channel車線は専用実装へ、匿名車線はmodel別endpointへ進みます。全modelの送信先・認証が同じではありません。

token saverは最終payloadへ適用され、推定用payloadにも適用されます。UIの節約表示だけではなくmodelへ渡す情報を変えます。recoveryは2 attemptの内側で再送・継続を組み立て、AbortSignal、total timeout、continuation timeoutを扱います。Hostへ記録される元Session logと、adapter内部で修復/圧縮した実payloadの差を再構成できるかが採用時の条件です。

根拠: [拒否→payload→saver→通信](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/adapter.js#L313)。

[Issue #280](https://github.com/Ebony-Vinyl/dsh-our-free-model/issues/280)は`read_url`本文をgrep結果と誤認し、偽摘要へ置換したという報告です。[PR #285](https://github.com/Ebony-Vinyl/dsh-our-free-model/pull/285)はfile section検証への変更案ですが取得時open、未mergeです。作者提案と現行修正を混同せず、今回実model/APIで再現していません。SearchでRTKのような節約層を加えるならURL本文、Windows path、tool出所、空本文をfixture化する理由になります。

### 更新はdisk復帰とruntime復帰を別に記録する

1. `check`は固定repoのmain/masterをGitHub commits APIで40桁SHAへ解決する。同じrefのraw/CDNは同じsnapshotを共有する。
2. 署名を確認してmanifestを受け取り、version/base/publishedAt/notes/files/minSupportedをcanonical JSONで検証する。案内feedの`feedUrl`は更新code sourceを変更しない。
3. `apply`はcheckを再実行し、要求versionとの一致、downgrade拒否、再署名検証、download/hash/size/staging検証を済ませる。
4. old packageのbackupを検証し、`installing`を先に永続化してからfileを置換する。
5. installed bytesを検証し、`activating`記録→reload→期待versionを確認する。
6. 失敗時はbackupへ復帰する。diskRestoredとruntimeRestoredのどちらかが成立しなければ`recovery-required`を維持し、次回更新を拒否する。

根拠: [SHA snapshot取得](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/updater.js#L242)、[code source固定](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/updater.js#L763)、[更新transactionと復帰判定](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/updater.js#L801)。

hot reloadはLoader内部cacheをpurge → fresh import/export/version確認 → 旧runtime削除とfiber終了待ち → 同じparent/configで新登録 → entryのfiber再関連付け → 新fiberのawaitです。import失敗なら旧codeを残し、登録失敗ならcacheと旧runtimeを復帰します。これは正常manager更新とは異なる所有範囲です。process共通`Symbol.for`のupgrade lockはreloadした後継moduleにも効きますが、別processのfile lockではありません。途中crashのmix-version、lazy import、lockfile/依存変更、複数Host共有packageは未検証です。

根拠: [reload実経路](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/reload.js#L124)、[generationをまたぐlock](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/updater.js#L127)。

### 修正事例: #232は署名の前で全更新が止まった

[PR #232](https://github.com/Ebony-Vinyl/dsh-our-free-model/pull/232)は、v2.1.0の大きいmergeに対してcommits APIのJSON envelopeが256 KiB上限を超え、manifest検証以前のSHA解決で全候補が落ちたと報告します。原因所有者はsnapshot resolverであり、署名やCDN cacheではありません。

修正は`Accept: application/vnd.github.sha`で裸SHAだけを受け取り、JSON fallbackと上限を維持するものです。作者は45/45 testとmanifest再署名を報告し、PRはmerge済みです。現行固定SHAのresolverにも修正があります。しかし元の[v2.1.0 Release](https://github.com/Ebony-Vinyl/dsh-our-free-model/releases/tag/v2.1.0)は10-11公開、package版はその後も2.1.0です。旧installed updaterが新manifestを読めること、既存Release assetが差し替えられたことを、mainの修正だけで保証しません。

今回、`signManifest/verifyManifestSignature`だけを一時鍵で実行し、元manifest受理、署名対象4 field改変の拒否、署名対象外metadataの追加が許容されることを確認しました。鍵rotation/revocation、公開manifestの配信可用性、実plugin reloadは未確認です。

## Routing Suite: 読み込みを変えるinjectorと指示を変えるpreset

### runtime注入は一時実行と再起動後の構成を別々に持つ

injectorは`dev_inject_package`、`dev_install_package`、整包reload、registry保存、自動watch、staging toolの登録を持ちます。profile installはdependency/linkとLoader entryを扱い、runtime injectionはregistryの復元を使います。root bundle patchが挿入するのはinjectorだけで、router presetsを読み込ませる配布構成と同一ではありません。

reloadは内部`loadCache`のrealpath URLに依存し、freshness検査、旧module/cache backup、旧fiber disposal、新fiber関連付け、rollbackを持ちます。自分をreloadする場合は旧contextの外のtimerへ再建を委ね、watchによる自己reloadを避け、watchdog/healも使います。普通のpluginに「reload toolだけ」を借りると、この独立timerと旧contextを扱う責任も増えます。

stagingはJS sourceを`staging.json`へ保存し、起動時に`new Function`で再compileし、promoted toolを再登録します。ツール説明を増やすだけではなく、Hostの`ctx`へ届くコードの保存・再実行機能です。専用trusted development環境での採用条件を明示すべき箇所です。

根拠: [root bundleの範囲](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/cordis.patch.yml#L1)、[registryとcache purge](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/injector/src/index.ts#L584)、[reload/self reload](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/injector/src/index.ts#L882)、[staging再compile](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/injector/src/index.ts#L1408)。

### 段階ごとのツール許可リストとprompt側の子Session除外が一致しない

router-standardは段階0〜3をSession IDに結び、read/planning/write/verify toolsを順次開き、旧restrict disposerを外してから新restrictを掛けます。複数restrictは交差するため、単に後のallowを増やすだけでは解除になりません。gradeの完了時にはfull catalogへ戻します。

prompt assemble側は`parentSession`があれば処理を外れます。一方、固定SHAの`agent/pre-step`は子Sessionを同じ条件で除外せず、そのsidの新stage 0状態を作る経路です。`applyStageRestrict`にも子Session除外がありません。この差はソースから確認できるが、どの宿主でtool喪失が実発生するかを今回実行確認したわけではありません。

根拠: [restrict解除と再設定](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/preset/router-standard/router-bootstrap.mjs#L573)、[prompt側除外](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/preset/router-standard/router-bootstrap.mjs#L629)、[pre-step側状態](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/preset/router-standard/router-bootstrap.mjs#L679)。

[PR #120](https://github.com/yjh051108/dsh-routing-suite/pull/120)は子agentがtodo_write後に別Session recordへ移り、bash/send_messageを失う実測を報告し、三つのguardへparentSession条件を追加しました。[PR #117](https://github.com/yjh051108/dsh-routing-suite/pull/117)は常駐`skill` loaderをallowlistから落とし、skill catalogまで空になったという報告と修正案です。両PRは**closedだがmerged_atがnull**。作者が方式を使わなくなって閉じたコメントがあり、公開版で直ったとは記載できません。成功selftest/実機結果は各提案作者のbranch上の報告です。

### 0.2.x向け提案を現行mainの機能にしない

[PR #220](https://github.com/yjh051108/dsh-routing-suite/pull/220)は取得時openです。bundle preset宣言、package subpath export、persona `text→prefix`、producer-owned message source、profile reloadのremove/createへの変更を提案しています。作者は0.2.0-rc.2 Desktopでの読み込み・再読み込みと51testを報告しますが、今回mainを同条件へ導入していません。

固定SHAのroot patchは依然`.agent-presets`説明を持ち、root exportsにpreset subpathはありません。root packageとinjector/packageのpeer名差も残ります。さらにrouter-standardは単句RL_PERSONAをassembleで使い、coreの分類関数があることだけでtask別persona選択が実行されると判断できません。#220自身も読み込みの修正とwe-form persona変更を別の提案として説明しています。model文体指標の改善は、タスク正答率やDSH元動作維持の証明ではありません。

gradedは`edit_plan/lock_stage/mark_task`等、disk状態、承認UI、pre-step注入を持ちます。`userMsg`にはIDがありますが固定SHAはgeneric `source.kind: plugin`を使うため、v4 producer-owned契約への追従は#168/#220の提案と分けます。冒頭コメントの「未触発ならtools無し」と、その後の全局常駐tools説明も同時にあり、紹介文だけで非介入とは扱いません。

根拠: [graded protocolと登録の説明](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/graded/src/index.js#L1)、[注入source](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/graded/src/index.js#L62)、[persona定数](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/preset/router-standard/router-bootstrap.mjs#L56)。

## Anchored Standard: 最初の要求条件を固定する代償

presetはagent-planeのisolate realmを使い、host-owned sandbox/approval/persistence/model routeとは構成を分けます。しかし「hostのenforcementを残す」と「そのpolicy snapshotをmodelへ見せる」は別です。

`context-gate`を最初に登録し、assembleの`contexts`を未promotion中空にします。pre-stepは`next()`後、claimed batchのidentity/IDとallowKindsだけを残すため、後のpluginが足した自動contextも落ちます。bootstrapはbash/editorへmodel-visible catalogを絞り、durable tool/callまたはassistant/messageでpromotionします。`compaction/end`でphaseを再び閉じ、境界後の新しいsignalを待ちます。子agentも`includeSubagents: true`なら自分のfirst requestをgateします。

promotion後もresident toolsと検索で開いたtoolsを使う構成です。instruction-hintはAGENTS本文を参照先案内に置換し、personaはcomplete/ランタイムcontext無しのMinimal条件を使います。AGENTS指示を毎要求受け取るというDSHの前提、unknown plugin context、最初のapproval/sandbox説明が変わるため、認証/UI日本語化/Searchへ暗黙採用する機能ではありません。適用後に「情報が少ない」状態をagentがどう補うかまで評価が必要です。

根拠: [realm/gate/bootstrap構成](https://github.com/xiaobright/dsh-anchored-standard/blob/dda23ef119e3715f417d73f72eca407732846d1a/preset/agent.cordis.yml#L21)、[assembleとpre-stepのfilter](https://github.com/xiaobright/dsh-anchored-standard/blob/dda23ef119e3715f417d73f72eca407732846d1a/shared/context-gate.mjs#L155)、[promotion後hint](https://github.com/xiaobright/dsh-anchored-standard/blob/dda23ef119e3715f417d73f72eca407732846d1a/shared/instruction-hint.mjs#L188)。

wire-think変種はturnのstep 0を別providerへ送り、独自adapterが`tool_choice: none`とprovider wireを作り、execute時にrouteを戻します。think routeが登録されなければzero-toolへdegrade、steer失敗ならthink replyがそのturnのanswerになる方針です。資格情報は公式routeの利用と別adapterの通信境界を確認する必要があり、元agent loopを完全に保つpresetではありません。

根拠: [phaseとroute交換](https://github.com/xiaobright/dsh-anchored-standard/blob/dda23ef119e3715f417d73f72eca407732846d1a/shared/wire-think.mjs#L183)、[独自wire request](https://github.com/xiaobright/dsh-anchored-standard/blob/dda23ef119e3715f417d73f72eca407732846d1a/shared/toolchoice-adapter.mjs#L192)。

### 修正事例: #76と#78は似た履歴障害でも所有者が違う

[Issue #76](https://github.com/xiaobright/dsh-anchored-standard/issues/76)はrestart後にin-memory dedupが空になり、同じmessage IDのhintを再注入して履歴assemblerが失敗する報告です。[PR #79](https://github.com/xiaobright/dsh-anchored-standard/pull/79)はdurable scanを維持した上でUUIDを足し、scan前にhistoryがmaterializeされない穴を「重複tokens」に留める修正を08-23にmerge。作者の209/209成功報告があり、固定SHAにもunique IDがあります。Release APIは空で、最初の配布tag/tarball境界は確定していません。

[Issue #78](https://github.com/xiaobright/dsh-anchored-standard/issues/78)はID無しのhintによるreload失敗ですが、maintainerは`buildInstructionHint`が別repoのliangshen実装と訂正しています。同名`tool-bootstrap.mjs`を原因所有者の同一性に使わない例です。#79は新規注入の耐性であり、既に壊れた保存logの自動migrationではありません。

[PR #90](https://github.com/xiaobright/dsh-anchored-standard/pull/90)はpersona `text→prefix`変更をmergeし、作者は223/223と実schemaでのmountを報告します。完全personaの文字列を保っても、旧hostとのone-way migration条件は残ります。root package `0.1.0`だけで、この追従の導入版を識別できません。

今回はNode 22.23.3で`node --test test/context-gate.test.mjs test/compaction-epoch.test.mjs test/instruction-hint.test.mjs`を実行し、43/43成功しました。fake context/eventを使うkeyless testsです。実DSHの保存・resume・provider生成、全変種、modelの文体効果はこの成功に含まれません。

## AgentTeams: parent modelの継承と制約の緩和を分ける

member routeはcaller指定 → plugin default → captain request routeの順で合成し、provider/modelをpairとして扱います。明示providerには明示modelが必要、model ID中の`/`はprovider separatorではありません。model-only plugin defaultはcatalogからownerを探せますが、複数providerが同じIDを持てば曖昧として拒否します。routeが変わればcaptainのeffortを持ち越さず、新modelのdefaultを使います。

`resolveMemberLlmSelection` → model capability検証 → `spawnMember` → subagent providerのcontinuable/persona/toolFilter対応を確認 → owner policy + captain/depth denyを合成 → `ctx.subagents.startContinuable`へparent/persona/agentOptions/AbortSignal → childIdをmemberへ保存、という経路です。現在のowner configured denyは、hostのunknown-name回復retryでも削除しません。host固有のbuilt-in denyだけを緩和対象にするため、互換性回復を権限緩和へ広げない設計です。

根拠: [model route解決](https://github.com/NanmiCoder/dsh-agent-teams/blob/1094b84add6f2fb19edf659367fe2fd5f7f14154/src/members.ts#L449)、[spawn実経路](https://github.com/NanmiCoder/dsh-agent-teams/blob/1094b84add6f2fb19edf659367fe2fd5f7f14154/src/members.ts#L867)、[owner denyの保持](https://github.com/NanmiCoder/dsh-agent-teams/blob/1094b84add6f2fb19edf659367fe2fd5f7f14154/src/tool-policies.ts#L150)。

team.jsonとJSONL mailboxはworkspaceのstateDirに保存し、per-team Promise queueでread-modify-writeを直列化します。mailbox live deliveryには60秒leaseがあり、task attempt/receiptを照合する構成です。taskのcompleted/failed/cancelledは終端で、approval、依存DAG、repair/review gateを別記録として持ちます。diskのmember routeとsubagent descriptorをcold resume時にも照合します。「継続可能Sessionが保存された」と「Web restart後に全memberが自動起動する」は別なので、recover/wake経路を受け入れ条件に置きます。

根拠: [state/mailboxとqueue](https://github.com/NanmiCoder/dsh-agent-teams/blob/1094b84add6f2fb19edf659367fe2fd5f7f14154/src/state.ts#L1)、[cold child setup](https://github.com/NanmiCoder/dsh-agent-teams/blob/1094b84add6f2fb19edf659367fe2fd5f7f14154/src/members.ts#L614)。

### 修正事例: #224は全局hookで障害を収容した

[Issue #224](https://github.com/NanmiCoder/dsh-agent-teams/issues/224)は非法team.jsonのSyntaxErrorがglobal pre-step/mailboxへ漏れ、無関係Sessionも止まる報告でした。[PR #225](https://github.com/NanmiCoder/dsh-agent-teams/pull/225)は10-05にmerge。state libraryのthrow契約は維持し、mailbox境界では原decisionのpass-throughとwarning、delegation guardではteam.jsonを指す明確な拒否へ変えます。状態が読めないときのackは消費を偽るため送らず、委任はpolicy確認不能として拒否します。

作者は旧/新13ケース比較、7回帰、8 host実runtimeを報告しています。今回suite未実行です。修正は現行固定SHAにあり、[v0.1.23](https://github.com/NanmiCoder/dsh-agent-teams/releases/tag/v0.1.23)と[release PR #233](https://github.com/NanmiCoder/dsh-agent-teams/pull/233)の配布境界も確認できます。保存書込みのatomic性と、破損を読むglobal hookのblast radiusを分けた小さい設計が参考になります。

しかし[Issue #235](https://github.com/NanmiCoder/dsh-agent-teams/issues/235)は0.2.1-alpha.2で`startContinuable`がなく全memberのstartが失敗すると報告しています。固定SHAもそのmethodを呼びます。対応宣言外hostの報告であり、0.1.23の対応host検証を否定する材料にはしません。LoaderでpluginがRunning、建隊やapprovalが成功することはchild生成成功の証拠ではありません。

## IM: 外部sender、管理browser、DSH permissionを三つに分ける

### 認証済みbotから届いたmessageも操作権限は別

管理RPCは既定`trusted-host`でDSHのbrowser auth/Host/Origin admissionを使い、更新RPC等はloopback条件を指定します。Feishu secret保存は`ctx.credentials`を使い、App secretを先に、App IDを後に保存し、二つ目失敗なら前値へ復帰を試みます。これはrollback付き複数writeで、復帰失敗もあり得るため完全transactionとは呼びません。

根拠: [管理authority](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/plugin-src/host/rpc-authority.mjs#L1)、[secret所有と復帰](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/plugin-src/host/channels/feishu/credential-store.mjs#L1)。

Feishu `accept`はAbortとmessage ID → bot self-loop/mention → legacy allowlist → group addressed条件 → durable seen + in-flight IDs → conversation/topic key → direct/groupとcommand権限 → queueへ進みます。session切替、workspace変更、カード操作は単にbotと接続できることでは許可されません。new bot seedとmigration seedも違います。**新Feishu/QQ botはdirect/groupの通常messageとcommandがopen**。旧Feishu migrationではowner wildcard等の旧設定を読んでseedし、保存済みpolicyを上書きしません。Telegram compatible等も一律private allowlistではありません。

今回純粋helperで新Feishu/QQの未知senderを8組（direct/group × message/command）通し、legacy Feishuの未知sender拒否とmalformed policy拒否を確認しました。これは認証/IM通信を一切行わない確認です。Remoraのdevice enrollmentやscope選択を借りるとき、botのcredential possession、remote sender ID、DSH tool approvalを一つの「認証済み」にまとめない条件が得られます。

根拠: [実message admission](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/src/channels/feishu/bridge.mjs#L1156)、[channel別migration/new bot seed](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/plugin-src/host/channels/shared/access-policy-production.mjs#L42)、[policy決定](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/src/channels/shared/access-policy.mjs#L165)。

### SessionとmessageのIDを結び、再接続で再promptしない

botごとのstateはconversation key→sessionId、直近1000 seen message IDs、topic、watch、mirror、deferredを保存します。write queue→snapshot→`0700` directory/`0600` temporary→renameです。managed topicはthreadとroot messageを使い、同じgroupの全会話を一つのSessionに潰しません。1000件のbounded dedupは無期限のexactly-once保証ではありません。provider送信成功とmarkSeenの永続化の間のcrashを別条件で調べます。

根拠: [stateとbounded dedup](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/src/channels/feishu/state-store.mjs#L27)、[永続write queue](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/src/channels/feishu/state-store.mjs#L201)、[topic key](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/src/channels/feishu/bridge.mjs#L1009)。

HarnessClientのaskはSession確保/モデル設定 → interaction streamを先に開く → baseline seqとprompt rpcIdを保持 → `session.prompt` → event/historyで当該turnを追う → answer/approval/questionをIMへ返す経路です。modern adapterはHTTPを経ず`ctx.typertGateway.invoke/stream`へ進みます。event mux再接続、interaction owner、Session filter、promptAccepted/turnFinishedが二重promptと別turnの返信取り違えを避ける境界です。接続supervisorは単一running処理と段階backoff、healthy pollを持ち、closeではtimer停止とrunning完了待ちを行います。

根拠: [interaction→prompt→追跡](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/src/channels/shared/harness-client.mjs#L1958)、[ownerとreconnect](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/src/channels/shared/harness-client.mjs#L2187)、[in-process gateway](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/plugin-src/host/modern-harness-api.mjs#L218)、[supervisor終了条件](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/plugin-src/host/channels/shared/connection-supervisor.mjs#L61)。

Session logはagentへの入力/結果を再構成し、stateのmirror/deferredとerror referenceは配信状態を追います。これだけで改ざん耐性のある監査trail、全sender操作と全credential更新を永続監査できるとは確認していません。Remoraへ持ち帰るなら、Session append、RPC receipt、external send、audit flushの各完了点を別々に設計します。

### 修正事例: #352は再起動しても復活する永続retry

[Issue #352](https://github.com/xmanrui/dsh-im/issues/352)は4.38.1で14日超のFeishu card更新が30秒ごとに永久再試行される報告です。mirrorはrestart復元を目的に永続化され、clear条件は更新成功だけだったため、外部serviceが永久に拒否するcardが残り続けました。

作者の[b857025](https://github.com/xmanrui/dsh-im/commit/b857025)と[v4.38.2](https://github.com/xmanrui/dsh-im/releases/tag/v4.38.2)（10-13 03:14 UTC）は、14日snapshot TTL、expired errorの終端扱い、永続20回failure budget、timerごとのkey限定復元を追加しました。作者は4072 testと実過期cardの1回送信→原interval後再試行なし→reload後復元なしを報告しています。今回外部送信していません。現行ソースにもqueue内で最新entry再読込み、adopted turnのowner確認、expiry判定、clear timer + durable record削除があります。

根拠: [mirror回復の現行順序](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/src/channels/feishu/bridge.mjs#L866)。

[Issue #346](https://github.com/xmanrui/dsh-im/issues/346)も、HTTP JSONでは消える`undefined` fieldがin-process gatewayでは残り、clientTimeZoneの入力検証で全promptを拒否された例です。作者は[v4.38.1](https://github.com/xmanrui/dsh-im/releases/tag/v4.38.1)で省略処理とHARNESS_PROTOCOL分類、実bot/steer検証を報告しています。入力拒否、Session受入れ、model失敗、IM返送を同じINTERNAL_UNKNOWNに潰さない設計が必要です。

更新は固定npm packageのmetadata/tarball origin・path・sha512 integrityを検証し、profile別intent/lockと実installation再照合を持ち、成功はrestart-requiredで止まります。registry integrityはOFMの導入済みEd25519鍵によるmanifest署名とは別です。自作更新と比較するときは「何が真正性を保証し、どの状態へ適用するか」を記録します。根拠: [固定npm取得と検証](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/plugin-src/host/update-service.mjs#L20)、[導入後照合とrestart-required](https://github.com/xmanrui/dsh-im/blob/f6a9dd0abbeae605e459a660a9922c9a703e6aa0/plugin-src/host/update-service.mjs#L282)。

## 比較枠: Purgeはhook追加に加えて宿主fileを書き換える

YuJunZhiXue/dsh-purgeはdefault branch `master`、固定SHA `6c1d638d1bdcc45ede50fc30249c753d58122a51`、manifest `1.1.71`です。bundleとClient entryを持ち、preferred tarballはmutable master archive、peerはCordisのみ、`dshTarget`は0.2.0-rc.2です。これをhost API全互換の根拠にはしません。

bundle patchでHarness identityとpersona設定を変更し、Hostはglobal pre-stepのmemory message filter、system-prompt/assembleとassemble guard、Session hook、retry/continueを持ちます。さらにcore/host側に宿主install file、shim、backup/reapply/uninstallの処理があります。preset内の一時gateと違い、fileへ適用したpatchはhook disposerだけで元に戻る性質ではありません。codeにrevert/uninstall経路があることと、解除・別host更新で復旧を実証したことも分けます。

根拠: [配布宣言](https://github.com/YuJunZhiXue/dsh-purge/blob/6c1d638d1bdcc45ede50fc30249c753d58122a51/package.json#L64)、[identity設定変更](https://github.com/YuJunZhiXue/dsh-purge/blob/6c1d638d1bdcc45ede50fc30249c753d58122a51/cordis.patch.yml#L24)、[global message filter](https://github.com/YuJunZhiXue/dsh-purge/blob/6c1d638d1bdcc45ede50fc30249c753d58122a51/lib/index.js#L457)、[assemble変更のlifecycle](https://github.com/YuJunZhiXue/dsh-purge/blob/6c1d638d1bdcc45ede50fc30249c753d58122a51/lib/index.js#L697)、[宿主patch実装](https://github.com/YuJunZhiXue/dsh-purge/blob/6c1d638d1bdcc45ede50fc30249c753d58122a51/lib/core.js#L1)。prompt本文は転載せず、生成・patch・retryを実行していません。DSHの元system promptとagent動作を維持する自作方針では、採用対象にしません。

## 自作Pi / Search / Remoraへ持ち帰る小さい設計

| 持ち帰る単位 | 採用条件 | 対応する自作課題 |
| --- | --- | --- |
| provider別OAuth claim番号 | token交換中のcancel/logout/new loginをfixture化。refresh成功の遅延writeも別に扱う | Piのcredential復活・交換完了取り違え |
| capability-bearing accountをprepareCallへ固定 | stream直前のpolicy取消を検証。表示IDはwire IDと分ける | Piの動的catalogとOFF、Fast/effort能力 |
| catalog writerのpath別queueとbounded rename retry | 複数processで共有なら別の排他契約。fire-and-forget保存失敗を観測可能にする | Pi/Searchの永続fallbackとWindows保存 |
| disk/runtime復帰を分けた更新状態 | manager経由のprofile/operation/receiptに合わせる。独自Loader cache purgeは必要性がある場合のみ | 自作更新のprofile identity、restart案内 |
| global hookの狭いcatchとack保留 | 読み取り障害時は無関係Sessionを通す。権限検証不能の委任は拒否 | Remora接続状態・監査保存と無関係会話 |
| 永続retry budgetと外部serviceの終端分類 | 期限切れなど成功しない要求の再試行を打ち切り、restartでbudgetを戻さない | Remora reconnect・Search HTTP再試行 |
| Session/rpcId/外部message IDの明示対応 | 外部送信と保存完了を別ackにする | Remora audit flush、response喪失後の照合 |

認証追加を理由にcontext gate、persona固定、graded loop、token saver、Purgeの宿主patchを同時採用しません。model動作変更は別の要求と評価で扱います。自作の公開修正履歴は[own cases](../workflow/own-cases.md)、更新状態の記録は[更新実装](../update-implementation.md)と照合します。

## 次に実行するtargeted testと今回の限界

- OAuth: callback到着→exchange保留→cancel/logout→exchange解放。加えてtoken refresh成功/永久失効とnew login/logoutを交差させ、accountとaliasとdiskが一致するか確認する。
- catalog: plan違いで同じmodel ID、rename、OFF直後のprepared stream、壊れたsnapshot、catalog更新中dispose、shared pathの二processを分ける。
- wire: Fast対応あり/なし、保存ultra、tier fallback後のeffort/context、tool resultと画像が交互になる履歴、token saverのURL本文誤認をfixture化する。
- updater: mutable refが途中で変わる、署名不一致、hash不一致、backup後process kill、file置換途中、fresh import失敗、新fiber失敗、runtimeだけ復帰不能を分ける。実公開code更新は行わない。
- routing: skill loaderのschemaとcatalog、own-scope shadow、子Sessionのstage記録、compaction、restart、別generation restrict解放を確認する。closed未mergeの提案branchとmainを同一試験で比較する。
- AgentTeams:対応hostのfresh/cold child、member-relative maxDepth、owner deny未知名、corrupt team.jsonと無関係Session、stale task attempt、親fork、fallback後effortを確認する。
- IM: unknown sender/direct/group/command、policy変更中カードaction、1000件超duplicate、送信成功直後crash、interaction再接続中cancel、mirror expiry/20回/restart、Session archived、audit writer保留を確認する。

今回実行した検証は、Anchoredの3 test file 43/43と独立`helper-probes.mjs`（署名field・new bot policy）のみです。`node --test test/channels/shared/new-bot-access-policy.test.mjs`は2件とも外部SDK未導入（Lark/QQ）のmodule解決で失敗し、製品runtimeを評価できませんでした。依存を導入して成功扱いへ変えていません。helper確認へ範囲を縮小しました。

6主要repoのIssue/PRはstate=all、per_page=100の公開API取得を使い、選択した事例のdetail/comments/PR metadataを追加取得しました。全履歴を網羅した調査ではありません。取得SHA、API snapshot、限定probeは調査用snapshotに保存しました。npm registryやRelease assetの実内容一致、外部providerの利用条件・現在の可用性、実desktop/native/mobile、クロスprocess安全性、改ざん耐性の監査は未確認です。
