# 配布物と互換性の確認結果

この章は、今回実行した確認の記録です。READMEに書かれた導入方法や作者のテスト件数を、そのまま成功結果として転記していません。

以下は最初の8 packageの確認です。その後の再取得と追加対象を含む15 packageの結果は[深掘り対象の配布物確認](deep-package-checks.md)へ分けています。同じ版の再取得と、新しい版の検査を混同しません。

## 公開npm tarballを確認した

2026-10-13 02:35 UTC前後に、versionを指定してregistry metadataとtarballを取得しました。archiveのSHA-512をregistryの`dist.integrity`と照合し、package名・版、main、exportsの具体的なfile、bundle patchの存在を確認しています。

archiveをDSHへ導入したり、packageのinstall/build scriptを実行したりはしていません。整合性の一致は、runtimeの正しさや発行者の安全性の保証ではありません。

| package・版 | 圧縮byte数 | 通常file数 | 整合性 | 公開entry・patch |
| --- | ---: | ---: | --- | --- |
| `dshmarket@1.66.18` | 1,225,306 | 177 | 一致 | 存在 |
| `dsh-better-sidebar@0.25.0` | 4,412,751 | 434 | 一致 | 存在 |
| `@deepseek-harness-tui/dsh-tui@0.14.0` | 18,063,990 | 3,082 | 一致 | 存在 |
| `dsh-plugin-subscriptions@0.9.9` | 552,933 | 139 | 一致 | 存在 |
| `@liustack/modlens@3.26.6` | 233,457 | 34 | 一致 | 存在 |
| `@wxg-prc-cpg/browser-skill-dsh-plugin@0.3.2` | 107,246 | 13 | 一致 | 存在 |
| `@zilliz/memsearch-dsh@0.1.6` | 54,275 | 23 | 一致 | 存在 |
| `@linxin666/dsh-web-all@0.4.6` | 2,168,044 | 20 | 一致 | 存在 |

globのexportsは、具体的な全組合せをこの確認で生成していません。型宣言を含む具体的なpathの存在までの確認です。import時の依存解決、Clientでの実行、実際のLoader登録は別に検証します。

`@open-design/dsh-runtime@0.1.0`は、この確認時にregistryから404が返りました。公開npm版としては確認できていません。ソース上にbundleが存在することとは別の結果です。

