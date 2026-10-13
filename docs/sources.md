# 参照元と確認範囲

確認日は2026-10-13です。以下の公開コミット、修正PR、未完了Issueを参照しています。作業ディレクトリやブラウザーfixtureだけを、公開版の証拠にしないよう、参照を公開URLで残しています。最初のレビュー、更新Issue作成、更新実装後の確認は、それぞれの対象版を残しています。

## 確認したソース

この表は最初のレビューの確認版です。更新機能・干渉対策の追加調査で確認した新しい版は、末尾の「自作7プラグインの追加調査」から参照できます。

| 対象 | 確認版 | 固定したソース |
| --- | --- | --- |
| DeepSeek Harness | `0.2.1-alpha.2` | [d743267](https://github.com/deepseek-ai/deepseek-harness/tree/d743267388641bc76f17c45ce8b4c231aed1d32c) |
| Piログイン | `0.3.1` | [8302457](https://github.com/Aero123421/dsh-pi-login/tree/830245768a319f19ac461aa0d8716ea32baf020f) |
| 日本語化 | `0.1.1` | [c6bb537](https://github.com/Aero123421/dsh-japanese/tree/c6bb53790233c171f6854820f89e87205abf5b51) |
| PWA | `0.1.0` | [135828c](https://github.com/Aero123421/dsh-pwa/tree/135828c05e8fe5fc4af2fefdf891564c686638a9) |
| 検索プロバイダー | `0.2.0` | [ca7a1e4](https://github.com/Aero123421/dsh-search-providers/tree/ca7a1e484cd25e1812fc333c85b0185a40659e49) |
| Remora | `0.1.1` | [ed7e997](https://github.com/Aero123421/dsh-remora/tree/ed7e99736b0cc8e72a956722fb6fc72fda927239) |
| Glass UI | `0.1.0` | [b97fa77](https://github.com/Aero123421/dsh-glassui/tree/b97fa776424b209f72625f81327f7be3c559b6f7) |

DSHの固定コミットは、Piログイン・日本語化などの`upstream.json`と一致する基準版です。確認日に公開されているDSHの最新版という意味ではありません。

ソースの`main`先頭と、あるRelease tagの指すコミットは別の場合があります。例えばworkflowだけを修正したコミットと、既存の配布tarballの内容は区別して追います。

## 主な修正PR

| 対象 | PR | 扱った内容 |
| --- | --- | --- |
| Piログイン | [#3](https://github.com/Aero123421/dsh-pi-login/pull/3) | 再取得競合、Device Code期限 |
| Piログイン | [#5](https://github.com/Aero123421/dsh-pi-login/pull/5) | Fastを独立した候補として扱う |
| Piログイン | [#8](https://github.com/Aero123421/dsh-pi-login/pull/8) | GitHub指定の導入、生成物の一致 |
| 日本語化 | [#1](https://github.com/Aero123421/dsh-japanese/pull/1) | GitHub指定の導入、font同梱 |
| PWA | [#2](https://github.com/Aero123421/dsh-pwa/pull/2) | workspaceへの導入、CI、license |
| 検索プロバイダー | [#1](https://github.com/Aero123421/dsh-search-providers/pull/1) | FxTwitterの`x_search` |
| Remora | [#1](https://github.com/Aero123421/dsh-remora/pull/1) | 権限、再送、保存、停止など14件 |
| Remora | [#2](https://github.com/Aero123421/dsh-remora/pull/2) | 監査ログの保存待ち |
| Remora | [#3](https://github.com/Aero123421/dsh-remora/pull/3) | タブ選択背景、設定panel幅 |
| Glass UI | [#2](https://github.com/Aero123421/dsh-glassui/pull/2) | 設定競合、解除、描画、UI、配布 |
| Glass UI | [#3](https://github.com/Aero123421/dsh-glassui/pull/3) | Release assetの出力先・公開対象 |

過去のPRの検証結果は、その変更と環境についての結果です。この文書の作成時に、すべてのpluginテストや実APIを再実行したことを意味しません。

## 未完了・未検証の扱い

| 項目 | 2026-10-13に確認した状態 |
| --- | --- |
| Piの動的model catalog | [Issue #6](https://github.com/Aero123421/dsh-pi-login/issues/6)は未完了 |
| 他pluginのprovider統合表示 | [Issue #7](https://github.com/Aero123421/dsh-pi-login/issues/7)は未完了 |
| Muse ContributorのMax | [Issue #4](https://github.com/Aero123421/dsh-pi-login/issues/4)で実API調査中 |
| 有料検索provider | mockによるadapter確認と、実API確認を区別する |
| FxTwitter | 投稿URL取得の実通信確認と、キーワード検索の利用可否を区別する |
| Remoraの外部配備・OS別keychain | 実行した環境以外へ検証結果を広げない |
| 小さい画面 | pluginのresponsive対応と、親DSHのlayout制約を区別する |
| 独自更新ボタン | 自作7pluginに実装・公開済み。[設計章](update-button.md)は実装指針で、単独の共通updater packageの配布ではない |

## DSH本体で参照した境界

- [install-spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/install-spec.ts): 入力形式、path、記録する依存指定。
- [types.ts](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/types.ts): bundle、変更結果、検査、導入オプション。
- [index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/index.ts): 導入、取消、進行中要求の照合。
- [manager-store.ts](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/client/ui-plugin-manager/src/client/manager-store.ts): 標準画面の更新条件と結果処理。
- [plugin manager README](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/README.md): profile、権限、package差し替え、保存復元の範囲。

## 外部仕様

- [GitHub REST API: Releases](https://docs.github.com/en/rest/releases/releases#get-the-latest-release): 公開Releaseの取得。取得したReleaseをpluginの互換版と判断する処理は別に必要です。
- [Semantic Versioning 2.0.0](https://semver.org/): 版の形式と順序。

外部仕様は確認日に参照しています。固定コミットと違い、リンク先の説明が将来変わる可能性があります。

## 公式・外部プラグインの追加調査

[調査一覧](ecosystem/README.md)に外部12リポジトリの固定コミット、GitHub stars、npm downloadsを記録しています。公式は同じDSHコミットから、任意bundle 11種類と、後から導入するCodex・Claude Code連携を整理しています。

追加調査では、更新・認証・model catalog・context注入・UI登録・processとprofileの所有を、主要な実行経路まで読みました。各章のfileリンクは、調べたコミットへ固定しています。

公開npm配布物8種類の整合性・entry、ソースとnpm metadataのpeer条件、I/Oを伴わないqueue helperを確認しました。[配布物と互換性の結果](ecosystem/package-checks.md)には、実施した確認と、実DSH・実APIなど未実施の範囲を分けて記録しています。

## Issueから解決までの追加調査

[自作の履歴](workflow/own-cases.md)では上の修正PRに加え、Issue、commit列、Actions run/job、公開時刻、現在のasset一覧を照合しています。[外部の履歴](workflow/ecosystem-cases.md)はdsh-market #497/#824/#788、TUI #60/#183、modlens #34と関連する公式discussionを追っています。

一次ソースは各事例の該当箇所にリンクしています。公開記録の事実、作者の検証報告、分析上の推論を区別し、取得件数と時刻の扱いは[調査方法](workflow/evidence.md)へまとめています。

## 自作7プラグインの追加調査

2026-10-13 14:00 JSTに公開metadataとソースを追加取得しました。[自作プラグイン一覧](own-plugins.md)に7つの固定SHA、package版、Releaseと更新Issueを記載しています。Piは`0.4.1`、Glass UIは`0.1.2`を改めて確認し、CF `0.1.0-alpha.3`を追加しました。

[搭載する機能](recommended-features.md)と[干渉対策](plugin-coexistence.md)は、その固定ソースの主要処理から比較した分析です。登録・解除、CSS、辞書、tool、credential、設定競合、接続の寿命、proxyと管理権限、processとクラウド資源の所有を扱っています。実装から確認したことと、提案・今後の併用確認を区別しています。

この追加調査ではruntimeを変更・起動していません。新規文書のMarkdown・内部リンク・引用先を検証し、Issueには実装時に必要な確認項目を記載しています。過去のReleaseのテスト結果を、今回の全組み合わせの検証結果として扱いません。

## 更新実装後と後続Releaseの確認

2026-10-13 12:22 UTCから、7repositoryの最新公開Release・asset名・prerelease状態、mainの固定SHAとpackage、公開タグのSHA、更新Issueのclosed状態と実装PRを取得しました。現在版と公開ソースの対応は[一覧](own-plugins.md)へまとめています。CFはソースのみのプレリリース、ほかの6つにはplugin用tgzと`SHA256SUMS`があります。

[実装記録](update-implementation.md)は、更新機能追加時の実行結果と、その後のPWA `0.3.0`・Glass UI `0.2.2`の公開報告を分けています。PWA・Glass UIの後続版は固定したREADME、ReleaseノートとPRを照合し、今回すべてのruntime試験を再実行したとは記載しません。Piの動的catalogと統合表示のIssue #6/#7は、再取得時もopenです。

PWA `0.1.0`→`0.2.0`の設定欄欠落は隔離した実DSHで別途再現しました。ブラウザー再読み込みでは欠落が残り、Host再起動後に実行版と更新ボタンを確認しています。[再起動の章](update-and-restart.md)には確認順序と、基準DSHのClient metadataキャッシュ・installer・終了APIへの固定リンクがあります。この結果は利用者実機の再起動や最新7版の共存確認ではありません。
