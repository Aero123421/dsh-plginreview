# 人気プラグインとDSH接続実装の深掘り

2026-10-13に、[dsh-pluginトピック](https://github.com/topics/dsh-plugin)の上位候補から、人気プラグインと周辺実装を読み直しました。31プロジェクトと、EverOS adapterの移転先を合わせた32リポジトリをSHA固定し、主要な実行・保存・解除・更新の経路と、Issue/PRの修正先を追っています。分析はGPT-6.1-solのmediumで分担しました。

前回の12件の概説より深く、利用者の操作がどの状態を変え、何を確認すれば反映済みと言えるかを調べています。大きなアプリの接続leaf、native bundle、preset、カタログを混ぜて品質ランキングにはしていません。範囲・人気指標・検索上限は[調査条件](topic-method.md)にあります。

## 読む場所

| 目的 | 分析章 |
| --- | --- |
| 更新ボタン、market、Sidebar、集約bundle、TUIの状態を追う | [UI・更新・Host](deep-ui-updates.md) |
| OAuth、model/account、routing、Agent Teams、IMの境界を追う | [認証・モデル・エージェント](deep-providers-agents.md) |
| ログイン済みbrowser、画像evidence、記憶、別アプリ連携を追う | [ブラウザー・画像・記憶](deep-browser-memory.md) |
| 別Desktopのruntime更新・再起動と、壁紙のprocess/CSS解除を比較する | [Desktop・壁紙](deep-desktop-theme.md) |
| 遠隔Web接続と、カタログの検証表示・掲載条件を調べる | [Pocket・Radar・Shop](deep-access-catalogs.md) |
| 画像ツールの履歴と、研究presetのevidenceを比較する | [Vision・研究preset](deep-vision-research.md) |
| 自作プラグインへ持ち帰る実装を選ぶ | [横断比較と確認項目](deep-patterns.md) |
| 実際に取得したnpm配布物と、DSH peer条件を確認する | [15 packageの配布物確認](deep-package-checks.md) |

## 対象と固定ソース

スター数は2026-10-13 13:10 UTCのtopic検索結果です。本体全体の値で、DSH adapterの利用者数ではありません。SHAはその後に取得したソースです。再取得可能な対応表は[公開snapshot一覧](../../data/topic-source-snapshots-2026-10-13.json)にあります。

| 分析対象 | stars | 主に追った入口 |
| --- | ---: | --- |
| nexu-io/open-design | 100,892 | 別アプリとDSH profile/runtimeのhandshake |
| volcengine/OpenViking | 39,813 | DSH memory leaf、stdio MCP、HTTP server、pending write |
| anywhere-labs/dsh-desktop | 30,668 | edition/runtime/profile、renderer回復、製品更新 |
| dataelement/dsh-desktop | 13,650 | desired状態とgeneration、Host起動・停止・更新 |
| Ebony-Vinyl/dsh-our-free-model | 13,445 | provider・channel pack、署名付き独自更新 |
| EverMind-AI/EverOS | 13,411 | adapterの移転、recall/capture/flush |
| MemTensor/MemOS | 11,847 | local adapter、Host model、promptと記憶 |
| Tencent/BrowserSkill | 8,786 | CLI・extension・DSH runner、queueと所有journal |
| zhu1090093659/dsh-web | 8,694 | aggregate、fault shell、設定・package変更 |
| yjh051108/dsh-routing-suite | 7,021 | runtime injector、routingと子Session |
| dsh-market/dsh-market | 6,366 | candidate、mutation、operationとClient queue |
| YuJunZhiXue/dsh-purge | 5,166 | provider wrapperによるモデル指示の変更 |
| MeteorNOX/DeepSeek-Balance-Whale-Widget | 4,681 | 小さいoverlay、残高取得、page寿命 |
| ccch1mneyyy/dsh-TUI | 4,536 | terminal query・ACK・inputとbackend/profile |
| liustack/modlens | 4,231 | image wrapper、agent scope、wire evidence |
| omdsh-dev/DSH-better-sidebar | 4,142 | tab/viewer registry、file権限、terminal資源 |
| xiaobright/dsh-anchored-standard | 3,760 | 二段階preset、gateのlog/tool副作用 |
| dsh-tauri/deepseek-harness-desktop | 3,038 | child handle・PID、port・health、runtime取得 |
| zilliztech/memsearch | 2,741 | Markdown capture、index、maintenance lock |
| Small-tailqwq/dsh-deep-whale | 2,565 | skin manager、共有body/CSSの復元 |
| NanmiCoder/dsh-agent-teams | 2,092 | 親子agentのmodel・permission・durable state |
| bowenliang123/dsh-context | 2,069 | projection・cold read・contextの観測値 |
| xmanrui/dsh-im | 1,946 | bot policy、Session対応、interaction、mirror retry |
| shaobeichen/dsh-pocket | 1,714 | PIN付きWeb入口、tunnel、子processと設定 |
| AdamPlatin123/dsh-plugin-radar | 1,471 | カタログ生成、runtime verdict、来歴とfreshness |
| elysia395/dsh-wallpaper-engine | 1,161 | iframe/WebGL/ffmpeg、upload tokenと解除 |
| ysr666/dsh-vision-router | 1,148 | 画像履歴、vision provider、fallback |
| LivXue/dsh-plugin-shop | 1,011 | community registry、掲載gate、plugin installer |
| Clearailhc/clearai-dsh | 986 | evidence ledger、別モデル評価、preset/UI |
| Anionex/dsh-vision-toolkit | 887 | Session別durable evidence、CLI・tool出力 |
| V1ki/dsh-plugin-subscriptions | 455 | OAuth lease、account固定、model catalog |
| EverMind-AI/plugins | — | EverOSの現在のDSH adapter。移転先として別SHAを固定 |

一覧の順位はstarsの降順です。Subscriptionsのような比較用選定もあり、「この順に入れるべき」という推奨順ではありません。各章の表にはmanifest版と導入するleafを残しています。

## ソース・配布・実行を結ぶ

1. topicとカタログで候補を発見する。
2. 実bundle・leaf・接続方式と、固定ソースを確認する。
3. 呼び出し先、保存先、登録解除、更新後の再接続を追う。
4. 関連Issueから修正PR・merge・配布版・残件を照合する。
5. 公開物を取得し、宣言と中身を確認する。
6. 実起動・実APIが必要な条件を、未確認として残す。

今回のnpm 15 packageはintegrity・manifest・具体entry・patchを確認しました。うち5つの公開宣言は基準DSH `0.2.1-alpha.2`とpeer条件が一致しません。これは人気指標とは独立した導入条件です。[配布物確認](deep-package-checks.md)に対象版と検査範囲があります。

純粋helperの限定再現は各分析章に記録しています。外部plugin全体の導入・実OAuth・課金API・OS別画面・本番クラウドの動作を全件確認したものではありません。公開PRの試験件数やカタログのbadgeを、今回の実行結果へ加算していません。
