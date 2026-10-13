# 自作プラグインの公開版と更新実装

2026-10-13 12:22 UTCから、7つの公開Release、タグが指すコミット、mainのpackage、更新Issueと実装PRを照合しました。下表のmainと最新公開タグは同じコミットです。CFはプレリリースです。

## 現在の公開版

| プラグイン | 公開版 / 確認コミット | 更新操作の場所 | 更新Issue / 実装PR |
| --- | --- | --- | --- |
| [Piログイン](https://github.com/Aero123421/dsh-pi-login) | [v0.5.1](https://github.com/Aero123421/dsh-pi-login/releases/tag/v0.5.1) / [a8002c2](https://github.com/Aero123421/dsh-pi-login/tree/a8002c2355cb31fab680ff220b7a985010ec4f9e) | 設定 → モデルの共通フッター | [#9](https://github.com/Aero123421/dsh-pi-login/issues/9) closed / [#10](https://github.com/Aero123421/dsh-pi-login/pull/10)、[#11](https://github.com/Aero123421/dsh-pi-login/pull/11) |
| [日本語パック](https://github.com/Aero123421/dsh-japanese) | [v0.2.1](https://github.com/Aero123421/dsh-japanese/releases/tag/v0.2.1) / [97b4ce3](https://github.com/Aero123421/dsh-japanese/tree/97b4ce33f4fa696a497a6630180681565983a5fc) | 設定 → 日本語パック | [#2](https://github.com/Aero123421/dsh-japanese/issues/2) closed / [#3](https://github.com/Aero123421/dsh-japanese/pull/3)、[#4](https://github.com/Aero123421/dsh-japanese/pull/4) |
| [PWA・モバイル](https://github.com/Aero123421/dsh-pwa) | [v0.3.0](https://github.com/Aero123421/dsh-pwa/releases/tag/v0.3.0) / [e2692d0](https://github.com/Aero123421/dsh-pwa/tree/e2692d04699294c31b53e54224bc05d81e2b205e) | 設定 → PWA・モバイル（英語: PWA & Mobile） | [#4](https://github.com/Aero123421/dsh-pwa/issues/4) closed / [#5](https://github.com/Aero123421/dsh-pwa/pull/5)、[#6](https://github.com/Aero123421/dsh-pwa/pull/6) |
| [検索プロバイダー](https://github.com/Aero123421/dsh-search-providers) | [v0.3.1](https://github.com/Aero123421/dsh-search-providers/releases/tag/v0.3.1) / [4a5e517](https://github.com/Aero123421/dsh-search-providers/tree/4a5e517504f51fb9b36bf52ee74fc443693303b1) | 設定 → 検索プロバイダーの共通ヘッダー | [#2](https://github.com/Aero123421/dsh-search-providers/issues/2) closed / [#3](https://github.com/Aero123421/dsh-search-providers/pull/3)、[#4](https://github.com/Aero123421/dsh-search-providers/pull/4) |
| [Remora](https://github.com/Aero123421/dsh-remora) | [v0.1.3](https://github.com/Aero123421/dsh-remora/releases/tag/v0.1.3) / [b7d6d85](https://github.com/Aero123421/dsh-remora/tree/b7d6d85436806f6b6ac16736e5fb9df2f82cf406) | 設定 → Remora → 互換性と更新 | [#4](https://github.com/Aero123421/dsh-remora/issues/4) closed / [#6](https://github.com/Aero123421/dsh-remora/pull/6) |
| [Glass UI](https://github.com/Aero123421/dsh-glassui) | [v0.2.2](https://github.com/Aero123421/dsh-glassui/releases/tag/v0.2.2) / [997333b](https://github.com/Aero123421/dsh-glassui/tree/997333b69b1559e4784c58c46c9a01ce47142046) | Glass UI設定画面 | [#5](https://github.com/Aero123421/dsh-glassui/issues/5) closed / [#10](https://github.com/Aero123421/dsh-glassui/pull/10)、[#11](https://github.com/Aero123421/dsh-glassui/pull/11) |
| [CF](https://github.com/Aero123421/dsh-cf) | [v0.1.0-alpha.4](https://github.com/Aero123421/dsh-cf/releases/tag/v0.1.0-alpha.4) / [e4a43d2](https://github.com/Aero123421/dsh-cf/tree/e4a43d240d402514629400da5600f1bb4ee06b03) | 設定 → Cloudflare → プラグインの更新 | [#5](https://github.com/Aero123421/dsh-cf/issues/5) closed / [#6](https://github.com/Aero123421/dsh-cf/pull/6) |

各画面では「更新を確認」と「更新する」を分けています。導入元やmanagerの有無、書き込み可否によって手動更新になる場合があります。プラグインをOFFにすると独自設定欄も使えないため、CLIで手動更新できます。標準画面の更新操作は、Hostが`installTarget`を提供する項目に限られます。CLIと`installBundle()`では有効化の扱いが違うため、[導入手順](installation.md#cliから入れる)で確認してください。

## 実装例と配布経路

リンクは上表の公開タグと同じコミットへ固定しています。ファイル単体のコピーではなく、Host・Client・配布宣言・テストを合わせて確認します。

| 対象 | Host / Clientの実装例 | 配布・更新で保つもの |
| --- | --- | --- |
| Piログイン | [候補・導入・照合](https://github.com/Aero123421/dsh-pi-login/blob/a8002c2355cb31fab680ff220b7a985010ec4f9e/src/updates.mjs)、[Client状態](https://github.com/Aero123421/dsh-pi-login/blob/a8002c2355cb31fab680ff220b7a985010ec4f9e/src/update-controller.mjs) | GitHubタグまたは検証済みtgz。credential・モデル・Fast選択を維持。Pi SDK更新は開発者の別手順 |
| 日本語パック | [Host更新](https://github.com/Aero123421/dsh-japanese/blob/97b4ce33f4fa696a497a6630180681565983a5fc/src/updates.ts)、[設定ページ](https://github.com/Aero123421/dsh-japanese/blob/97b4ce33f4fa696a497a6630180681565983a5fc/src/update-page.jsx) | GitHubタグまたは検証済みtgz。表示言語と利用者指定のfontを維持。更新サービスなしでも辞書・fontを登録 |
| PWA・モバイル | [Host更新](https://github.com/Aero123421/dsh-pwa/blob/e2692d04699294c31b53e54224bc05d81e2b205e/updates.js)、[設定・モバイル表示](https://github.com/Aero123421/dsh-pwa/blob/e2692d04699294c31b53e54224bc05d81e2b205e/client.js) | 自己更新はGitHubソースを明示タグで固定。tgz導入は手動更新。manifestのidentity・scope・icon URLを維持 |
| 検索プロバイダー | [Host更新](https://github.com/Aero123421/dsh-search-providers/blob/4a5e517504f51fb9b36bf52ee74fc443693303b1/src/updates.ts)、[Client状態](https://github.com/Aero123421/dsh-search-providers/blob/4a5e517504f51fb9b36bf52ee74fc443693303b1/src/update-controller.ts) | GitHubタグまたは検証済みtgz。APIキー・既定provider・ON/OFF・追加toolの選択を維持 |
| Remora | [候補・tgz検査](https://github.com/Aero123421/dsh-remora/blob/b7d6d85436806f6b6ac16736e5fb9df2f82cf406/packages/dsh-remora/src/core/updates.ts)、[導入・照合](https://github.com/Aero123421/dsh-remora/blob/b7d6d85436806f6b6ac16736e5fb9df2f82cf406/packages/dsh-remora/src/core/remora.ts) | workspaceルートでなく`dsh-remora-<version>.tgz`。local限定管理、権限・緊急停止・監査、Hub/CLIの別配布を維持 |
| Glass UI | [Host更新](https://github.com/Aero123421/dsh-glassui/blob/997333b69b1559e4784c58c46c9a01ce47142046/src/host/updates.mjs)、[Client状態](https://github.com/Aero123421/dsh-glassui/blob/997333b69b1559e4784c58c46c9a01ce47142046/src/client/update-controller.mjs) | 更新前に保存待ち編集を確定。更新処理と描画engineの寿命を分ける。設定・壁紙を維持 |
| CF | [Host更新](https://github.com/Aero123421/dsh-cf/blob/e4a43d240d402514629400da5600f1bb4ee06b03/src/updates.js)、[設定UI](https://github.com/Aero123421/dsh-cf/blob/e4a43d240d402514629400da5600f1bb4ee06b03/src/client.js) | GitHubソース。安定版・プレリリースを区別。cloudflaredやTunnel/DNS/Accessを更新に巻き込まない |

6つの最新Releaseにはplugin用tgzと`SHA256SUMS`があり、CFはassetなしのソース配布です。assetがあることと、各updaterがtgz導入の自己更新に対応することは別です。ローカル開発pathやnpm導入を、画面から黙って別の配布経路へ切り替えません。

PWA `0.3.0`のモバイル表示は自動・オン・オフを選べ、自動では幅768px未満で有効です。選択はブラウザー内に保存され、Host profileの更新記録とは別です。Glass UI `0.2.2`はインラインコードの不透明度設定と描画処理の改善を含みます。検証報告と限界は[追加公開分](update-implementation.md#更新機能追加後の公開分)にあります。

## 更新Issue作成時の調査

以下は2026-10-13 14:00 JSTの記録です。当時の版・配布状態・提案を残しており、現在の機能一覧ではありません。

| リポジトリ | 用途 | mainのpackage版 / 確認コミット | 最新の公開Release | 更新Issue |
| --- | --- | --- | --- | --- |
| [dsh-pi-login](https://github.com/Aero123421/dsh-pi-login) | Pi経由のログイン・provider/model管理 | `0.4.1` / [2c47c82](https://github.com/Aero123421/dsh-pi-login/tree/2c47c82880c0f2f8f8f1dd433369acd50478259d) | [v0.4.1](https://github.com/Aero123421/dsh-pi-login/releases/tag/v0.4.1) | [#9](https://github.com/Aero123421/dsh-pi-login/issues/9) |
| [dsh-japanese](https://github.com/Aero123421/dsh-japanese) | 日本語辞書と日本語font | `0.1.1` / [c6bb537](https://github.com/Aero123421/dsh-japanese/tree/c6bb53790233c171f6854820f89e87205abf5b51) | [v0.1.1](https://github.com/Aero123421/dsh-japanese/releases/tag/v0.1.1) | [#2](https://github.com/Aero123421/dsh-japanese/issues/2) |
| [dsh-pwa](https://github.com/Aero123421/dsh-pwa) | Web版のmanifestとホーム画面icon | `0.1.0` / [135828c](https://github.com/Aero123421/dsh-pwa/tree/135828c05e8fe5fc4af2fefdf891564c686638a9) | 未作成 | [#4](https://github.com/Aero123421/dsh-pwa/issues/4) |
| [dsh-search-providers](https://github.com/Aero123421/dsh-search-providers) | web_searchのproviderと追加検索ツール | `0.2.0` / [ca7a1e4](https://github.com/Aero123421/dsh-search-providers/tree/ca7a1e484cd25e1812fc333c85b0185a40659e49) | [v0.2.0](https://github.com/Aero123421/dsh-search-providers/releases/tag/v0.2.0) | [#2](https://github.com/Aero123421/dsh-search-providers/issues/2) |
| [dsh-remora](https://github.com/Aero123421/dsh-remora) | 外部clientからDSHを操作するhub連携 | `0.1.1` / [ed7e997](https://github.com/Aero123421/dsh-remora/tree/ed7e99736b0cc8e72a956722fb6fc72fda927239) | [v0.1.1](https://github.com/Aero123421/dsh-remora/releases/tag/v0.1.1) | [#4](https://github.com/Aero123421/dsh-remora/issues/4) |
| [dsh-glassui](https://github.com/Aero123421/dsh-glassui) | DSHのガラス調UI・壁紙 | `0.1.2` / [3a062be](https://github.com/Aero123421/dsh-glassui/tree/3a062be9a5e0e7a2b0f81a95e38b9e6d71620f37) | [v0.1.2](https://github.com/Aero123421/dsh-glassui/releases/tag/v0.1.2) | [#5](https://github.com/Aero123421/dsh-glassui/issues/5) |
| [dsh-cf](https://github.com/Aero123421/dsh-cf) | Cloudflare Tunnel・Access経由の接続 | `0.1.0-alpha.3` / [5da69eb](https://github.com/Aero123421/dsh-cf/tree/5da69eb4458640ec8f9e62b71f2982b5dee8cbda) | [v0.1.0-alpha.3](https://github.com/Aero123421/dsh-cf/releases/tag/v0.1.0-alpha.3)（プレリリース） | [#5](https://github.com/Aero123421/dsh-cf/issues/5) |

当時はmainのpackage版とReleaseの公開物を別々に確認し、調査・Issue作成・文書化を行いました。下の差分表も、実装前の提案です。実装後の検証は[実装記録](update-implementation.md)へ分けています。

### Issue作成時の更新機能の差分

| 対象 | 当時の入口 | 当時の更新対象と配布 | Issueで提案した変更 |
| --- | --- | --- | --- |
| Piログイン | モデル設定の共通フッターとproviderカード | `@local/dsh-pi-login`。`local-dsh-pi-login-<version>.tgz` | 共通フッターに1組の更新操作。モデル一覧の再取得と区別 |
| 日本語化 | locale・fontの登録。独自設定画面なし | `@local/dsh-japanese`。`local-dsh-japanese-<version>.tgz` | 小さな設定項目。更新サービスがなくても日本語化は継続 |
| PWA | HostのrouteとHTML注入。Client entryなし | `dsh-pwa`。ソース直配布、Release未作成 | 版付き配布を先に作成し、Client entryと更新UIを追加 |
| 検索プロバイダー | 専用の検索設定画面 | `@aero123421/dsh-search-providers`。`aero123421-dsh-search-providers-<version>.tgz` | 共通ヘッダーに更新操作。既定provider・追加tool・キーを維持 |
| Remora | 「互換性と更新」に実装あり | `dsh-remora`。`dsh-remora-<version>.tgz` | 導入結果・再起動待ちを正しく表示し、監査も結果に合わせる |
| Glass UI | versionを受け取る専用設定画面 | `dsh-glassui`。`dsh-glassui-<version>.tgz` | 既存画面に更新操作。保存待ち編集とengineの寿命に配慮 |
| CF | Cloudflare設定画面 | `dsh-cf`。版付きGitHub source、alphaのみ、assetなし | channelを区別した候補取得。Tunnel資源とbinaryを更新対象に混ぜない |

当時tgzを公開していた5つには`SHA256SUMS`もありました。ソースをGitHubから入れた利用者を、更新時に黙ってtgzやnpmへ移す方針ではありません。同じ配布経路で検証した候補を選ぶか、経路変更を表示して明示的に選択させます。Remoraはrootがworkspaceなので、plugin用tgzを使います。

## 共通部分と個別部分

共通にするのは、状態名、候補の検証、実際のDSH managerへの委譲、切断後の照合です。repository・package・asset名・channel・権限・保存状態はpluginごとに決めます。

```text
更新を確認
  → 固定した配布元の候補を取得
  → 版・channel・互換性・配布形式を確認
  → 現在版、候補版、変更内容を表示
更新する
  → Hostで管理権限と候補を再確認
  → 現在のbundleのenabledを取得
  → DSH installBundleへ委譲
  → ChangeResultを表示
  → 必要なら再起動し、実行版を確認
```

各Issueには対象ファイル、package名、Host側の擬似コード、保存すべき設定、完了条件を載せています。共通の新しいSDKを7つへ必須導入する案ではありません。小さな内部helperで始め、複数の実装で同じ契約が確認できた部分だけを後から共通化できます。

詳細は[更新ボタン](update-button.md)、更新以外の機能は[搭載する機能](recommended-features.md)、併用時の境界は[干渉対策](plugin-coexistence.md)にあります。

## 確認範囲

現在の公開版はRelease・タグ・package・主要なREADMEと実装PRを照合しています。最新PWA・Glass UIの試験結果は各PRとReleaseノートの報告として参照し、この文書更新で再実行した結果には含めません。以下はIssue作成時の調査範囲です。

- 公開リポジトリのmetadata、mainの固定SHA、package・patch・主要Host/Client処理を確認した。
- 各repositoryの全状態のIssue/PR一覧を取得した。各100件を上限に取得し、今回の各一覧は100件未満だった。更新UIの重複Issueがないことを確認したうえで作成した。
- Releaseのタグ、prerelease状態、asset名を確認した。PWAにはReleaseがなく、CFの最新Releaseにはassetがなかった。
- DSH APIは`0.2.1-alpha.2` / `d743267388641bc76f17c45ce8b4c231aed1d32c`を基準にした。DSHの最新版という意味ではない。
- runtimeコードの変更、7pluginの同時起動、実providerへの通信、Cloudflare資源の作成、更新の実行は行っていない。

過去のレビューは当時のコミットを参照したまま残しています。今回Piが`0.4.1`、Glass UIが`0.1.2`でも、以前の版を調べた記録を新しい版の検証結果へ書き換えません。
