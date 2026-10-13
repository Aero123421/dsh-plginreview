# 他プラグインとの干渉を避ける

DSHでは複数のpluginが、同じ画面、locale、tool registry、設定、接続を使います。自分だけで動くことに加えて、「他の登録を消さない」「後から届いた古い応答で上書きしない」「自分をOFFにした後に残さない」を確認します。

2026-10-13 JSTの[自作7プラグイン](own-plugins.md)の主要処理を比較しました。以下の実装例は固定コミットを参照しています。「提案」「確認項目」は今後の設計・検証であり、7つを同時起動して通過した結果ではありません。

## 名前と所有範囲を決める

| 対象 | 実装で確認した名前・扱い | 気を付ける点 |
| --- | --- | --- |
| Piログイン | slot ID `dsh-pi-login`、route `dsh-pi-login/*`、credential scope `llm-pi-ai` | package名と保存scopeは同一とは限らない。scopeを見た目の統一だけで改名しない |
| 検索プロバイダー | slot ID `web-search-provider`、locale `dsh.searchProviders`、追加tool `x_search`等 | 名前付きproviderの追加と、同名toolの登録は別の競合になる |
| 日本語化 | `ja`言語、DSHの各namespaceの日本語辞書、`data-dsh-japanese`のstyle | 既存namespaceへの翻訳追加は意図した共有。言語そのものを重複登録しない |
| PWA | `/manifest.webmanifest`、`/pwa/*`、HTML headへのmeta追加 | route名とmetaは共有面。prefixだけではmanifest・theme-colorの競合を解決できない |
| Remora | 更新対象package `dsh-remora`、ローカル操作の独自判定 | proxyで実際の接続元・Hostを変えると、権限判定まで変わる |
| Glass UI | `data-glassui-*`、`--glassui-*`、`glassui-*`クラス | DSH全体の色・レイヤーを扱うため、独自prefixがあっても画面全体に影響する |
| CF | `/dsh-cf/*`、profile内`.dsh-cf/`、所有した資源のID | DSHの接続許可とクラウド資源は共有。自分が所有する範囲だけを変更する |

新しいpluginではroute・event・slot ID・credential・保存key・CSSを先に一覧化します。tool名など外部に公開済みの名前を後から変える場合は、保存された設定やSessionへの影響も扱います。名前が衝突しそうだからという理由で、既存の利用者に黙って改名しません。

## 登録の解除を所有者へ結び付ける

