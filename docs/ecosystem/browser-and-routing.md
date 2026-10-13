# ブラウザー操作とルーティングの実装比較

ブラウザー拡張を使うtool、browser runtime、実行時plugin injector、agent presetは、エージェントへの入口と所有する資源が違います。登録するtool名だけで互換性や権限を判断しません。

## BrowserSkill: browser Sessionの所有権を管理する

Tencent/BrowserSkillのDSH bundleは、`@wxg-prc-cpg/browser-skill-dsh-plugin 0.3.2`です。別の`bsk` CLIとブラウザー拡張がある構成で、DSHのbundleだけでブラウザー環境がすべて用意されるとは扱いません。

pluginはSession registry、CLI runner、Sessionごとのqueue、観測service、tool、Clientの観測UIを分けます。lazy toolsは既定で有効で、Skillを使用した後にtoolを公開する経路を持ちます。

根拠: [plugin entry](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/index.ts)。

### model操作と観測を同じSession queueへ入れる

CLI側は一つのbrowser Sessionでの操作を直列に処理します。plugin側でも、modelのtool呼び出しとthumbnail取得などの観測を同じkeyのqueueへ通します。

待機中のBをキャンセルしたとき、BのPromiseが先にrejectしても、実行中のAが終わるまで後続Cを開始しないようにしています。tailはAとBの両方の終了を待ちます。

この点は、外部serviceが直列操作を要求するwrapperで参考にできます。観測だけが別経路で同じ資源に触れると、model側を直列化しても競合します。

根拠: [KeyedExecutor](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/queue.ts)。この待機キャンセル順序は、queue helperを単独で実行して確認しました。

### 単独検証で見つかった同期例外の条件

同じhelperには、callbackがPromiseを返す前に同期throwすると、呼び出し元へ返したPromiseが終了せず、内側のPromiseからunhandled rejectionが出る条件がありました。

最小の入力は次の形です。

```ts
queue.run('session', () => {
  throw new Error('synchronous callback failure')
})
```

原因は、別Promiseのcallback内で`fn().then(...)`を呼び、その同期例外を呼び出し元の`reject`へつないでいないことです。callbackを`Promise.resolve().then(fn)`のようにPromiseの拒否へ変換すると、呼び出し元がrejectし、後続も進むことを確認しました。

これはcallbackが同期throwする場合に限った結果です。通常の`async` callbackからのrejectとは別です。実ブラウザーでこの条件を発生させたことや、productionの各呼び出し元から到達することまでは確認していません。

queue処理を参考実装から移す際には、キャンセル、非同期rejectに加えて、同期例外も境界のテストに含めます。今回、元リポジトリへの修正・Issue投稿は行っていません。

### 所有していないSessionを停止しない

registryは、pluginが作成したSessionと参照しているSessionを区別します。解除処理で、他のエージェントや別pluginが共有daemonに作ったSessionまで止めない方針です。

dispose testは、所有Sessionのみを止めることと、既に無くなったhandleへの停止失敗が、残りの停止を妨げないことを確認する構成です。今回このplugin全体のtest suiteは実行していません。

根拠: [Session registry](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/src/sessions.ts)、[dispose test](https://github.com/Tencent/BrowserSkill/blob/4c8616b12273ac5a22ce4adb494cac941e20de2a/packages/dsh-plugin-browserskill/tests/dispose.test.ts)。

ブラウザーにはlogin済みの状態があるため、接続できること、どのSessionを操作できること、tab・URLの対象、観測画像の保存、停止する所有範囲を別々に確認します。pluginの無効化が、ブラウザー本体や他利用者のSession停止まで意味するとは説明しません。

## Routing Suite: Loaderとmodel入力を変更する

`dsh-routing-suite`のルートは、`@dsh-external/dsh-super-injector 0.3.3`のbundleです。そのほかにrouting presetやgraded modeの構成があります。

injectorはローカルpackageのruntime注入、profileへのinstall、整包reload、entry状態の記録、build生成物の監視などを持ちます。通常のDSH managerの導入経路とは別に、Loader・registry・module cacheを扱う機能です。

根拠: [injector](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/injector/src/index.ts)、[patch](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/injector/cordis.patch.yml)。

### 開発時の便利機能と公開導入を分ける

scaffold・buildの処理には、DSHのソースcheckoutを探し、そのpackageへlinkする経路があります。開発用の環境に依存する処理を、そのまま利用者向けのGitHub導入に使えるとは考えません。

runtime reloadでは、同じpackageの旧fiber、module cache、設定、共有service、失敗時の復帰を調べます。特定版での内部Loaderの挙動を前提にした処理は、上流の公開APIを使う部分より、追従時に調べる範囲が広がります。

起動中のpluginを入れ替えられることだけで、保存済みprofileからの再起動でも同じ構成が復元されるとは判断しません。

### routingはprompt・tool構成の変更として扱う

Router Reactのpresetは、最初の要求で渡す情報・toolを制限し、その後にStandard構成へ進める方針を持ちます。graded modeには追加toolとpre-stepの注入処理があります。

これらは表示だけの変更ではありません。modelへ渡す指示、tool schema、段階遷移、ユーザー確認、能力の公開タイミングを変更します。比較する場合は、同じmodel・task・予算での結果、失敗例、途中再開、注入した内容の履歴を確認します。

今回、自作の認証・日本語化・検索pluginへこのroutingやprompt変更は取り込んでいません。DSHの元の動作を維持する目的と、動作を変更するpresetの採用は、ユーザーの依頼範囲で分けます。

根拠: [Router React preset](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/preset/router-react/preset.yml)、[graded mode entry](https://github.com/yjh051108/dsh-routing-suite/blob/195273352f23bff7f9023ebe2ec0cdbdf9c98f10/graded/src/index.js)。benchmarkや紹介文の改善率は、この調査で再計測した結果ではありません。

## 自作pluginへ持ち帰ること

| 境界 | 確認すること |
| --- | --- |
| browser・worker・daemon | 自分が作った資源だけを止め、共有ownerを区別する |
| queue | model操作・観測・管理操作を含めて順序を保証する |
| callback | 非同期reject、同期throw、解除後の完了を別々に確認する |
| runtime注入 | 一時登録と、再起動後に復元する構成を区別する |
| preset・prompt注入 | 表示変更と分け、model入力・履歴・評価の範囲を示す |
| 内部Loader依存 | 固定したソースと依存箇所を残し、上流更新時に再確認する |
