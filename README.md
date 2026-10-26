# DSHプラグインの開発・レビュー記録

DeepSeek Harness向けプラグインの開発・レビューで得た知見と、独立したプラグインリポジトリへ持ち込めるSkillsをまとめています。実行プラグイン本体は含みません。

## 2026-10-15時点の固定ソース基準

**このalpha.3資料は2026-10-15時点の歴史的なソース確認記録であり、最新基準ではありません。** 公開版と開発中のmasterを分けた当時の記録です。対象版がalpha.3以降の場合は、その公開Releaseと所属packageのソースを確認してください。まず[alpha.3の固定基準記録](docs/current-baseline.md)を読み、変更する領域の資料へ進んでください。

今回、更新・HMR、Remoteのprincipal/Peer、profile別の資格情報、Session/projection、解除順序、responsive UIを再確認しました。[本家・外部の開発と不具合の分析](docs/workflow/upstream-2026-10-15.md)には、未mergeのPR、追加修正、mockの限界、障害中の性能をどう開発手順へ反映するかを記録しています。

これは全プラグインのalpha.3実行互換性を認定する更新ではありません。今回のruntime・実OAuth・実OS別UI・自作7件共存試験は未実施です。確認した公開ソースと限界は[基準記録](.agents/baseline.json)と[外部事例の記録](data/upstream-refresh-2026-10-15.json)を参照してください。

## 読む場所

| やりたいこと | 文書 |
| --- | --- |
| alpha.3 (2026-10-15)で確認した契約を見る | [固定基準記録](docs/current-baseline.md) |
| 開発エージェントの指示とSkillsを用意する | [.agentsの使い方・22 Skills](.agents/README.md) |
| 上流と人気プラグインの変化を追う | [2026-10-15の分析と更新手順](docs/workflow/upstream-2026-10-15.md) |
| レビューを始める | [レビューの進め方](docs/review.md) |
| 過去の不具合と修正を調べる | [よくあった問題](docs/common-problems.md)・[Issueから解決まで](docs/workflow/README.md) |
| 導入・公開物を確認する | [インストール](docs/installation.md)・[配布とリリース](docs/release.md) |
| 更新を設計する | [更新の種類](docs/updates.md)・[更新ボタン](docs/update-button.md)・[反映と再起動](docs/update-and-restart.md) |
| UI・認証・tool・保存を拡張する | [UI](docs/ui.md)・[拡張点](docs/integration.md)・[権限と保存](docs/security-and-storage.md) |
| 他pluginとの併用を設計する | [干渉を避ける](docs/plugin-coexistence.md)・[機能を選ぶ](docs/recommended-features.md) |
| 検証と公開を記録する | [テスト](docs/testing.md)・[レビュー報告](templates/review-report.md)・[公開確認](templates/release-checklist.md)・[解決記録](templates/issue-resolution.md) |

2026-10-13を基準にした各章は、当時の実例と一般的な設計観点を残したものです。APIや挙動が競合する場合は、alpha.3の固定記録だけで判断せず、対象版の所有packageを確認します。更新・再起動の旧ガイドは[更新ボタンalpha.2版](docs/update-button-alpha2.md)・[再起動alpha.2版](docs/update-and-restart-alpha2.md)へ、内容を変えずに分離しました。

## この文書の前提

自作の日本語化、Piログイン、PWA、検索プロバイダー、Remora、Glass UI、CFを[自作一覧](docs/own-plugins.md)と[更新実装の記録](docs/update-implementation.md)にまとめています。記載版と試験は2026-10-13の確認時点に属し、現在の各repoの最新版やalpha.3対応を意味しません。

[外部プラグインの調査](docs/ecosystem/README.md)は、最初の12件の比較と、その後の31プロジェクト・EverOS adapter移転先を合わせた[32リポジトリの深掘り](docs/ecosystem/deep-topic.md)です。[横断比較](docs/ecosystem/deep-patterns.md)、topic検索上位1,000件の条件、15 packageの配布物検査も当時の固定記録として残しています。スター数は採用実績や品質の認定ではありません。

2026-10-13のPWA `0.1.0`→`0.2.0`更新でHost再起動が必要だった再現、初期7件の同時起動、各PRの検証報告を、今回の再試験結果へ置き換えていません。固定ソースの一覧は[参照元](docs/sources.md)にあります。

## 用語

| 用語 | 意味 |
| --- | --- |
| Host | 処理・保存・外部通信を行うDSH側。Webではサーバーprocess |
| Client | ブラウザーやアプリで画面を表示する側 |
| profile | 起動するpluginと設定の構成 |
| bundle | DSHへの登録patchを持つ配布package |
| HMR | 実行中の構成や対象moduleを再構成する仕組み |
| wire model | APIへ送るmodel ID。画面の表示名・選択IDとは区別 |

## 最初に確認すること

1. 対象DSH・plugin・profile・配布物を固定し、公開経路と実行中の版を区別する。
2. 古い非同期結果、権限変更、取消、自己解除が新しい状態を壊さないか確認する。
3. 受け付け済み処理の最終保存が終わる前に、依存service・listenerを閉じない。
4. 更新は候補・削除・導入・実行版・Client反映を分け、失敗後の状態も記録する。
5. 変更に合う検証を選び、作者報告・コード読解・今回の実行・未確認を分ける。

## 文書とSkillsの検査

完全なcheckoutでは `python3 scripts/validate_docs.py` でJSON、Skill frontmatter、同梱LICENSE、相対リンクとローカル見出しを検査できます。`python3 -m unittest discover -s scripts -p 'test_validate_docs.py'` は検査器自体の小さいfixtureを確認します。これらは文書の形式検査で、記述されたAPIの動作やpluginの実行試験を代替しません。
