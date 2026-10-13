# 深掘り対象の配布物を別に確認する

2026-10-13に、ソース分析対象の15 packageについて、版を指定してnpm metadataと実tarballを取得しました。registryの`dist.integrity`、アーカイブ内のpackage名・版、具体的な公開entryとbundle patchの存在を確認しています。npm/prepare/install scriptやplugin entryは実行していません。

## 取得した実tarball

| package・版 | 圧縮byte数 | 通常file数 | integrity / 具体entry・patch |
| --- | ---: | ---: | --- |
| `dshmarket@1.66.20` | 1,249,972 | 177 | 一致 / 存在 |
| `dsh-better-sidebar@0.25.0` | 4,412,751 | 434 | 一致 / 存在 |
| `@linxin666/dsh-web-all@0.4.6` | 2,168,044 | 20 | 一致 / 存在 |
| `@deepseek-harness-tui/dsh-tui@0.14.0` | 18,063,990 | 3,082 | 一致 / 存在 |
| `dsh-plugin-subscriptions@0.9.9` | 552,933 | 139 | 一致 / 存在 |
| `@liustack/modlens@3.26.6` | 233,457 | 34 | 一致 / 存在 |
| `@wxg-prc-cpg/browser-skill-dsh-plugin@0.3.2` | 107,246 | 13 | 一致 / 存在 |
| `@zilliz/memsearch-dsh@0.1.6` | 54,275 | 23 | 一致 / 存在 |
| `dsh-context@0.69.1` | 158,277 | 10 | 一致 / 存在 |
| `dsh-whale-widget@0.4.2` | 5,706,702 | 24 | 一致 / 存在 |
| `@openviking/dsh-memory-plugin@0.5.24` | 101,120 | 41 | 一致 / 存在 |
| `@everos-ai/dsh-plugin@0.1.0` | 23,943 | 22 | 一致 / 存在 |
| `@memtensor/memos-local-plugin@2.0.16-beta.1` | 1,509,211 | 836 | 一致 / 存在 |
| `@nanmicoder/dsh-agent-teams@0.1.23` | 2,160,245 | 123 | 一致 / 存在 |
| `@xmanrui/dsh-im@4.39.0` | 9,634,840 | 435 | 一致 / 存在 |

版別の取得URL、確認したentry、peerの不一致は[機械可読の記録](../../data/npm-package-checks-2026-10-13.json)にあります。例えば[dshmarket 1.66.20](https://registry.npmjs.org/dshmarket/1.66.20)、[OpenViking 0.5.24](https://registry.npmjs.org/%40openviking%2Fdsh-memory-plugin/0.5.24)、[Agent Teams 0.1.23](https://registry.npmjs.org/%40nanmicoder%2Fdsh-agent-teams/0.1.23)のmetadataを参照できます。

globを持つexportsは具体的な全組み合わせを列挙していません。通常fileとしての存在と、package内の宣言を照合した結果です。依存の解決、DSHへの登録、ブラウザー実行、別CLI/serverの準備は別の検査です。registryのdigestとの一致を発行者確認やruntimeの正しさの保証とは扱いません。

## 基準DSHへのpeer条件

公開tarballの`@deepseek-ai/dsh`・`@deepseek-ai/dsh-*`のpeerを、DSH `0.2.1-alpha.2`へ照合しました。Node `22.23.3`、semver `7.8.5`で、DSHと同じく`includePrerelease: true`を使っています。根拠は[DSHの互換性検査](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/app-boot/src/plugin-compatibility.ts)です。

| package | 調べたDSH peer数 | 不一致 |
| --- | ---: | ---: |
| dshmarket | 1 | 0 |
| Better Sidebar | 14 | 0 |
| dsh-web-all | 1 | 0 |
| TUI | 31 | 31 |
| Subscriptions | 5 | 5 |
| Modlens | 0 | 検査対象なし |
| BrowserSkill | 5 | 0 |
| Memsearch | 1 | 0 |
| Context | 2 | 0 |
| Whale Widget | 0 | 検査対象なし |
| OpenViking | 3 | 0 |
| EverOS plugin | 3 | 3 |
| MemOS local plugin | 6 | 6 |
| Agent Teams | 21 | 21 |
| IM | 0 | 検査対象なし |

TUI・Subscriptions・EverOS・MemOS・Agent Teamsの公開宣言は、この基準版と一致しません。旧版の列挙や`<0.2.0`などの範囲が理由です。作者の対象DSHでも動かないという結果ではなく、このDSHへ通常の版検査で導入すると不一致となる条件です。版検査を回避して対応済みに見せず、対象版・実APIへの追従を確認します。

peerがないpackageは、DSH APIを使っていない・互換性を実証済みという意味ではありません。不一致0でも、実際のevent、remote、Client inject、保存形式を検査した結果ではありません。例えば[画像・記憶](deep-browser-memory.md)と[エージェント](deep-providers-agents.md)の章では、ソースに残る旧API形状とモデルへ渡る情報を別に追っています。

## 修正ソースと配布物が届く順番

OpenVikingの共有proxy修正PRは、その公開報告の時点でnpm未publishと記載しています。今回の再取得では`@openviking/dsh-memory-plugin@0.5.24`のmetadata・tarball・entryを確認できました。報告当時の状態と、今取得できる版を別々に記録します。実DSH/MCPへ導入して修正経路を実行した結果ではありません。

ソースのdefault HEAD、npm版、Release、別CLI・extension・installerの公開は同時とは限りません。同じpackage版でソースだけ進む場合もあるため、同版番号だけで中身の一致や利用者への修正到達を証明しません。旧版からの更新と再起動は、[更新後の反映](../update-and-restart.md)の経路で別に確認します。

前回の8 packageの記録は[当時の配布物確認](package-checks.md)に残しています。今回は15 packageの再取得・拡大で、全外部pluginの実起動や全配布経路を確認したものではありません。
