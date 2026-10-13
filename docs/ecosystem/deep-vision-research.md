# 画像ルーティングと研究presetの経路分析

2026-10-13の固定ソースを対象にした追加調査です。Modlensの解析cacheとwire変換は[前章](deep-browser-memory.md)にあります。ここでは画像を渡した利用者がどのproviderと保存物へ到達するか、研究presetの結論がどの証拠で承認されるかを追います。画像能力のtoolを追加することと、modelの入力・計画・完成条件を変えることは、変更範囲として分けます。

## 導入するものと、ソースの配置

| repo・固定SHA | package版・公開entry | 導入で越える境界 |
| --- | --- | --- |
| ysr666/dsh-vision-router / `dadd0a4115db59280d8ffcda918db57d80bf8f76` | `dsh-vision-router@3.0.3`、`lib/public-entry.js` | native bundleとWeb client。generated libが必要。sharp peer、puppeteer-core、HTTP provider。DSH peerは0.1.5-rc.1〜0.2未満と0.2.0-rc.2〜0.3未満の二範囲 |
| Anionex/dsh-vision-toolkit / `d4fb7402513cab73be915aa6f54d4e7f63ffc46e` | `@anionex/dsh-vision-toolkit@0.1.46`、`lib/index.js` | native bundle/Client。tracked libもある。別Python runtimeとvendored upstreamを使う。DSH peerは旧0.1系列と**exact0.2.0-rc.2**を含み、0.2全系列を受け入れる宣言ではない |
| Clearailhc/clearai-dsh / `950e8fddf53c0546b3233a98447fdb3e9737a225` | `clearai-dsh@0.5.4`、`lib/host.js` | native Host/Clientとagent preset。sourceはui/lib・preset・packに分かれ、buildがdist/clearai-dshへ再配置。DSH peer宣言はない |