一次資料は、例えば[dshmarketの版別metadata](https://registry.npmjs.org/dshmarket/1.66.18)、[TUIのmetadata](https://registry.npmjs.org/%40deepseek-harness-tui%2Fdsh-tui/0.14.0)、[Subscriptionsのmetadata](https://registry.npmjs.org/dsh-plugin-subscriptions/0.9.9)です。registryの応答を取得した時点の記録として扱います。

## DSHのpeer条件を同じ規則で照合した

確認版のDSHは、`@deepseek-ai/dsh`と`@deepseek-ai/dsh-*`のpeer条件を、実行中DSHの版へ照合します。prereleaseを含む比較には`includePrerelease: true`を指定しています。

通常のSemVer比較でprereleaseを除外する条件と、DSHのこの検査は違います。今回も同じ条件で`0.2.1-alpha.2`と比較しました。

```js
semver.satisfies('0.2.1-alpha.2', '^0.2.0-rc.2', {
  includePrerelease: true,
}) // true

semver.satisfies('0.2.1-alpha.2', '0.2.0-rc.2', {
  includePrerelease: true,
}) // false
```

根拠: [DSHの実際の版検査](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/app-boot/src/plugin-compatibility.ts)。

### npm metadataでの結果

| package・版 | 調べたDSH peer数 | 不一致 |
| --- | ---: | ---: |
| `dshmarket@1.66.18` | 1 | 0 |
| `dsh-better-sidebar@0.25.0` | 14 | 0 |
| `@deepseek-harness-tui/dsh-tui@0.14.0` | 31 | 31 |
| `dsh-plugin-subscriptions@0.9.9` | 5 | 5 |
| `@liustack/modlens@3.26.6` | 0 | 検査対象なし |
| `@wxg-prc-cpg/browser-skill-dsh-plugin@0.3.2` | 5 | 0 |
| `@zilliz/memsearch-dsh@0.1.6` | 1 | 0 |
| `@linxin666/dsh-web-all@0.4.6` | 1 | 0 |

TUIとSubscriptionsは、列挙した旧版や`0.2.0-rc.2`までを受け入れる条件が、基準版と一致しません。通常のDSH互換性検査では、この条件が拒否の理由になります。今回の結果を、作者が対応対象にしている旧DSHでも動かないという意味には広げません。

不一致0は、調べた宣言に不一致がないという結果です。内部API、React、Cordis、native module、OS、実通信の互換性を確認した結果ではありません。検査対象がないpackageを、0件合格と同じ意味で扱わないでください。

## Gitソースとnpm配布物を分けた

固定したGitコミットのmanifestも同じ条件で調べました。TUIのGit側はDSH peerが36件で、同じ基準版への不一致も36件でした。npm側の31件と同一ではありません。

ブランチ先頭、packageのversion、公開npm版、Release tagの内容が、自動的にすべて一致するとは考えません。実際に利用者が取得する指定で検証します。

Git treeに公開entryが存在するかも確認しました。

| ソース構成 | 固定コミットの状態 | 導入時に確認すること |
| --- | --- | --- |
| dshmarket | Host側の`lib/`entryは未追跡 | `prepare`によるbuildと、その許可・依存・成功 |
| Better Sidebar | `lib/`entry・型宣言は未追跡 | Git取得時のbuildと、npm配布物との違い |
| TUI | `lib/types/`entryは未追跡 | packageのbuildと、専用profile・起動経路 |
| Subscriptions | `lib/`entryは未追跡 | `prepare`による生成と、DSH peer条件 |
| Routing Suite injector | `injector/lib/`entryは未追跡 | prepare・DSHソースcheckout依存の範囲 |
| BrowserSkill | DSH leafの`lib/`entryは未追跡 | repoのルートと導入するleaf packageを区別する |
| Open Design | DSH leafの`dist/`entryは未追跡 | 接続用packageのbuild・配布経路 |
| Modlens | DSH entryはplain JSで追跡済み | 同梱CLI・依存・外部解析provider |
| Memsearch | DSH leaf entryはplain JSで追跡済み | 別のmemsearch CLI・Python・indexの準備 |
| Our Free Model | ルートentryはplain JSで追跡済み | 同梱channel、更新方式、設定・通信先 |
| dsh-web | ルートbundleから集約packageを指定 | 集約packageとchild dependencyの解決 |

未追跡のentryがあることだけで、GitHub導入が失敗すると確定したわけではありません。build scriptを含む経路で生成される場合があります。ただし、ビルドなしで導入できる案内には、その確認が必要です。

自作pluginでは、GitHub指定を主な導入方法にするなら、[インストール章](../installation.md)のように必要な生成物を同梱し、CIで一致を確認する方法を基本にできます。

## 小さいqueue helperの単独確認

BrowserSkillの確認コミットにある`queue.ts`をNode `22.23.3`の別processで読み込み、次を確認しました。CLI、ブラウザー拡張、plugin entry、npm scriptは実行していません。

| 入力・順序 | 結果 |
| --- | --- |
| Aが実行中 → 待機Bを取消 → Cを待機 | Aの終了までCは開始しない |
| callbackがPromiseを返す前に同期throw | 呼び出し元Promiseがpending、内側のunhandled rejectionを観測 |
| 同じthrowをPromiseの拒否へ変換 | 呼び出し元がrejectし、後続要求も完了 |

参照元と条件は[BrowserSkillの調査](browser-and-routing.md)にあります。ソースhelperの検証を、公開npm bundle全体や実ブラウザーでの検証へ広げていません。

## 今回実施していない確認

- 外部pluginの実DSH導入と、ON/OFF・再起動・解除。
- OAuthと実providerへの生成、画像解析、embedding、要約。
- 実ブラウザー・terminal・Desktopの表示と操作。
- OS別keychain・native module・process終了。
- 実際の旧版profile・保存データからの更新・復旧。

これらを確認した後に、対象版・操作・結果を追記してください。ソース上の設計から成功結果を推測して埋めないでください。
