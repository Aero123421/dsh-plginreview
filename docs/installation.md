# インストールとパッケージ構成

導入手順は、DSHのプラグイン管理画面と`dsh plugin`を基本にします。利用者にprofileの内部ファイルを手編集させる方法は、通常の導入手順にはしません。

## UIから入れる

「プラグイン → プラグインを追加」の入力欄には、パッケージ指定を入れます。CLIコマンド全体は入力しません。

公開済みGlass UIの例です。

```text
github:Aero123421/dsh-glassui#v0.2.2
```

インストール結果に従って有効化・再起動します。確認版のDSHでは、インストール済みパッケージを差し替えた場合に`restart-required`を返します。

Web版で再起動が必要な場合は、DSHサーバーを終了・起動し直してからブラウザーを再読み込みします。ブラウザーの再読み込みだけでは、HostのClient metadataキャッシュは更新されません。標準詳細が新しい版・Runningでも、新しい設定欄が出ない場合があります。[再現例と確認手順](update-and-restart.md)を参照してください。

## CLIから入れる

Web profileを指定します。

```sh
dsh plugin --profile web add -w github:Aero123421/dsh-glassui#v0.2.2
```

`-w`はpnpm workspace rootへの追加を明示します。PWAの導入で`ERR_PNPM_ADDING_TO_ROOT`が発生したため、各プラグインの公開手順ではこの形を使っています。すべてのDSH版・profileでこのエラーが出るという意味ではありません。

画面やプラグインの更新ボタンは、CLIに書いた`-w`を引き継ぐ操作ではありません。DSH `0.2.1-alpha.2`とpnpm `11.7.0`で画面側に同じエラーが出た場合の対処は、[対象profileのworkspace設定](update-implementation.md#dshとpnpmの導入条件)にあります。

確認版のCLIは新規bundleを有効化しますが、既存依存の差し替えではOFFのbundleを再有効化しません。根拠は[package操作のreconcile](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/operations.ts)です。一方、更新ボタンが呼ぶ`installBundle()`は`enabled`を省略すると有効化するので、更新前の値を明示します。CLIとこのAPIの既定値を混同しないでください。

OFF中はプラグイン独自の設定欄が出ません。標準画面も、Hostから`installTarget`がある項目だけに更新操作を出します。第三者pluginのすべてに標準更新ボタンがある前提で案内せず、利用できない場合は元の導入元を指定したCLIを使い、更新後のON/OFFを確認します。

タグを省略すると、取得時のリポジトリの既定ブランチを使う指定になります。再現可能な導入には、公開済みのタグまたはコミットを指定します。

## 入力できる形式

`OWNER`、`REPO`、`VERSION`、`PACKAGE`、パスは、自分の配布物に置き換える例です。

| 形式 | 入力例 | 用途・注意 |
| --- | --- | --- |
| GitHub | `github:OWNER/REPO#vVERSION` | GitHub上のソース一式から導入 |
| npm | `PACKAGE@VERSION` | npmに公開済みの場合 |
| Releaseのtarball | `https://github.com/OWNER/REPO/releases/download/vVERSION/PACKAGE-VERSION.tgz` | ビルド済み配布物から導入 |
| ローカルディレクトリ | `/absolute/path/to/plugin` | 開発・手動配置 |
| ローカルtarball | `/absolute/path/to/PACKAGE-VERSION.tgz` | ダウンロード済み配布物から導入 |

画面に入れるローカルパスは絶対パスを使います。CLIは実行したディレクトリを基準に相対パスを解決します。

DSH Webを別のPC・サーバーで動かしている場合、ローカルパスはそのDSH Host側のパスです。ブラウザーを開いている端末のファイルを、この入力欄からアップロードする機能ではありません。

レジストリの選択はnpmパッケージと依存の取得先に関わります。GitHubリポジトリやRelease URL自体を、npmミラーから取得する指定にはなりません。

## DSHが導入できるbundleにする

Cordisのplugin entryがあるだけでは、DSHの管理画面で導入・有効化するbundleの宣言になりません。確認版では`dsh.bundle.patch`でprofileに加えるpatchを指定します。

次は名前を置き換えて使う構成例です。DSHやClientへの依存宣言、metadata、設定schemaは、実際に使うAPIに合わせて追加します。

```json
{
  "name": "dsh-example",
  "version": "0.1.0",
  "type": "module",
  "exports": {
    ".": "./dist/index.js",
    "./client": "./dist/client.js",
    "./package.json": "./package.json"
  },
  "files": ["dist", "cordis.patch.yml", "README.md", "LICENSE"],
  "dsh": {
    "bundle": { "patch": "./cordis.patch.yml" }
  }
}
```

```yaml
- insert:
    - id: dsh-example
      name: dsh-example
```

Clientを持たないプラグインには`./client`を追加しません。Clientを持つ場合は、実装に必要な`dsh.client.platform`と`inject`なども宣言します。例のJSONだけでHost・Clientの連携が完成するわけではありません。

`id`は他のプラグインと衝突させず、設定namespaceとして使う場合はClient側と一致させます。共有ライブラリや通常のnpmパッケージを、bundleとして誤って案内しないでください。

## GitHub指定で配るとき

利用者の環境でビルドが実行されることを前提にしません。今回のPiログイン、日本語化、Glass UIでは、`exports`が指すビルド済み`dist/`をGitに含め、GitHub指定で導入できるようにしました。

`package.json.files`はpackされる範囲の指定です。ローカルの未追跡`dist/`がGitHubにも存在することの証明にはなりません。Gitで追跡されているか、公開タグに入っているかも確認します。

PWAのように実行可能なJSを直接同梱する構成なら、不要なビルド工程を追加する必要はありません。必要なのは、配布先のentryが実際に存在し、DSHから読めることです。

生成物をGitに入れる場合は、固定した依存から再ビルドし、追跡された生成物と一致するCIを置きます。フォント、画像、第三者ライセンスもpackの対象に含めます。

外部pluginには、Gitに生成物を置かず、`prepare`で生成する構成もあります。その場合はbuildに必要な依存と許可、profileからの解決を含めて検証します。[外部packageの確認結果](ecosystem/package-checks.md)では、Gitのentryとnpm tarballのentryを別々に調べています。

## 最後に試す導入経路

1. 新しい隔離環境のWeb profileへ、公開予定タグと同じ内容を導入する。
2. Host entry・Client entry・設定ページ・ツールが実際に登録されることを確認する。
3. 無効化、再有効化、削除、再起動を確認する。
4. 配布する`.tgz`でも同じ確認を行う。
5. 旧版の設定を持つprofileで更新し、資格情報・設定・ON/OFF状態を確認する。

workspace symlinkや開発用node_modulesを使った確認だけでは、配布物の確認を代替できません。

上のGlass UI `0.2.2`指定は公開タグ・package・実装側の配布smoke報告を照合しています。この文書更新でコマンドを再実行した結果ではありません。各プラグインの現在の導入元・更新入口は[一覧](own-plugins.md)を参照してください。

## 根拠

- [DSHのinstall-spec parser](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/install-spec.ts)
- [DSH plugin manager](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/README.md)
- [PiログインのGitHub導入修正](https://github.com/Aero123421/dsh-pi-login/pull/8)、[日本語化の修正](https://github.com/Aero123421/dsh-japanese/pull/1)、[PWAの導入修正](https://github.com/Aero123421/dsh-pwa/pull/2)