日本語化の[Client](https://github.com/Aero123421/dsh-japanese/blob/c6bb53790233c171f6854820f89e87205abf5b51/src/client.jsx)は、自分で作ったstyle要素を保持し、解除時にその要素だけを取り除きます。既存実装の要点は次の形です。

```js
ctx.effect(() => {
  const style = document.createElement('style');
  style.dataset.dshJapanese = '';
  style.textContent = fontCss + japaneseTypography;
  document.head.append(style);
  return () => style.remove();
});
```

`document.querySelectorAll('style')`でまとめて削除すると、DSHや別pluginのCSSも消えます。自分のselectorであっても、複数instanceが作った要素をすべて消す処理は、もう一方のinstanceを壊します。原則として作成時の参照・返されたdisposerを保持します。

同じようにtimer・observer・RAF・network request・processの所有者を決めます。Cordisが登録APIの内部で解除を管理するものと、呼び出し側がdisposerを保管するものを確認し、API名だけから推測しません。waterfallで処理を委譲する経路は`next()`を呼びます。

## UIのCSSは適用範囲と解除を両方確認する

設定UIは自分のroot class以下へCSSを限定します。`button`、`input`、`dialog`、`[role=tab]`を全ページへ一律適用しないようにします。Portalで表示するmenuはrootの外に出る場合があるので、Portalの内容にも自分のclassを付けるか、DSHの正式な部品を使います。

Glass UIの[DOM名](https://github.com/Aero123421/dsh-glassui/blob/3a062be9a5e0e7a2b0f81a95e38b9e6d71620f37/src/shared/dom.ts)には、公開された除外属性`data-glassui-ignore`と、明示的な適用属性`data-glassui-material`があります。他pluginの特殊なpreviewなどを除外する使用例です。

```html
<section class="dsh-example-preview" data-glassui-ignore>
  <!-- この領域と子孫をGlass UIの処理対象から外す -->
</section>
```

すべての設定UIを一律に除外する必要はありません。通常はDSHのtheme tokenで馴染ませ、特殊な描画だけを除外します。この属性は確認版のGlass UIとの取り決めで、DSH標準の全theme共通APIではありません。

[DynamicSheet](https://github.com/Aero123421/dsh-glassui/blob/3a062be9a5e0e7a2b0f81a95e38b9e6d71620f37/src/client/engine/sheet.ts)も、自分のstyleだけを書き換えて解除します。テーマを止めるときに、開始時に保存した`documentElement.style.cssText`全体を戻す方法は避けます。その間に別pluginや利用者が加えた変更まで失われるためです。

既存のDOMへinline propertyを書かざるを得ない場合は、次のように限定して復元する案があります。これは新規実装用の例です。

```js
function setOwnedProperty(element, property, value) {
  const oldValue = element.style.getPropertyValue(property);
  const oldPriority = element.style.getPropertyPriority(property);
  element.style.setProperty(property, value);
  const written = element.style.getPropertyValue(property);
  const priority = element.style.getPropertyPriority(property);
  return () => {
    if (element.style.getPropertyValue(property) !== written ||
        element.style.getPropertyPriority(property) !== priority) return;
    if (oldValue) element.style.setProperty(property, oldValue, oldPriority);
    else element.style.removeProperty(property);
  };
}
```

この比較でも、別pluginが偶然同じ値を書いた場合の所有者は判別できません。まず専用のclass・CSS変数を使い、複数の書き手が必要なら共有側に所有者を管理する仕組みを置きます。比較して戻す方法だけで、完全に安全な多重上書きを保証しないでください。

MutationObserverは自分のstyle変更を繰り返し観測しないよう、対象attribute、差分判定、処理回数を絞ります。theme切り替え、日本語切り替え、設定panelの開閉を組み合わせて、再描画が止まることを確認します。

## 翻訳・fontは利用者の選択を優先する

日本語化の[実装](https://github.com/Aero123421/dsh-japanese/blob/c6bb53790233c171f6854820f89e87205abf5b51/src/client.jsx)は、`ja`が未登録のときだけ言語を追加し、fontを`html:lang(ja)`に限定しています。text/code fontには利用者の指定を参照するCSS変数があります。

新しいpluginのUI文言は、そのpluginのlocale namespaceに置きます。日本語化pluginがあることを前提にせず、自分の文言のfallbackも用意します。翻訳の追加と、言語選択の強制変更は別の処理です。モデル出力・ユーザー入力・wire IDを翻訳したり、システムプロンプトに日本語応答指示を追加したりしません。

DSH本体や別の言語パックが同じnamespaceの`ja`を提供する場合は、確認版locale APIの優先順位・解除時の動作を確認します。「先に`ja`が存在するか調べる」だけでは、辞書ごとの衝突まで解決したことにはなりません。

## providerを追加し、共有toolをむやみに再登録しない

検索プロバイダーの[Host](https://github.com/Aero123421/dsh-search-providers/blob/ca7a1e484cd25e1812fc333c85b0185a40659e49/src/index.ts)は、標準`web_search`を同名で作り直さず、`ctx.web.registerSearchProvider()`へ実装を追加します。標準toolの出力・表示・引用処理を利用でき、他の検索pluginと分担する境界も明確になります。

一方、[追加ツール](https://github.com/Aero123421/dsh-search-providers/blob/ca7a1e484cd25e1812fc333c85b0185a40659e49/src/tools.ts)は`x_search`、`search_news`などの名前で登録します。内部のregistration keyが`capability:provider`であっても、別pluginが同じtool名を使う問題は残ります。これらの衝突が実起動で確認済みという意味ではなく、併用テストが必要な境界です。

同じtool名を持つ構成では、対象DSHの重複登録時の仕様を確認し、利用者が片方を選べるようにします。無断で既存toolを解除したり、「後に登録した方が勝つ」と決め付けたりしません。新規tool名のprefixは選択肢ですが、既存名の変更には互換性の検討が必要です。

既定の検索providerを変更する処理は、利用者が選んだときに実行します。pluginの起動・更新・再有効化をきっかけに、他pluginで選択した既定値を毎回上書きしません。

## 保存設定とcredentialを共有領域ごと上書きしない

Piの[起動処理](https://github.com/Aero123421/dsh-pi-login/blob/2c47c82880c0f2f8f8f1dd433369acd50478259d/src/index.mjs)は、既存provider設定を一度だけ取り込み、元設定を残しています。credential scopeも`llm-pi-ai`を維持しています。表示名に合わせて保存keyを変えると、既存ユーザーがログアウトしたように見えるためです。

設定更新は、自分のnamespace・対象fieldへ絞ります。revision付き更新で競合を検出できる場合は使い、競合したら再読込・再適用・利用者への通知のどれを行うかを決めます。起動時のsnapshot全体を後から保存すると、その間の他pluginの変更が消えます。

CFの[DSH adapter](https://github.com/Aero123421/dsh-cf/blob/5da69eb4458640ec8f9e62b71f2982b5dee8cbda/src/dsh.js)は、`trustedHosts`を変更する際に現在値へ追加し、配列だけでなく既存の式形式も考慮しています。解釈できない形式なら上書きせず失敗させます。共有設定を扱うときの参考になります。

credentialの削除対象はplugin・provider・accountなど、保存時に決めたkeyで指定します。全credentialの削除、別profileの資格情報を探して移す処理、診断へのsecret値出力を避けます。PiとDSH標準が同じ表示名のproviderを扱っても、同じcredentialを共有するとは限りません。

## 依存packageの別コピーを持ち込まない

[Piのpackage](https://github.com/Aero123421/dsh-pi-login/blob/2c47c82880c0f2f8f8f1dd433369acd50478259d/package.json)や[検索のpackage](https://github.com/Aero123421/dsh-search-providers/blob/ca7a1e484cd25e1812fc333c85b0185a40659e49/package.json)は、CordisやDSHのサービスpackageをpeerとして宣言しています。pluginが必要とするSDKの版と、Hostが提供する版の境界が確認できます。

peer条件とbundlerのexternal指定は別々に確認します。peer宣言があっても、buildでHost用SDKやReactを別コピーとして埋め込めば、共有すべきContext・型の識別・hookの実体が分かれる可能性があります。対象DSHのLoaderに合わせて共有し、公開物を空のprofileへ導入して確認します。

「型チェックを通すため」にDSHの依存を利用者のprofileごと上書きしたり、無関係なpluginのpeer条件を変更したりしません。DSHの版に互換性がなければ、その版に合わせたpluginを選ぶか、必要な更新を明示します。

## 接続の再生成とpluginの停止を区別する

CFの[Host登録](https://github.com/Aero123421/dsh-cf/blob/5da69eb4458640ec8f9e62b71f2982b5dee8cbda/src/index.js)は、controllerをrootに置き、ConnectionとWebServerに依存するrouteだけを子の依存範囲へ置いています。許可Hostの設定変更によってConnectionが再生成されるため、controllerまで同じ寿命にすると、その変更を進めている処理自身が停止し得ます。

```js
// CFの構造を簡略化した例。createController/registerRoutesは説明用の関数。
const controller = createController(ctx);
ctx.effect(() => () => controller.dispose());
ctx.inject(['connection', 'webServer'], child => {
  registerRoutes(child, controller);
});
```

長く生かすのは必要なcontrollerだけです。接続ごとの要求・購読は接続が終わったら解除し、旧接続の結果を新接続のUIへ反映しません。逆にplugin自体をOFFにした場合は、rootのcontrollerも確実に停止させます。

共有profileに対する更新・設定保存は、DSHのmanager・settingsを通します。プラグインごとに直接pnpmを起動したり、profileファイルを書き換えたりすると、他pluginの更新処理と競合します。UIの連打防止だけでは、別の画面・pluginから始まった処理は制御できません。

## proxyで権限判定を変えない

Remoraの[route](https://github.com/Aero123421/dsh-remora/blob/ed7e99736b0cc8e72a956722fb6fc72fda927239/packages/dsh-remora/src/routes.ts)は、loopback接続だけでなくHost、Origin、転送元headerなどを使ってlocal操作を判定します。CFの[gate](https://github.com/Aero123421/dsh-cf/blob/5da69eb4458640ec8f9e62b71f2982b5dee8cbda/src/gate.js)は、公開側のHost・Originを保持する構成です。

この組み合わせで期待する動作は、CF経由でDSHを閲覧できても、Remoraのlocal限定更新がremoteから許可されないことです。接続を通すためにHostを`localhost`へ書き換えたりOriginを削ったりすると、別pluginの管理元判定も変わり得ます。実際のHTTP/WS経路で拒否を確認する必要があります。

PWAのmanifest・iconをCF経由で使う場合も、認証を回避する別の公開経路を追加して解決しません。公開origin、scope、認証後の取得、既存ホーム画面からの起動を確認します。PWAの確認版はservice workerを登録しないため、他pluginのworker・cacheを一括消去する理由はありません。

## process・クラウド資源の所有を確認する

CFの[保存処理](https://github.com/Aero123421/dsh-cf/blob/5da69eb4458640ec8f9e62b71f2982b5dee8cbda/src/store.js)では、profileごとのlockと所有情報を扱っています。プロセス名が同じという理由で`cloudflared`をすべて止めたり、表示名が似ているTunnelを引き継いだりしない構造です。

新しいpluginも、自分が起動したprocess handle・所有token・資源IDを持ちます。停止時にPIDだけを見る方法は、終了後のPID再利用を考慮する必要があります。共有ディレクトリの削除や、他profileのプロセス停止をcleanupとして行わないようにします。

RemoraのhubとCFのTunnelは、どちらもCloudflareを使っていても別の資源です。片方の停止・更新で、もう片方のdeploy・DNS・認証を変更しません。

## 併用確認の優先順

以下は追加すべき検証です。この調査で全組み合わせの実起動を確認したわけではありません。

| 組み合わせ | 操作 | 期待する結果 |
| --- | --- | --- |
| 日本語化 + Glass UI | 言語・theme・font設定の変更、片方のOFF/ON | 指定言語・fontを維持し、片方のCSS解除で他方を消さない |
| Glass UI + Pi/Search/Remora | 狭い設定panel、Portal、keyboard、効果OFF | menuと選択表示がずれず、閉じる・保存・更新を操作できる |
| Pi + 標準/別provider plugin | 同名providerの接続、片方のOFF、再接続 | credentialとmodel選択を取り違えず、片方の解除で他方を消さない |
| Search + 別検索plugin | 既定provider変更、同名追加tool、片方のOFF | 既定値を取り戻さず、tool重複を利用者が解決できる |
| CF + Remora | 公開URLと直接localから同じ管理操作 | Remoraのlocal限定操作が公開経由では拒否される |
| CF + PWA | 公開URLから追加・再起動・認証期限切れ | 正しいoriginで再認証でき、認証を回避するrouteを生まない |
| PWA + 別manifest/theme plugin | route・head要素・theme-colorの併用 | 競合を検出し、どちらを使うか決める。重複を放置しない |
| 複数の更新UI | 同時更新、途中切断、片方の取消、DSH再起動 | 操作IDを取り違えず、他の導入を成功・取消扱いしない |

同じ組み合わせでもA→BとB→Aの起動順、片方だけの再読み込みで結果が変わることがあります。主要な衝突候補について、両順序とOFF/ONを確認します。全21組を毎回実行するより、共有する資源と今回変更した境界から選ぶ方が、不具合の原因を追いやすくなります。
