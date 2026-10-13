# 配布とリリース

GitHub指定での導入と、GitHub Releasesのビルド済みtarballを用意します。npmへ公開する場合は追加の配布先として扱い、公開していないnpm名を導入手順に載せません。

## 配布対象を決める

リポジトリのルートがDSH bundleなら、`github:OWNER/REPO#TAG`で導入しやすくなります。ルートが開発用workspaceの場合は、公開bundleがどこにあるかを先に確認します。

Remoraのルートはworkspaceで、bundleは`packages/dsh-remora`です。このような構成に、他の単一packageと同じGitHubルート導入手順を確認なしに当てはめません。利用者に渡すbundle tarballや、対応するsubdirectory指定の可否を実installerで確認します。

複数packageのworkspaceでは、`workspace:*`などの参照がpack後に解決できることも確認します。開発用symlinkに依存した公開物を作らないようにします。

## 版と生成物を揃える

1. packageの版、lockfile、コードに埋めた版を更新する。
2. 固定された依存からbuildし、配布用生成物を作る。
3. 関連テストと、旧版からの設定互換性を確認する。
4. GitHub取得に必要な生成物をGitへ含める。
5. packしたtarballのmanifest、entry、patch、asset、licenseを確認する。
6. 確認したコミットにtagを付け、その内容を配布する。

tag、package、画面の版が違う場合は公開を止めます。buildでtimestamp、ランダム値、入力file列挙順が変わる場合は、生成物が再現できるように直します。

一度公開したtagを別コミットへ移動して、同じ版の中身を差し替える運用は避けます。修正は新しい版として出し、公開された版とソースを追えるようにします。

## `dist/`と`release/`を分ける

推奨する出力の分担です。

```text
dist/                         # packageが実行に使うビルド結果
release/
  dsh-example-0.1.0.tgz       # 配布用package
  SHA256SUMS                  # 配布ファイルのchecksum
```

`dist/`をGitに含めたうえで、release artifactを同じ場所へdownloadして`dist/*`を公開すると、生のJSまでassetに混ざります。Glass UIの[PR #3](https://github.com/Aero123421/dsh-glassui/pull/3)で修正した問題です。

公開対象はtarballとchecksumなど、意図した名前に限定します。globを使う場合も、余計なtarballが残るdirectoryを再利用せず、生成した一覧と照合します。

## CIからReleaseへ渡す

release jobは、テストしたコミットの配布物を受け取ります。別のブランチや、後から変わった`main`を再buildして差し替えません。

| 段階 | 確認 |
| --- | --- |
| checkout | 対象tagとcommitが一致する |
| install | lockfileに従う。秘密情報なしで動く範囲を基本にする |
| build・test | 関連確認が成功し、追跡した生成物との一致を確認する |
| pack | 配布用packageのfile一覧を検査する |
| checksum | 実際に公開するtarballから生成する |
| artifact転送 | 出力先は`release/`。受け取ったchecksumを照合する |
| Release作成 | 明示したassetだけを載せる |
| 公開後smoke | 公開URL・公開tagから実DSHへ導入する |

workflowの`contents: write`は公開するjobに絞ります。attestationを生成する場合も、必要な権限と対象fileをそのjobで宣言します。

## 公開コマンドの例

次は、tagと配布ファイルをすでに作成・検証した後のコマンド例です。`OWNER/REPO`、版、ファイル名、release notesのパスを置き換えます。この文書の確認のために実行するコマンドではありません。

```sh
gh release create v0.1.0 \
  release/dsh-example-0.1.0.tgz \
  release/SHA256SUMS \
  --repo OWNER/REPO \
  --verify-tag \
  --draft \
  --title 'v0.1.0' \
  --notes-file release-notes.md
```

draftのasset名、対象tag、本文を確認してから公開します。不要なassetを見つけたら、ソースtagを変更する前に、配布工程と公開file一覧を見直します。

## リリース本文

利用者が判断するための情報を先に書きます。

- 直った不具合、追加された操作。
- 対応するDSH版。
- 更新方法と再起動の要否。
- 設定・資格情報・履歴の移行がある場合、その扱い。
- 実際に確認した導入経路と、未検証の範囲。

「さまざまな改善」「体験を向上」とだけ書かず、発生条件と修正後の動作を示します。PRの会話履歴や、使わなかった案は通常のリリース本文に並べません。

## checksum・attestation・license

checksumは配布物の破損・取り違えの検出に使います。attestationを付けた場合は、生成したことと、取得者が検証したことを区別します。どちらもruntimeの正しさや全依存の安全性を保証するものではありません。

第三者のfont、画像、アイコン、取り込んだコードを配る場合は、それぞれのlicenseと必要なnoticeをpackに含めます。日本語化のfontと、PWAの元のDeepSeekロゴのlicenseは、この確認が必要だった例です。

## 更新後と旧版への復旧

導入後に、保存設定、資格情報、ON/OFF、ツール・UI登録、現在の実行版を確認します。再起動要求があれば、再起動してから新しい実行版を確認します。

旧版へ戻せるtag・tarballを残し、保存形式が変わる場合は旧コードで読める範囲も記録します。migrationの前に保存したbackupと、秘密情報の保存先を不用意に公開しないようにします。

作業結果は[リリース確認テンプレート](../templates/release-checklist.md)に残せます。

Issue close、merge、配布、利用者の再確認を結ぶ記録は[解決までの進め方](workflow/resolution.md)にあります。Release job成功後のasset修正と、公開後のUI修正は[自作pluginの履歴](workflow/own-cases.md)で追っています。

## 根拠

- [Glass UIの公開workflow](https://github.com/Aero123421/dsh-glassui/blob/b97fa776424b209f72625f81327f7be3c559b6f7/.github/workflows/release.yml)
- [Remora bundleのpackage構成](https://github.com/Aero123421/dsh-remora/blob/ed7e99736b0cc8e72a956722fb6fc72fda927239/packages/dsh-remora/package.json)
- [日本語化のGitHub配布修正](https://github.com/Aero123421/dsh-japanese/pull/1)、[PWAの導入・license修正](https://github.com/Aero123421/dsh-pwa/pull/2)
