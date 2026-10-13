# DSHプラグインの開発・レビュー記録

DeepSeek Harness向けに作ったプラグインのレビューで見つかった問題と、インストール・更新・配布の手順をまとめています。次のプラグインを作るときや、既存の実装を見直すときに使うための文書です。

自作の日本語化、Piログイン、PWA、検索プロバイダー、Remora、Glass UI、CFに加え、公式bundleと外部12リポジトリの実装も調べています。確認したコミットと修正PRは[参照元](docs/sources.md)にあります。

## 読む場所

| やりたいこと | 文書 |
| --- | --- |
| レビューを始める | [レビューの進め方](docs/review.md) |
| Issueから公開・利用者確認までの詰まりを調べる | [解決フローの分析](docs/workflow/README.md) |
| 過去の不具合を調べる | [よくあった問題と修正例](docs/common-problems.md) |
| 公式・人気の外部プラグインを比較する | [外部プラグインの実装調査](docs/ecosystem/README.md) |
| UIやCLIから導入できるようにする | [インストールとパッケージ構成](docs/installation.md) |
| 更新の種類と追従方針を決める | [プラグイン・モデル・DSHの更新](docs/updates.md) |
| 設定画面に更新ボタンを作る | [更新ボタンの設計](docs/update-button.md) |
| 自作7プラグインの公開版・更新操作・実装例を確認する | [自作プラグイン一覧](docs/own-plugins.md) |
| 更新機能の修正と検証結果を調べる | [更新機能の実装記録](docs/update-implementation.md) |
| 更新後に設定欄が出ない・旧版のまま動く | [更新後の反映と再起動](docs/update-and-restart.md) |
| 次のプラグインに持たせる機能を決める | [搭載する機能](docs/recommended-features.md) |
| 他プラグインとの併用を設計する | [干渉を避ける実装と確認項目](docs/plugin-coexistence.md) |
| DSHに合う設定画面を作る | [UI・日本語化・フォント](docs/ui.md) |
| 認証、モデル、検索ツールを追加する | [プロバイダーとツールの拡張](docs/integration.md) |
| Hostの権限や保存処理を見直す | [権限・保存・外部通信](docs/security-and-storage.md) |
| テストとCIを組む | [テストとCI](docs/testing.md) |
| GitHubで公開する | [配布とリリース](docs/release.md) |
| レビュー結果を書き残す | [レビュー報告テンプレート](templates/review-report.md) |
| リリース前の確認を記録する | [リリース確認テンプレート](templates/release-checklist.md) |

## 用語

| 用語 | この文書での意味 |
| --- | --- |
| Host | DSHの処理・保存・外部通信を実行する側。Webではサーバー側のprocess |
| Client | ブラウザーやアプリ内で画面を表示する側 |
| profile | 起動するプラグインと設定の構成。変更はそのprofileを使うSessionに影響する |
| bundle | DSHへの登録patchを含み、管理画面から導入・有効化できるpackage |
| HMR | 実行中の構成を再読み込みし、プラグインを解除・登録する仕組み |
| wire model | APIや通信に使うmodel ID。表示名・画面の選択IDとは区別する |

## 最初に確認すること

1. 配布するGitHubタグや`.tgz`を、作業用リポジトリとは別のDSH環境にインストールする。
2. 設定の再取得・保存・接続切り替えで、古い結果が新しい状態を上書きしないか確認する。
3. 無効化・アンインストール後に、登録したツール、イベント、タイマー、通信、CSSが残らないか確認する。
4. 更新後の保存設定、資格情報、ON/OFF状態と、実際に動いている版を確認する。
5. 実際のDSH画面で、設定パネルの狭い幅、日本語、キーボード操作を確認する。

## この文書の前提

2026-10-13時点の公開リポジトリと修正PRを調べています。DSH本体のAPIは`0.2.1-alpha.2`、コミット`d743267388641bc76f17c45ce8b4c231aed1d32c`を基準にしています。新しいDSHで同じAPIや動作が続くことを保証するものではありません。

過去に修正した事例、確認版の仕様、今後の設計案を区別して書いています。更新ボタンの章には、既存実装をそのままコピーすると残る問題も含めています。文書中の「推奨」「設計案」は、このリポジトリで実装済みの機能を意味しません。

外部pluginは主要処理のソース比較と、公開npm配布物8種類の確認を行いました。版条件の照合とqueue helperの単独検証は[確認結果](docs/ecosystem/package-checks.md)にあります。全pluginの実起動・実APIを確認したものではありません。

Issueから解決までの分析では、自作6repositoryのIssue・PR・CI・Releaseと、外部6事例・公式discussionを追いました。時刻と解決範囲、追加修正の理由は[フローの分析](docs/workflow/README.md)、取得範囲と判断の限界は[調査方法](docs/workflow/evidence.md)に記録しています。

自作7repositoryには更新機能が入り、対象Issueはすべてclosedです。2026-10-13 12:22 UTCから公開Release、タグ、mainのpackage、IssueとPRを照合しました。[一覧](docs/own-plugins.md)に現在の公開版と実装例、[実装記録](docs/update-implementation.md)に修正・検証範囲とDSH/pnpmの導入条件があります。PWA `0.3.0`のモバイル表示、Glass UI `0.2.2`の設定・描画変更も反映しています。

PWA `0.1.0`から`0.2.0`への更新では、導入版が新しくなってもブラウザーの再読み込みだけでは設定欄が出ないことを再現しました。[更新後の反映と再起動](docs/update-and-restart.md)に、Hostのmetadataキャッシュ、導入版と実行版の違い、確認手順をまとめています。最新のPWA・Glass UIを含む7件の共存試験を今回やり直したわけではありません。

新しい問題を追加するときは、発生条件、影響、修正、失敗を再現する確認方法、PRまたはコミットを残してください。未検証のAPI接続やOSを「対応済み」に含めないでください。
