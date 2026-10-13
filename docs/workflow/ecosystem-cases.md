# 外部pluginと公式への提案

公開Issueの症状、原因の絞り込み、修正、確認、配布を追った6例です。時刻はUTC、日付は2026年です。作者のテスト報告とActionsの成否を分け、利用者の更新後確認が見つからない場合は補っていません。[調査方法](evidence.md)を参照してください。

## 1. dsh-market #497: 更新できる状態の所有者が違った

[Issue #497](https://github.com/dsh-market/dsh-market/issues/497)は09-03に作成されました。自己ビルドLinux Desktop、market 1.38.1で、10個中8個のpluginに更新が出ない報告です。marketは`link:`を開発checkoutと見ていましたが、Desktopは配布済みpackageを`.generations/live/`へ置く構成でした。

調査を進めた[質問と回答](https://github.com/dsh-market/dsh-market/issues/497#issuecomment-5542710254)は、profileでpackageを更新した後にhostが何を読むかです。示されたhostコードは`desired.json`から名前とdirectoryのmapを作っていました。profileの依存だけ変えても、実行するgenerationを変えられない構成でした。

[PR #532](https://github.com/dsh-market/dsh-market/pull/532)はgenerationを別の取得元として扱い、current/latestの報告に留め、更新ボタンとbatch選入を出さない修正です。普通の開発`link:`は維持しています。更新判定、UI、settings、routeのテストが変わり、merge SHAのLinux/Windowsと複数hostのCIは成功しています。

09-13 02:47:40 merge、1秒後にIssue close、03:21:27に[v1.46.0](https://github.com/dsh-market/dsh-market/releases/tag/v1.46.0)が#532を載せて公開されました。約9日の暦時間は確認できますが、待機・調査・実装の内訳は不明です。利用者が更新後の端末で確認した公開追認も見つかりません。

**詰まる条件**は、依存指定を変更できる側と、次回起動で使う状態を変更できる側が異なることです。hostがprofileを読み戻す証拠があれば、この制限は不要です。先に更新の所有者を確かめると、権限のない更新ボタンを作る手戻りを減らせます。

## 2. dsh-market #824: 表示用の判定が実行条件にも使われていた

[Issue #824](https://github.com/dsh-market/dsh-market/issues/824)は、floating Gitのpackage版が2.0.0のままでもbranch HEADが進むたびに「新バージョン」と出る問題です。plugin独自updaterとmarketで「最新」の意味が違っていました。

[仕様の確認](https://github.com/dsh-market/dsh-market/issues/824#issuecomment-6103998107)では、`updateAvailable`がbatch updateの選入条件にも使われると分かりました。文言だけ直しても、未発版commitの導入は続きます。

[PR #829](https://github.com/dsh-market/dsh-market/pull/829)はfloating GitHub取得についてpackage版のsemver上昇を使い、判定不能ならcommit比較へ戻す修正です。明示refはcommit比較を維持し、monorepo subpathやraw取得経路も扱っています。PRは関連56testの成功を報告し、merge SHAのLinux/Windows、複数host、pnpm互換のCIも成功しています。PR初期本文では別のclient test解析失敗が記載されており、関連test成功と当初の全体成功は別でした。

10-11 14:27:36 merge、14:34:08に[v1.66.17](https://github.com/dsh-market/dsh-market/releases/tag/v1.66.17)公開。未発版commitを実行対象にせず見せる変更は[PR #839](https://github.com/dsh-market/dsh-market/pull/839)、[v1.66.18](https://github.com/dsh-market/dsh-market/releases/tag/v1.66.18)へ分かれています。

**詰まる条件**は、発版、commit前進、表示、実行を一つのbooleanにまとめることです。この修正はpackage版が発版を示すという契約に依存します。版を上げないrepoや取得不能なmetadataへ一律に当てはめず、判定不能を保持します。仕様の修正と補助表示を分けた点も参考になります。

## 3. dsh-market #788: 詳細なログでも原因仮説が正しいとは限らない

[Issue #788](https://github.com/dsh-market/dsh-market/issues/788)はWindows 11 official Desktop、market 1.66.7でのpending、off/fiber、no-entry、patch縮小の報告です。名前照合不足や60秒再試行が原因候補として挙がりました。

[maintainerの訂正](https://github.com/dsh-market/dsh-market/issues/788#issuecomment-5981468794)は、entryが一致したことと、updateが成功したことを分けています。marketにその60秒timerはなく、同じpendingの再呼出しはpatch writerへ届かないため、報告されたfile縮小をこの経路の結果とは認めていません。

[b561a53](https://github.com/dsh-market/dsh-market/tree/b561a53886ad875925082ef99fd9474b82fcd6c3)ではmatchedとlandedを別判定にし、成功時だけoff/onをログに出し、同じpendingを新しい失敗として繰り返さない修正が入りました。旧コードで失敗する3用例と正常ログの用例があります。commitはfull suite/typecheck成功を報告していますが、この経路の独立実行ログや修正PRは確認できません。

10-05の[v1.66.9](https://github.com/dsh-market/dsh-market/releases/tag/v1.66.9)で診断修正を配布し、Issueは10-08にcloseです。[修正報告](https://github.com/dsh-market/dsh-market/issues/788#issuecomment-5999160968)が示す範囲はログです。pending処理の終了、失われた設定の復元、縮小原因の確定まで直した証拠にはしません。また、このIssueの証拠不足から現行実装の全経路が未解決だとも判断しません。

**詰まる条件**は、`matched / attempted / settled / persisted`を曖昧な成功表示でまとめ、報告の仮説をそのまま修正理由にすることです。原因を確かめるには、該当writeのevent、backup時刻、変わったfileを結ぶ証拠が必要です。ログ改善を根治としてclose記録へ書くと、残る調査が見えなくなります。

## 4. TUI #60: pnpm版の問題に見えて、解決の起点が問題だった

[Issue #60](https://github.com/ccch1mneyyy/dsh-TUI/issues/60)はpnpm 9.15.9で起動後すぐ終了する報告です。初期返信はpnpm更新、報告中のAI診断は直接依存の追加を提案していました。

[PR #75](https://github.com/ccch1mneyyy/dsh-TUI/pull/75)の調査では依存宣言自体は既にありました。Loaderがprofileを起点にbare nameを解決し、isolated pnpmではpluginの依存がprofileへhoistされないことが問題でした。npmやhoisted layoutでの成功は、この条件を否定する証拠になりません。

own-packageのsubpathからre-exportし、patchをそのentryへ向け、実package位置から依存を解決する修正です。PRはfresh profileとtarball、pnpm 9でbare import失敗・subpath import成功、buildと回帰確認を報告しています。08-14 13:40:19 merge、2秒後にIssue closeでした。

merge SHAのcheck-runsは取得時に空でした。取得したRelease 100件から、この修正の最初の発版境界を確定できなかったため、未公開とも公開済みとも断定しません。

**詰まる条件**は、依存が「存在する」ことだけ見て、誰がどのdirectoryから解決するかを見ないことです。依存追加やversion floorの変更前に、利用者のisolated layoutを再現します。hostにplugin-local解決の保証があれば、この回避は不要です。

## 5. TUI #183: 緩和を配ってもregistryから旧版が戻る

[Issue #183](https://github.com/ccch1mneyyy/dsh-TUI/issues/183)はTUI v0.7.0、macOS ARM64、DSH rc.6で`tuiWorkspaces`待機が続く報告です。export file自体はありました。

[PR #194](https://github.com/ccch1mneyyy/dsh-TUI/pull/194)はglobal launcher側の古いbundle patchと、profile側の新しいmoduleを読む不一致を原因としています。新codeのhard injectを外してlocal runtimeへ縮小する経路と、新patch・旧moduleの危険な組合せをlauncherで拒否する経路を分けました。

PRは両方向の隔離profile E2E、launcher assertions、build/smokeを報告し、merge SHAのbuild checkは成功です。08-16 09:54:41 merge、10:22:44に[v0.7.2](https://github.com/ccch1mneyyy/dsh-TUI/releases/tag/v0.7.2)で#194を明示しています。

その後の[comment](https://github.com/ccch1mneyyy/dsh-TUI/issues/183#issuecomment-5323368240)はregistry mirrorの古いlatestから0.7.0〜0.7.1が再導入された再発を記録します。[PR #315](https://github.com/ccch1mneyyy/dsh-TUI/pull/315)は危険版の拒否、導入後の実package版の確認、registry対照を追加し、[v0.8.1](https://github.com/ccch1mneyyy/dsh-TUI/releases/tag/v0.8.1)を08-18 03:50:01に公開しました。#315のmerge SHAではbuild成功と[npm jobの失敗](https://github.com/ccch1mneyyy/dsh-TUI/actions/runs/32096006358/job/95587375958)が並んでいます。このjobは依存のinstallで失敗し、compile以降とpublishはskipです。GitHub Release公開はnpm publish成功の証明ではありません。

関連する[公式discussion #2348](https://github.com/deepseek-ai/deepseek-harness/discussions/2348)は08-16、同じ構成のpatch・main・subpathを一つのresolved package pathへ揃える提案です。取得時にcommentはなく、根治PR・配布の証拠も得られませんでした。返信の不在から内部作業の有無は判断しません。

**詰まる条件**は、host、plugin、launcher、registryがそれぞれ異なる版を選べることです。plugin側のfallbackとinstaller guardは緩和、hostの解決方式変更は構造的な修正です。起動時のpatchとmoduleのrealpath・版、導入後の実package版を確認し、改善が届く範囲を分けます。

## 6. modlens #34: register成功でもmodelから見えなかった

[Issue #34](https://github.com/liustack/modlens/issues/34)はDSH rc.6、modlens 3.16.1のtool問題です。先行修正は同じ層のduplicate exceptionで改名していましたが、scoped host toolがglobal plugin toolを遮蔽する場合はexceptionがありません。登録は成功しても、model-visible listに目的のtoolが出ませんでした。

[33dea33](https://github.com/liustack/modlens/tree/33dea3311be51408de876621f83b1d1bfb39120b)でdefaultを`modlens_read_image`に変え、exception依存のfallbackを削除しました。PR経由の証拠は見つかりません。[v3.16.3](https://github.com/liustack/modlens/releases/tag/v3.16.3)は08-14 16:23:07公開、16:25:00にIssue closeです。

[説明の訂正](https://github.com/liustack/modlens/issues/34#issuecomment-5295658439)では「scopeの検出が不可能」「誰にもshadowされない」という初期説明を撤回しています。公開APIで検出は可能だが、複雑な検出より名前を分ける方が小さい修正です。古い名前へ戻すworkaround文書も訂正しています。

**詰まる条件**は、apply時のregister/get成功を、実agent scopeに送るschemaとdispatchの成功へ広げることです。modelへ渡るtool一覧と実呼出しを確認します。固有名でも同名scoped toolによる遮蔽はあり得ます。また、既存toolを意図的に置換するpluginは、その拡張契約を確認する別の設計です。

## 外部例を取り込む条件

| 調べる境界 | 先に必要な証拠 |
| --- | --- |
| 更新の所有者 | 次回起動でhostが読む状態と、それを誰が変更できるか |
| 依存の解決 | patch・module・第三者依存の起点とrealpath |
| toolの公開 | 実agent scopeのschemaとdispatch |
| 成功ログ | 照合、実行、完了、保存のどこまで進んだか |
| 配布先 | GitHub・npm・mirrorそれぞれの公開結果と、実際に取った版 |

詳細なIssueでも因果を取り違えることがあり、早いcloseにも再発がありました。成功したCIと失敗した配布jobが並ぶ例もあります。公式・人気という分類に加え、自分の修正が通る経路と同じ条件かを確かめます。
