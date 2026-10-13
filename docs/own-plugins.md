# 自作プラグインと更新Issue

2026-10-13 14:00 JSTに取得した公開リポジトリ、mainのpackage、Release、Issue/PRを照合しました。DSH向けの自作拡張は次の7つです。文書リポジトリやDSH本体とは分けています。

## 一覧

| リポジトリ | 用途 | mainのpackage版 / 確認コミット | 最新の公開Release | 更新Issue |
| --- | --- | --- | --- | --- |
| [dsh-pi-login](https://github.com/Aero123421/dsh-pi-login) | Pi経由のログイン・provider/model管理 | `0.4.1` / [2c47c82](https://github.com/Aero123421/dsh-pi-login/tree/2c47c82880c0f2f8f8f1dd433369acd50478259d) | [v0.4.1](https://github.com/Aero123421/dsh-pi-login/releases/tag/v0.4.1) | [#9](https://github.com/Aero123421/dsh-pi-login/issues/9) |
| [dsh-japanese](https://github.com/Aero123421/dsh-japanese) | 日本語辞書と日本語font | `0.1.1` / [c6bb537](https://github.com/Aero123421/dsh-japanese/tree/c6bb53790233c171f6854820f89e87205abf5b51) | [v0.1.1](https://github.com/Aero123421/dsh-japanese/releases/tag/v0.1.1) | [#2](https://github.com/Aero123421/dsh-japanese/issues/2) |
| [dsh-pwa](https://github.com/Aero123421/dsh-pwa) | Web版のmanifestとホーム画面icon | `0.1.0` / [135828c](https://github.com/Aero123421/dsh-pwa/tree/135828c05e8fe5fc4af2fefdf891564c686638a9) | 未作成 | [#4](https://github.com/Aero123421/dsh-pwa/issues/4) |
| [dsh-search-providers](https://github.com/Aero123421/dsh-search-providers) | web_searchのproviderと追加検索ツール | `0.2.0` / [ca7a1e4](https://github.com/Aero123421/dsh-search-providers/tree/ca7a1e484cd25e1812fc333c85b0185a40659e49) | [v0.2.0](https://github.com/Aero123421/dsh-search-providers/releases/tag/v0.2.0) | [#2](https://github.com/Aero123421/dsh-search-providers/issues/2) |
| [dsh-remora](https://github.com/Aero123421/dsh-remora) | 外部clientからDSHを操作するhub連携 | `0.1.1` / [ed7e997](https://github.com/Aero123421/dsh-remora/tree/ed7e99736b0cc8e72a956722fb6fc72fda927239) | [v0.1.1](https://github.com/Aero123421/dsh-remora/releases/tag/v0.1.1) | [#4](https://github.com/Aero123421/dsh-remora/issues/4) |
| [dsh-glassui](https://github.com/Aero123421/dsh-glassui) | DSHのガラス調UI・壁紙 | `0.1.2` / [3a062be](https://github.com/Aero123421/dsh-glassui/tree/3a062be9a5e0e7a2b0f81a95e38b9e6d71620f37) | [v0.1.2](https://github.com/Aero123421/dsh-glassui/releases/tag/v0.1.2) | [#5](https://github.com/Aero123421/dsh-glassui/issues/5) |
| [dsh-cf](https://github.com/Aero123421/dsh-cf) | Cloudflare Tunnel・Access経由の接続 | `0.1.0-alpha.3` / [5da69eb](https://github.com/Aero123421/dsh-cf/tree/5da69eb4458640ec8f9e62b71f2982b5dee8cbda) | [v0.1.0-alpha.3](https://github.com/Aero123421/dsh-cf/releases/tag/v0.1.0-alpha.3)（プレリリース） | [#5](https://github.com/Aero123421/dsh-cf/issues/5) |

mainのpackage版とReleaseの公開物は別々に確認しています。上の版が一致しても、そのtgzを今回インストールして内容・動作まで照合したという意味ではありません。Issueは更新機能の実装計画で、今回行ったのは調査・Issue作成・文書化です。

## 更新機能の差分

| 対象 | 現在の入口 | 更新対象と配布 | Issueで提案した変更 |
| --- | --- | --- | --- |
| Piログイン | モデル設定の共通フッターとproviderカード | `@local/dsh-pi-login`。`local-dsh-pi-login-<version>.tgz` | 共通フッターに1組の更新操作。モデル一覧の再取得と区別 |
| 日本語化 | locale・fontの登録。独自設定画面なし | `@local/dsh-japanese`。`local-dsh-japanese-<version>.tgz` | 小さな設定項目。更新サービスがなくても日本語化は継続 |
| PWA | HostのrouteとHTML注入。Client entryなし | `dsh-pwa`。ソース直配布、Release未作成 | 版付き配布を先に作成し、Client entryと更新UIを追加 |
| 検索プロバイダー | 専用の検索設定画面 | `@aero123421/dsh-search-providers`。`aero123421-dsh-search-providers-<version>.tgz` | 共通ヘッダーに更新操作。既定provider・追加tool・キーを維持 |
| Remora | 「互換性と更新」に実装あり | `dsh-remora`。`dsh-remora-<version>.tgz` | 導入結果・再起動待ちを正しく表示し、監査も結果に合わせる |
| Glass UI | versionを受け取る専用設定画面 | `dsh-glassui`。`dsh-glassui-<version>.tgz` | 既存画面に更新操作。保存待ち編集とengineの寿命に配慮 |
| CF | Cloudflare設定画面 | `dsh-cf`。版付きGitHub source、alphaのみ、assetなし | channelを区別した候補取得。Tunnel資源とbinaryを更新対象に混ぜない |

tgzを公開している5つには`SHA256SUMS`もあります。ソースをGitHubから入れた利用者を、更新時に黙ってtgzやnpmへ移す方針ではありません。同じ配布経路で検証した候補を選ぶか、経路変更を表示して明示的に選択させます。Remoraはrootがworkspaceなので、plugin用tgzを使います。

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

- 公開リポジトリのmetadata、mainの固定SHA、package・patch・主要Host/Client処理を確認した。
- 各repositoryの全状態のIssue/PR一覧を取得した。各100件を上限に取得し、今回の各一覧は100件未満だった。更新UIの重複Issueがないことを確認したうえで作成した。
- Releaseのタグ、prerelease状態、asset名を確認した。PWAにはReleaseがなく、CFの最新Releaseにはassetがなかった。
- DSH APIは`0.2.1-alpha.2` / `d743267388641bc76f17c45ce8b4c231aed1d32c`を基準にした。DSHの最新版という意味ではない。
- runtimeコードの変更、7pluginの同時起動、実providerへの通信、Cloudflare資源の作成、更新の実行は行っていない。

過去のレビューは当時のコミットを参照したまま残しています。今回Piが`0.4.1`、Glass UIが`0.1.2`でも、以前の版を調べた記録を新しい版の検証結果へ書き換えません。
