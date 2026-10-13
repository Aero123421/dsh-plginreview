# 自作pluginの修正履歴

時刻はUTCです。1〜9は最初の公開履歴調査、10〜11は2026-10-13の更新実装後に追加した事例です。Actionsの成否は公開run記録、ローカル・実機の検証はPR作者の報告として扱い、11のPWAは別途行った再現を記載しています。この文書更新でpluginの試験を再実行したものではありません。[調査方法](evidence.md)に件数と判断の限界があります。

## 1. Pi: Issueの再現条件が修正へ届いた例

| 日時 | 公開記録 |
| --- | --- |
| 10-11 00:53:28 | [Issue #1](https://github.com/Aero123421/dsh-pi-login/issues/1): 設定変更後のreloadが古い取得に吸収され、接続切替後の古い失敗も残る |
| 10-11 01:04:30 | [Issue #2](https://github.com/Aero123421/dsh-pi-login/issues/2): Brokerの10分期限とSDKのDevice Code 15分期限が不整合 |
| 10-11 03:58:21 | [PR #3](https://github.com/Aero123421/dsh-pi-login/pull/3)作成 |
| 10-11 03:59:10 | [PR CI](https://github.com/Aero123421/dsh-pi-login/actions/runs/38110082895)成功 |
| 10-11 04:00:09 / 04:00:11 | merge / 両Issue close |
| 10-11 04:01:37 | [v0.2.1](https://github.com/Aero123421/dsh-pi-login/releases/tag/v0.2.1)公開 |

Issue #1は対象commit、RPCダブルの再現、設定変更後の取得、旧接続の遅延成功・遅延失敗を示していました。#2も固定SDKの期限とBrokerの期限を比較し、中断・SDK期限切れ・plugin側timeoutを分ける条件があります。修正はこれらに対応しました。

ここでは報告から実装へ渡す条件が明確です。公開履歴から調査の入り口を主な詰まりとは呼べません。追加の大きいIssueフォームより、この具体性を維持する方が役立ちます。

残るのは実認証です。PRはunit、公式API互換、実SDK runtime、browser、packの確認と、実OAuth未検証を分けています。Issue closeは配布より86秒早く、利用者の実Device Code完了の公開追認は確認できません。競合・期限を直した証拠と、端末・資格情報を使う認証の証拠を引き継ぐ必要があります。

## 2. Pi Fast: 前提の訂正とUI方針が同じPRで動いた例

[PR #5](https://github.com/Aero123421/dsh-pi-login/pull/5)は10-11 04:34:54作成、08:51:48 mergeです。[24commitの履歴](https://github.com/Aero123421/dsh-pi-login/pull/5/commits)には次の変更があります。

| 時刻 | 変更 |
| --- | --- |
| 04:30:42 | Museのtier別Max能力補正を追加 |
| 07:15:34 | ハードコードしたMax補正を撤回し、Piカタログの能力を維持 |
| 08:16:09 | Fastを通常版と別のモデル項目にする |
| 08:24:25 | Fast選択の変更をモデル一覧へ通知 |
| 08:51:25 | [最終headのCI](https://github.com/Aero123421/dsh-pi-login/actions/runs/38126242016)成功 |
| 08:53:02 | [v0.3.0](https://github.com/Aero123421/dsh-pi-login/releases/tag/v0.3.0)公開 |

専用toggleはPR途中の実装にあり、最終版は独立した候補です。通常版とFast版のON/OFF、effort、APIへ送るmodel ID、画面の選択IDを分け、priority指定が失敗した場合の黙った通常版再送も避けています。

[初回CI](https://github.com/Aero123421/dsh-pi-login/actions/runs/38112040482)は04:35:43に成功していました。その後に能力補正の撤回とUI変更があるため、初回の緑を最終仕様の確認に使えません。レビューと期待値は、前提を撤回した後の差分まで追う必要があります。

分析としては、「Maxが足りないという観察」「対象モデルの実体」「Fastをどう選ぶか」を先に分ければ、補正の撤回やUIの作り直しの一部を減らせた可能性があります。ただし24commit全部を無駄と数える根拠はありません。追加検証や文書・配布準備も含まれます。

同じ表示名でもモデルの実体は異なります。`provider ID / exact model ID / API protocol / credential method / SDK version / endpoint`を識別し、SDKカタログ、Hostが公開する能力、実APIの受理・適用を分けます。PRのkeyless runtime検証は、契約別Fast資格、速度、課金の確認ではありません。

### openの3件は何を待つ仕事か

| Issue | 公開記録で分かる残件 | 次に必要な確認・判断 |
| --- | --- | --- |
| [#4 Muse Contributor Max](https://github.com/Aero123421/dsh-pi-login/issues/4) | Standardの正常とContributorの実API未確認を区別して調査中 | exact routeとSDK版を固定し、要求したeffortが受理・適用されるか確認する。HTTP 200だけで判定しない |
| [#6 動的カタログ](https://github.com/Aero123421/dsh-pi-login/issues/6) | SDK更新とruntime情報更新を分ける設計予定 | 候補と検証済み能力、手動設定、オフライン・429時の扱いを決める |
| [#7 他provider統合](https://github.com/Aero123421/dsh-pi-login/issues/7) | 認証flowとproviderの汎用対応付けがなく、管理の委譲が課題 | 元pluginが提供する識別・操作契約を確認し、表示の統合範囲を決める |

Issue #4の本文に鍵がないため待っているとは書かれていません。#6/#7も期限超過や放置と判断する根拠はありません。未確認、設計予定、外部条件による待機は分けます。

## 3. Pi・日本語化: tarballの配布とGitHub指定の導入が別だった例

Pi v0.3.0と日本語化v0.1.0にはRelease tarballがありました。しかし[Pi PR #8](https://github.com/Aero123421/dsh-pi-login/pull/8)と[日本語化PR #1](https://github.com/Aero123421/dsh-japanese/pull/1)は、GitHub指定で未ビルドsourceを取得して起動できない問題を扱っています。

両PRは10-11 09:55頃に作成し、10:02頃にmerge、[Pi v0.3.1](https://github.com/Aero123421/dsh-pi-login/releases/tag/v0.3.1)と[日本語化v0.1.1](https://github.com/Aero123421/dsh-japanese/releases/tag/v0.1.1)を10:05頃に公開しました。GitHub取得用distを追跡し、CIでbuild後の差分を検査しています。

Piの[初回PR CI](https://github.com/Aero123421/dsh-pi-login/actions/runs/38130097456)はbuild成功後、`git diff --exit-code --stat -- dist`で失敗し、後続testはskipでした。同じ公開head SHAの別push runは成功しています。CSSの並行読込みによる出力順序を固定し、[最終CI](https://github.com/Aero123421/dsh-pi-login/actions/runs/38130324939)が成功しました。これは新しい確認が、再現可能buildの不足を見つけた例です。

両PRは隔離した実DSH Web profileへのGitHub指定の追加、起動、認証済みHTML応答を報告しています。ここで使う「認証済み」はDSH Webの接続についての記録で、providerの実OAuth完了へ広げません。

詰まりは、開発checkoutからbuildしてpackした物と、READMEのコマンドが利用者へ渡す物の不一致でした。公開予定の指定をそのまま空profileへ入れる確認が、この境界を直接試せます。

## 4. PWA: 宿主のworkspace制約を複数repoで再発見した例

[PR #2](https://github.com/Aero123421/dsh-pwa/pull/2)は10-11 12:31:37作成、13:02:01 mergeです。追加・削除コマンドへ`-w`を加え、DeepSeekロゴの著作権表示・MIT全文をpackageに含め、GitHub-hosted CIを追加しました。

PRはunit、pack一覧、隔離DSH Web profileのadd/remove成功を報告し、[PR CI](https://github.com/Aero123421/dsh-pwa/actions/runs/38139598532)も成功しています。日本語化・Piでも同日にWeb導入コマンドの`-w`修正が必要でした。共通する導入条件がrepositoryごとに再確認されていることは、複数pluginを作るときの手戻りの手掛かりです。

再利用するべきものは宿主・profile・取得元を固定した確認方法です。workspace rootと公開bundleの位置が違うRemoraへ、同じコマンドを確認なしにコピーする方針にはしません。

この事例を調べた時点ではPWAのGitHub Releasesは0件でした。その後の公開版は[一覧](../own-plugins.md)で確認できます。GitHub source導入があるため、Releaseがないことだけで公開停止とは言えません。add/removeの成功も、iOS・Androidのホーム画面追加や更新後のアイコン反映を確認したことにはなりません。[PR #3](https://github.com/Aero123421/dsh-pwa/pull/3)のアイコン変更は表示方針の変更で、#2の障害再発に数えていません。

## 5. 検索: 公開とCI終了が並行し、後からtestの競合を直した例

| 10-12の時刻 | 記録 |
| --- | --- |
| 08:48:10 | [x_search PR #1のCI](https://github.com/Aero123421/dsh-search-providers/actions/runs/38225614498)成功 |
| 08:52:17 | [PR #1](https://github.com/Aero123421/dsh-search-providers/pull/1) merge |
| 08:52:59 | [v0.2.0](https://github.com/Aero123421/dsh-search-providers/releases/tag/v0.2.0)公開 |
| 08:54:18 | [merge後main CI](https://github.com/Aero123421/dsh-search-providers/actions/runs/38226258901)の`test:native`失敗 |
| 08:54:31 | 同じmain SHAの[別push run](https://github.com/Aero123421/dsh-search-providers/actions/runs/38226327860)成功 |
| 09:13:15 | [追加commit](https://github.com/Aero123421/dsh-search-providers/tree/ca7a1e484cd25e1812fc333c85b0185a40659e49)でnative fixtureを修正 |

追加commitはwelcome noticeをprofileで事前承認し、対話で閉じる処理とConfigEditorの再接続との競合を取り除いています。固定時間のdismiss loopをSettingsの待機に替え、終了処理ではprocess exitを待ちます。[続くCI](https://github.com/Aero123421/dsh-search-providers/actions/runs/38228475142)は成功しました。

同じSHAの成功と失敗が並んだだけでは、製品とtestのどちらが悪いか分かりません。ここはfixtureの追加修正です。前日の同じ`test:native`失敗ではpnpmの追加が必要でした。step名を原因名にしてはいけません。

公開はmain CIの失敗判明より79秒早く、公開後に失敗が見える順序でした。公開判断に使う最終SHAの関連確認が何か、release側で同等の確認をしているかを明示する必要があります。

実APIの残件は別です。PRはFxTwitterの投稿URL取得成功と、キーワード検索404・成功未確認を分けています。fixtureのCI修正は検索endpointの問題を直していません。404を空の検索成功へ変えると、未確認だった機能を対応済みに見せてしまいます。

## 6. Remora: greenだった順序を、保存保証と取り違えた例

[PR #1](https://github.com/Aero123421/dsh-remora/pull/1)は14指摘を修正し、10-12 15:51:38にmergeしました。[PR Checks](https://github.com/Aero123421/dsh-remora/actions/runs/38268802367)と[E2E](https://github.com/Aero123421/dsh-remora/actions/runs/38268802315)は成功し、本文は3agentの相互レビューを報告しています。

ところが[merge後Checks](https://github.com/Aero123421/dsh-remora/actions/runs/38273291489)は15:52:26に失敗しました。鍵更新の3段階が監査ログにあるというassertionが満たされず、build・packはskip、Hubの別jobは成功です。

[PR #2](https://github.com/Aero123421/dsh-remora/pull/2)は、監査ログreadの前に`auditLog.flush()`を待ち、RPCもawaitする修正を16:16:25にmergeしました。鍵更新・再接続の完了と、非同期監査書込みの完了は別でした。最初の成功は保存完了を待つ契約の証拠にはなりません。修正差分からは、write後にreadが走る順序では問題が表れなかったと考えられます。

回帰ではwriteの実ファイルロックを保持してreadを開始し、readが待つことと、解放後の全記録を確認します。PRは旧実装で失敗することも報告しています。timeout延長や一度の再実行より、欠けた順序保証を直接確認できる方法です。

分担の教訓は、担当ファイルと「完了しました」だけでは足りないことです。writer担当の完了、RPC担当の完了、readerが必要な保存保証を揃えます。公開記録から非公開agentの会話不足を立証したわけではありませんが、統合レビューでこの境界を確認する必要性は実装と後続修正から分かります。

## 7. Remora: 実DSH E2Eでも計測していないUIは残った例

[v0.1.0](https://github.com/Aero123421/dsh-remora/releases/tag/v0.1.0)は10-12 16:21:06公開、[Release run](https://github.com/Aero123421/dsh-remora/actions/runs/38276257015)は成功しました。実DSH E2E、plugin tarball、CLIのbuild・版確認を含みます。

[PR #3](https://github.com/Aero123421/dsh-remora/pull/3)は16:52:39作成、16:56:57 mergeです。「権限」の選択枠が隣の「範囲」に重なる問題と、権限カードの幅を修正しました。公式Tabsの等幅前提と、日本語で異なる長さになるタブを組み合わせた問題です。

unit件数は285のまま、E2Eは41から43へ変わっています。この違いは品質点数ではなく、タブ・カードの幾何を観測するassertionが加わったことを示します。PRは旧配布版への回帰適用で幅の不一致を検出し、実DSHの日本語・英語、明暗、1280/960/600px、全tab、keyboardを確認したと報告しています。

この会話では利用者の画面から指摘されました。公開PRには利用者報告の投稿時刻がなく、公開から報告までの時間は計算していません。[v0.1.1](https://github.com/Aero123421/dsh-remora/releases/tag/v0.1.1)は17:01:17公開です。390pxで親DSHの左ナビが内容幅を圧迫する制約は残るため、任意のmobile幅を確認済みにしません。

不足したのは「E2E」という種類ではなく、利用者の症状に対応する観測でした。全tabの実button境界と選択背景、実内容幅でのgridをrelease前の関連確認へ置くことが有効です。

## 8. Glass UI: runnerの前提を直す仕事と製品を直す仕事

10-12の[初回manual E2E](https://github.com/Aero123421/dsh-glassui/actions/runs/38273765719)はplugin addのcode 127、pnpm不在で失敗しました。[診断annotationを追加した次run](https://github.com/Aero123421/dsh-glassui/actions/runs/38274086046)も同じ理由で失敗し、pnpm setupを加えた[次のE2E](https://github.com/Aero123421/dsh-glassui/actions/runs/38274359337)が成功しました。

plugin自体のnpm install成功から、DSHのplugin managerもnpmだけで動くとは推測できません。クリーンrunnerで宿主の導入まで持つ担当が、必要なtoolを準備します。診断を見やすくする変更と、失敗の原因を除く変更は分けて記録します。

別系列の[依存更新PR #1](https://github.com/Aero123421/dsh-glassui/pull/1)の[CI](https://github.com/Aero123421/dsh-glassui/actions/runs/38285330068)と[E2E](https://github.com/Aero123421/dsh-glassui/actions/runs/38285330030)は、TypeScript 7.0.2とtypescript-eslint 8.71.1のpeer条件不一致で`npm ci`が失敗しました。runtime試験まで到達していません。これは依存解決の残件で、UIのruntime回帰を示す結果ではありません。

## 9. Glass UI: 配布方法の追加がrelease担当の前提を変えた例

[PR #2](https://github.com/Aero123421/dsh-glassui/pull/2)は保存競合、解除、描画、UI、配布を修正し、10-12 17:59:24にmergeしました。GitHub指定の導入用distをGitへ含め、buildとの差分確認も加えています。

[Release run](https://github.com/Aero123421/dsh-glassui/actions/runs/38287926073)は成功し、[v0.1.0](https://github.com/Aero123421/dsh-glassui/releases/tag/v0.1.0)を18:04:07に公開しました。しかしcheckoutで存在する`dist/index.js`と`dist/client.js`へ、配布artifactも`dist/`にdownloadし、`dist/*`をuploadしたため、生JSまでassetになりました。[PR #3](https://github.com/Aero123421/dsh-glassui/pull/3)がこの経路を説明し、18:08:29に修正をmergeしています。

修正は公開用directoryを`release/`に分け、tarballとchecksumを明示して渡すものです。PR本文は不要assetの削除、公開tarballのchecksum一致、実DSHへの導入・Host/Client起動成功を報告しています。現在のassetsは2件で、不要JSの混入を現行状態として扱いません。

公開tagは#2のmerge SHA、現在mainは#3のmerge SHAです。tagは書き換えていません。workflow修正は次回の配布工程に効き、既存Releaseのasset修復とは別です。

原因の分析は、GitHub導入用生成物と、packして公開するfile集合の境界が重なったことです。package内のfile検査、checksum、来歴の確認は、Release全体に不要assetがないことを検査しません。build担当が「distがcheckoutに存在するようになる」とrelease担当へ渡し、公開対象一覧を照合する確認が、この追加修正を減らせます。

## 10. 更新機能: 配布後に接続先の識別を追加した例

更新機能追加後、Pi [#11](https://github.com/Aero123421/dsh-pi-login/pull/11)、Search [#4](https://github.com/Aero123421/dsh-search-providers/pull/4)、日本語パック [#4](https://github.com/Aero123421/dsh-japanese/pull/4)でprofile別の操作ID復元を修正しました。初期版の後にそれぞれ`0.5.1`、`0.3.1`、`0.2.1`で公開しています。

問題は、同じブラウザー・同じoriginから接続先profileを替えると、前の操作IDを新しいHostへ照合することでした。通信世代を更新する処理だけでは、ブラウザーの永続記録の所有先は変わりません。認証済みHostからprofile識別子を先に取得し、保存キーと導入要求をそのprofileに結び付ける修正が必要でした。

さらに、Hostの最新操作と古いClientの記録、receipt保存中の外部更新を照合しています。単一Clientの正常更新だけでは、元のIDの保持・復帰と、別Clientが導入した新版の維持を確認できません。[実装記録](../update-implementation.md)に検証範囲をまとめています。

横展開した処理では、各repoの保存キー・route・package名を読むだけでなく、同じoriginのprofile A→B→A、最初の応答喪失、遅れて届く古い要求まで受け入れ条件に含めます。コードの共有が、状態の所有者の共有を意味するとは扱いません。

## 11. PWA: 導入済み版と設定UIの反映がずれた例

更新後の利用者画面では、PWA `0.2.0`が標準詳細でRunningなのに、設定欄にPWAがありませんでした。隔離した実DSHで`0.1.0`を起動したまま`0.2.0`へ更新すると、ブラウザー再読み込みだけでは欄が出ず、Host再起動後に実行版と更新ボタンを確認できました。

原因はHostのClient metadataキャッシュで、旧版の「Client packageではない」判定も再起動まで残ります。ソースと操作順は[再起動の章](../update-and-restart.md)へ記録しています。利用者の画面を根拠に原因を断定せず、旧版からの更新とサーバー再起動を別環境で比較しました。

新規導入のE2Eと標準詳細の版表示は成功しても、この操作順を通らなければ見つかりません。Client entryを初めて追加するときは、既存利用者の更新経路と、どのプロセスを再起動するかを配布側へ渡します。これはDSHの読み込み仕様の確認と利用者案内で、プラグインが再起動機能を実装した事例ではありません。
