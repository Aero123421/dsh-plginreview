# 公式・外部プラグインの実装調査

自作プラグイン以外の実装を調べ、次の開発で参考にできる処理と、そのまま取り込む前に確認する条件をまとめました。2026-10-13の調査です。

## 調査した範囲

公式はDeepSeek Harnessの公開ソースを基準に、同梱の任意bundle 11種類と、後から導入する連携2種類を整理しています。browser runtime、subagent、worktree、翻訳、音声入力などは主要な処理と解除経路まで読みました。

外部は12リポジトリを選び、公開コミットを固定しました。GitHubの`dsh-plugin` topic検索、スター数、プラグイン一覧を候補探しに使い、package manifestとソースで実際の構成を確認しています。一覧サイトの「公式」「検証済み」表示を、そのまま実装の検証結果には使っていません。

実施した確認はソース読解、DSHの版条件の照合、npm配布物の整合性・entry確認と、I/Oを伴わないqueue helperの単独検証です。外部プラグインのinstall scriptやアプリは実行していません。実DSHへの導入、ブラウザー操作、実OAuth、実API、OS別の動作は今回の確認範囲に含みません。

## 読む場所

| 調べたいこと | 文書 |
| --- | --- |
| 公式bundleの構成・登録・解除 | [公式プラグイン](official.md) |
| マーケット、更新API、複数packageの管理 | [配布・更新・マーケット](marketplaces-and-updates.md) |
| 認証、動的モデル一覧、画像、記憶 | [モデル・認証・画像・記憶](providers-and-memory.md) |
| Sidebar、TUI、Desktop、他アプリからの接続 | [UIと実行環境](ui-and-runtimes.md) |
| 実ブラウザー操作、実行時注入、routing preset | [ブラウザーとルーティング](browser-and-routing.md) |
| npm配布物、GitHubの生成物、DSH版条件 | [配布物と互換性の確認結果](package-checks.md) |

## 外部リポジトリの一覧

スター数は2026-10-13 02:28 UTC前後のGitHub APIの値です。DSH以外にも対応するプロジェクトでは、リポジトリ全体のスター数です。DSHプラグイン単独の利用者数ではありません。

| リポジトリ・固定コミット | stars | 確認した構成 |
| --- | ---: | --- |
| [nexu-io/open-design](https://github.com/nexu-io/open-design/tree/0bd8251c9b5c0bed4b3aef87f53f9c1eadc493c7) | 100,773 | 別アプリと、`packages/dsh-runtime`の接続bundle |
| [anywhere-labs/dsh-desktop](https://github.com/anywhere-labs/dsh-desktop/tree/7abe94dd037450f8ebaae71d938b8dad2f125610) | 30,594 | 複数のDesktop editionと、profile・配布runtimeの管理 |
| [Ebony-Vinyl/dsh-our-free-model](https://github.com/Ebony-Vinyl/dsh-our-free-model/tree/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68) | 12,127 | provider adapter、モデル一覧、独自の署名付き更新 |
| [Tencent/BrowserSkill](https://github.com/Tencent/BrowserSkill/tree/4c8616b12273ac5a22ce4adb494cac941e20de2a) | 8,732 | CLI・ブラウザー拡張と、DSH専用bundle |
| [zhu1090093659/dsh-web](https://github.com/zhu1090093659/dsh-web/tree/c76357950f341db57ef8852420f989dd7314d9e2) | 8,667 | UI、マーケット、presetなどをまとめる集約bundle |
| [yjh051108/dsh-routing-suite](https://github.com/yjh051108/dsh-routing-suite/tree/195273352f23bff7f9023ebe2ec0cdbdf9c98f10) | 7,022 | 実行時injectorと、エージェント構成・routing preset |
| [dsh-market/dsh-market](https://github.com/dsh-market/dsh-market/tree/840cd0a4e952aae6cf77c5e4a85df42ab105c718) | 6,285 | `dshmarket` bundleと、プラグイン向け更新API |
| [ccch1mneyyy/dsh-TUI](https://github.com/ccch1mneyyy/dsh-TUI/tree/e30a8ca9a88e536ad5096445cb1c3f29e6f35908) | 4,480 | 専用のterminal UI、backend・profile・拡張API |
| [liustack/modlens](https://github.com/liustack/modlens/tree/1d8b20fc97a33b456e0d500037d4d66febaeb80a) | 4,226 | 画像解析CLI、DSH tool、画像対応provider wrapper |
| [omdsh-dev/DSH-better-sidebar](https://github.com/omdsh-dev/DSH-better-sidebar/tree/d0a47bed1175e8214fc45bacf8535cc0b4d386a0) | 4,133 | Sidebarと、第三者がtab・viewerを登録するAPI |
| [zilliztech/memsearch](https://github.com/zilliztech/memsearch/tree/09e07d86b31ff81938b4f44a57099b6a9fc8723f) | 2,738 | 共通の記憶エンジンと、`plugins/dsh`のbundle |
| [V1ki/dsh-plugin-subscriptions](https://github.com/V1ki/dsh-plugin-subscriptions/tree/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443) | 448 | provider別OAuth、複数account、動的モデル一覧 |

これは実装比較のための選定で、全プラグインの人気ランキングではありません。一覧リポジトリ、単なるtopic付与、Skill、MCP server、native bundle、Desktopアプリを混ぜたランキングは作っていません。

## npmで取得されている規模

集計期間は2026-09-13〜2026-10-12です。npm download数にはCI・再導入・自動取得も含まれます。利用者数や品質評価への変換はしていません。

| package | 期間内downloads |
| --- | ---: |
| `dshmarket` | 562,173 |
| `dsh-better-sidebar` | 229,589 |
| `@linxin666/dsh-web-all` | 119,410 |
| `@liustack/modlens` | 94,116 |
| `@deepseek-harness-tui/dsh-tui` | 45,149 |
| `@wxg-prc-cpg/browser-skill-dsh-plugin` | 25,360 |
| `dsh-plugin-subscriptions` | 11,271 |
| `@zilliz/memsearch-dsh` | 2,488 |

取得元はnpmの公開downloads APIです。例えば[dshmarketの同期間の値](https://api.npmjs.org/downloads/point/2026-09-13:2026-10-12/dshmarket)を参照できます。package名はリポジトリ名と一致しない場合があります。

## この調査から追加した観点

1. 更新操作の記録が、画面の再接続まで残るか、Hostの再起動まで残るかを分ける。
2. branch差分、正式な版の更新、配布channel変更、package取得元の変更を分ける。
3. 動的モデル一覧はprovider・accountの権限と能力に結び付け、最後の正常結果を検証して保存する。
4. 拡張APIが返すdisposerと、UI・Host資源の所有範囲を確認する。
5. UI用のファイル操作も、workspace制限やSession sandboxを当然に継承するとは考えない。
6. preset、記憶注入、画像wrapper、token削減が、モデルに渡す情報をどう変えるか確認する。
7. npm配布物とGitHubソース取得を別経路として検証する。
8. 依存同士の版が一致する確認と、上流の公開版に追従している確認を分ける。