manifest: [Router manifest](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/package.json#L1)、[Toolkit manifest](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/package.json#L1)、[ClearAI manifest](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/package.json#L1)。ClearAI rootにmanifestの`lib/host.js`や`cordis.patch.yml`が見当たらないのは、sourceと発行packageのlayoutが違うためです。[配布packageの組み立て](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/tools/build-package.mjs#L10)のcopy表と二つのpatchが実装契約です。GitHub rootをbuildなしでそのまま読むLoaderでは、sourceの存在だけで成功を宣言できません。今回npm導入・build・Python取得は実行していません。

## Vision Router:画像能力に加えHostの入力契約を調整する

標準経路は「Vision toggle/選択route →session別画像indexとpolicy →pre-stepの案内/添付判定 →wrapper/twinまたはvision chain →DSH adapterかHTTP bridge →fallback →text model」です。crop/diff/color/trace等のlocal工具と、describe/detect/ground等のvision providerを使う工具が同居します。14toolという紹介数だけでは、どれが外部へ画像を送るか分かりません。[model-facing経路](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/src/index.js#L2288)

bundle patchはplugin一行に加え、Web connectionのtrustedHostsを設定するcompanion、recompose時のdisabled解除、**Host attachment normalizationの上限変更**を持ちます。画像をplugin独自にraw保存するのではなく、Host canonical pixelsを正とし、20MiB/100MP/10000pxへ揃える設計です。元画像とcanonical画像の座標・EXIF・色域は常に同じとは限らず、groundingやpixel diffの値はどのpixelsを使ったかとセットで返す必要があります。画像toolの追加だけを期待して導入する利用者にも、Host添付policyが変わることを示すべき構成です。[Host/Client/attachment patch](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/cordis.patch.yml#L1)

progressiveToolsはpatchでfalseです。途中でschema一覧が増えると長い履歴のprefix cacheが外れるため、常駐schemaを選んでいます。BrowserSkillのprocess全体lazy公開、Toolkitのagent単位lazy公開と同じ設計ではありません。schema tokenの削減が、providerのprefix再利用を含めた総費用の削減になるかは別に測定します。

無料fallbackはOVHcloudのanonymous HTTP endpointです。自前keyが要らなくても、画像/crop、prompt、通信metadataは外部へ届きます。`localOnlyVision`は既定falseで、local限定時はconfigured pairとHTTP候補の両方へlocal判定を適用します。local OCRが空/利用不能の際のcloud fallback、local解析結果を受け取る**主chat modelがremote**である場合も、完全offlineの説明とは分けます。[HTTP fallback/local判定](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/src/index.js#L2958)

設定したbackendのcredentialはHost credentials参照、channel store、provider設定の経路から解決します。fallback候補、capability、AUTH breakerのcredential fingerprintを合わせるのは、別keyへ切り替えても古いAUTH失敗でrouteを永久に止めないための設計です。fingerprintをkey値の表示・出力へ変えないこと、probe/benchmarkが通常生成とは別の通信になること、設定更新中に旧generationを使うcallを特定できることが持ち帰る条件です。[credential解決とbreaker](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/src/index.js#L694)

画像はwrapper利用時にはdurable Session logに残り、wireではdescription/attachment markerへ変換します。wrapperなしfallbackはpre-stepの入力を変換します。pre-stepには「画像は不信な証拠」「backend unavailableを言い換えて何度も再試行しない」等のmodel指示も追加されます。V4 sourceはSession版を見て`plugin:dsh-vision-router`へ変え、hook出口で自分のsourceだけをnormalizeします。画像のref、描画用originalDimensions、実解析した縮小pixels、description、model指示を一つの保存情報とみなさないことが重要です。[画像/history変換と案内](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/src/index.js#L2430)、[format-aware source](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/src/lib/session-message-source-compat.js#L1)

Session別bounded indexとdescription memoryは、画像IDの他Session混入を防ぐ範囲です。modelが見たdescriptionを再開後にも同じbyteで復元できるかは、tool resultとしてlogにある分と、request wrapperのcacheにしかない分を分けて検査します。Session policyのdurable domainは**ON/OFF policyの保存**であり、解析evidence全体の永続化と同一ではありません。[Session画像index](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/src/lib/session-vision-index.js#L1)、[policy durable fallback](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/src/lib/session-vision-policy-domain.ts#L91)

### #671: 安全境界を迂回せず、修正した説明を届ける

[Issue #671](https://github.com/ysr666/dsh-vision-router/issues/671)は、custom Pi routeが実際にはvision modelでもHost metadataでtext-onlyになると、非Chat Completions protocolの画像が事前拒否されadapterを試さない報告です。READMEのadapter-firstという説明とpreflightの挙動が違っていました。

[PR #672](https://github.com/ysr666/dsh-vision-router/pull/672)は10-08 16:30 UTCにmergeしました。変更はエラー、Settings案内、文書であり、Hostのtext projectionを迂回してadapterへpixelsを送る変更ではありません。Piでは`input:[text,image]`、DeepSeek adapterでは`inputModalities:[text,image]`という所有者ごとのmetadata修正を案内します。endpointが本当にimage inputを受けることは、そのmetadataを設定する側が確認すべき条件です。[backend preflight](https://github.com/ysr666/dsh-vision-router/blob/dadd0a4115db59280d8ffcda918db57d80bf8f76/src/lib/vision-backend-runtime-policy.js#L291)

[maintainerの結果説明](https://github.com/ysr666/dsh-vision-router/issues/671#issuecomment-6064444297)は86/86 checks成功を報告しますが、これは全custom providerへの実画像通信試験ではありません。現行manifestは3.0.3のままなので、このcommitを含む新しい公開npm版の境界は今回未照合です。mainの説明修正、Issue close、配布版を分けます。

[Issue #684](https://github.com/ysr666/dsh-vision-router/issues/684)はWindows Node24のON→OFF戻りが同SHA再実行では通る問題で、取得時openです。後続[#702](https://github.com/ysr666/dsh-vision-router/pull/702)はpointerとDOM置換のbounded traceを追加します。特定のcontrolled scheduleで同じ見た目になったことを、元の失敗原因が判明したことにしない姿勢が参考になります。UIのpressed値だけでHost commit成功・RPC応答・projection反映を代用しません。

## Vision Toolkit: evidenceを保存する単位がSession・prompt・runtimeまで及ぶ

経路は「bundle apply →Settingsを検証 →runtime managerがPython/upstreamを準備 →agentがSkillまたはactivationを使う →agent-scoped tool →Python subprocess →検証したJSON/text/artifact」です。runtime未準備ならSettingsは残し、Skill/activation/toolを登録しないので修復入口を失いません。manager更新が拒否されたら直前のserving generationを維持します。adminの診断とmodel-facing toolのscopeを分けている点がBrowserSkillのlazy公開との差です。[applyとruntime generation](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/index.ts#L43)、[agent-scoped公開](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/exposure.ts#L1)

Pythonはmanaged/externalを選び、managedではbootstrap artifact、version、platform/arch、hash、stage directoryを扱います。manifestはvendored upstream `bc9803d7d6300c864d17460ecbb33540b26638e0` とSkill commitを記録します。「npm依存が少ない」「一行install」からOS/native/runtime準備を省略できるとは考えません。Python3.14、vtracer、Pillow/NumPy、browser screenshotのChromeは別適合面です。[managed Python導入](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/runtime-install.ts#L741)、[Toolkit manifest](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/package.json#L1)

無料defaultは`vision.anionex.me/v1`のpublic serviceで、予約credential参照に合致する設定だけがbundled public値を使います。custom keyは`ctx.credentials`で保存・呼出し時に解決します。configにAPI key本文を置かない設計を持ち帰れますが、public serviceのquota・利用条件・将来の可用性は今回通信していません。無料routeを使っても、送る画像と質問は外部serviceへ届きます。[public service defaults](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/defaults.ts#L1)、[built-in経路の識別](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/config.ts#L520)、[credential store書込み](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/web.ts#L349)

image-input variantはtext modelにimage modalityを持つsynthetic routeを作り、user intentと直前assistant intentをfocusとして画像descriptionを生成します。sourceなしuser messageもuser扱いします。descriptionは元画像pixelsではなく、主modelが受ける追加推定です。channel noteでその違いをmodelへ伝え、absolute artifact pathを後続toolへ渡します。toolの`vision_glance`はanswer/truncated、groundはboxと解析image寸法など、用途別schemaを持ちます。Modlensの一つのOCR/layout/semantics JSONと同一の出力契約ではありません。[focusとimage variant](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/image-input-variants.ts#L430)、[tool output schema](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/tools.ts#L210)

**Modlensより再現性を支える部分**は、durable evidence sidecarです。keyにはSession ID/createdAt/cwd、attachment ID、prompt hash、runtime hash、contract versionを含め、runtime hashにはupstream commit、endpoint/model/protocol、credential fingerprint、header hash等を入れます。古いkeyを新設定の解析として使わず、process再起動後も同一条件のdescriptionを読める設計です。raw focus textをkey metadataへそのまま保存しません。[persistent evidence contract](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/evidence-cache.ts#L54)

ただしsidecarはoptionalです。破損/利用不能時は再解析し、write失敗時もprocess cache結果を返します。保存上限/期限のprune、Session IDなしのprogrammatic呼出し、credential/runtime変更後のmissもあるので、当時のmodel入力が永遠に固定される保証ではありません。失敗文には実エラーの一部を含む入口もあり、cooldown後や再開後のwire byte変化をModlens #68と同条件で検査する価値があります。[persistent evidence contract](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/evidence-cache.ts#L54)、[失敗placeholder](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/image-input-variants.ts#L369)

Toolのtimeoutはcaller AbortSignalとphase deadline、queued semaphore、subprocessへ伝えます。artifactはstaging→validation→公開を扱い、image/source寸法、boxの範囲、manifest入力一致、出力filenameを検査します。cancel時にprocessが終わったことと、remote serverの処理が終わったことは別です。pluginをOFFにしてもすでに公開したartifact/description sidecarは消える契約ではありません。保存場所を変えても過去artifactを読めるよう、configured storage historyもdurableに保持します。[deadline/semaphore](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/runtime.ts#L129)、[storage root履歴](https://github.com/Anionex/dsh-vision-toolkit/blob/d4fb7402513cab73be915aa6f54d4e7f63ffc46e/src/storage-history.ts#L1)

### #156 と #159: 程序化呼出しとSettings改版は別の互換性

[Issue #156](https://github.com/Anionex/dsh-vision-toolkit/issues/156)→[PR #157](https://github.com/Anionex/dsh-vision-toolkit/pull/157)は、official helper由来のsourceなしuser messageをvariantが裸読しTypeErrorになる問題です。09-26 11:28 UTC merge、現行はoptional accessがあります。報告者は当初挙げた別memory plugin0.8.1の具体例が0.8.2で回避済みと[訂正](https://github.com/Anionex/dsh-vision-toolkit/issues/156#issuecomment-5699287874)しています。全memory pluginが現在壊れると一般化せず、helperの正常出力に対するwrapper防御として扱います。

[Issue #159](https://github.com/Anionex/dsh-vision-toolkit/issues/159)→[PR #162](https://github.com/Anionex/dsh-vision-toolkit/pull/162)は旧`ctx.settings.register`の消失でapplyが失敗する問題です。09-26 11:47 UTC merge、現行entryはcompat binderを通します。peerのsemver一致はSettings APIの存在確認ではありません。両修正を含む現行source0.1.46は確認しましたが、Release/npm公開時刻の照合と実Host起動は未実施です。

[Issue #166](https://github.com/Anionex/dsh-vision-toolkit/issues/166)はdefault30秒の外側deadlineがPython側180秒attemptより早く、in-flight remote理解が止まる報告でopenです。6/12 timeout、40〜41秒での成功は報告者のservice/画像/予算条件であり性能順位ではありません。必要な調査はtimeoutを長くして成功させるだけでなく、全体予算が各attempt/retryへ配分されているか、cancel後公開・再試行・残りchildがどうなるかです。

## ClearAI:検索toolの追加ではなく、結論を許すpreset

ClearAIはHost投影/UIとagent-plane kernelの二層です。HostはSession logの変更記録から`clearai` projectionをfoldし、read facade/inspectorを提供します。presetはpersona、PROJECT/AGENTS指示file、shell/fs/web/Skill、native goal/todo/subagent/workflow、kernelを組み合わせます。FS権限・model/provider service・永続化そのものはHost所有の拡張点を使います。独立realmのworkflowEngineとtoolの置き場所もcompositionで決めます。[投影とread facade](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/ui/lib/index.js#L197)、[agent composition](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/preset/agent.cordis.yml#L1)

modelの行動は大きく変わります。`Frame`でclaimと反証条件を登録し、計画のpredictionsを先に作り、`AdvancePlan`でevidenceへ進め、`ClosePlan`/`Conclude`で結案します。systemPromptにはidentity/loop/human-facing方針、pre-stepには状況cardと差分が入ります。tool pre-executeはnative`update_goal(status:achieved)`をConcludeへ誘導し、system-prompt assembleにも関与します。日本語UIやSearch providerの追加だけの目的では、このprompt・完成gateを暗黙に移しません。[model指示](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/preset/plugins/prompts.js#L1)、[tool/prompt登録](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/preset/plugins/clearai-kernel.js#L5472)

独立評価者は通常task用subagentとは別の派遣経路です。評価tool filterはread/glob/grep/read_imageを基準にし、rerunが必要な場合だけshell/jobsを増やします。materials、criteria、answer、method file内容などのdigestで同じ評価を再利用し、材料が変われば再評価します。安定した論理IDと安全なpath componentを分けることで、modelはgoal IDを維持しつつWindows fileへ保存できます。[evaluator tool filter](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/preset/plugins/clearai-kernel.js#L1659)、[material hashとpath identity](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/preset/plugins/audit-material.js#L1)

「独立評価」は別modelが同じ証拠を読む処理であり、実験事実を外部で測定したことの代わりではありません。評価者が読めるpath、rerun script、criteriaの変更、同じmodel bias、ledgerとworkspace artifactの一致を確認する必要があります。audit結果、評価raw text、tool出力、file hash、派生ontologyを保存しても、引用元の信頼性と対象scopeが自動で証明されるわけではありません。

Host panelのviewはread-onlyで、human gateはnative ask/goal経路を使います。pluginの解除はprojection/hook/toolを外す一方、workspaceの`clear/ontology`、audit card、変更logは保存資産として残ります。解除を「研究ファイル全削除」にせず、再mount後のprojection rebuildと旧card読出しを対象versionで確認します。[投影とread facade](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/ui/lib/index.js#L197)

### #21: openでも修正と公開は進んでいる

[Issue #21](https://github.com/Clearailhc/clearai-dsh/issues/21)はWindowsで`goal:<id>`をそのままdirectoryにしてaudit card保存が失敗し、裁決をunknownへ落とし、再Concludeで評価を繰り返す報告です。[PR #22](https://github.com/Clearailhc/clearai-dsh/pull/22)自体は未mergeですが、[PR #23](https://github.com/Clearailhc/clearai-dsh/pull/23)で取り込み、[maintainer comment](https://github.com/Clearailhc/clearai-dsh/issues/21#issuecomment-6095192491)は0.5.2 Release/npm公開を説明しています。現行はstep/auditor IDを固定長SHA-256へ変え、card内のlogical IDは保持します。[audit card保存](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/preset/plugins/clearai-kernel.js#L1750)

作者はWindows Node24 native FS回帰とmacOS real DSH取消/復旧を報告し、元Windows利用者の再確認を待ってIssueをopenにしています。openを未修正と読むことも、公開版を利用者の追認と読むことも誤りです。失敗裁決をunknownのまま保つのは、保存失敗時にもpassedとしてgoalを進めないための選択です。

[Issue #30](https://github.com/Clearailhc/clearai-dsh/issues/30)と[PR #31](https://github.com/Clearailhc/clearai-dsh/pull/31)は取得時openで、Windows presetがpwshだけをmountする一方、三つのshell gateがbashのnameだけを検査する問題を扱います。固定mainにもbash条件が残ります。これはソースと公開報告の照合で、今回dangerous commandを実行していません。Unix regexをpwshへそのまま拡張しても意味が同じとは限らず、cmd alias・argument shape・不可逆操作の実行対象ごとにfixtureを作る必要があります。[shellとgoal gate](https://github.com/Clearailhc/clearai-dsh/blob/950e8fddf53c0546b3233a98447fdb3e9737a225/preset/plugins/clearai-kernel.js#L4977)

## 自作Search/Piへ持ち帰る条件

| 小さい設計 | 採用する条件と副作用 |
| --- | --- |
| ToolkitのSession/prompt/runtime key | modelへ渡したevidenceを再利用する目的に合う。credential変更、prune、sidecar破損、Sessionなしcallを別に扱う |
| Routerのproducer source出口検査 | 自分が作ったmessageだけをnormalizeする。他plugin/user/model sourceを勝手に変えない |
| 明示modalityとnative adapter優先 | Pi model catalogの能力を正確に扱う。text metadataの画像を無条件で別HTTPへ転送せず、verified endpointのbridgeだけを選ぶ |
| Toolkitのagent単位activation | tool一覧とdispatchを実agent scopeで確認する。Skill履歴の再開、別agent、PTC dispatchを同じfixtureへ入れる |
| source/build layoutの明示 | Source rootと配布entryのpathが違う場合、Git導入buildとpacked entryを独立確認する |
| ClearAIのlogical ID/path ID分離 | Search証拠やauditの論理IDを保持したままOS安全な保存名を使う。hashだけでactor/tenant権限を保証しない |
| ClearAIのcriteria/material digest | Search結果の日時、query、provider、引用範囲、再取得hash、評価版を含める。別modelの承認を外部事実の確認と呼ばない |

この追加調査ではhelperの動作試験は実行していません。manifest、patch、call経路、公開Issue/PR/commentを読んだ結果です。各repository最新100Issue/PRを取得し、一部関連commentを取得しました。実画像の送信、無料API、credential保存、Python取得、実Web/DSH、build、npm tarballの照合は未実施です。数値は作者/報告者の条件であり、model品質や本体starsによる順位付けに転用していません。
