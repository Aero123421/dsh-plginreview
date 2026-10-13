# UIと実行環境の実装比較

Sidebarを追加するもの、terminal UIを起動するもの、DSHを内包するDesktop、別アプリからDSHへ接続するものを分けて見ます。どれも「UI plugin」と呼べますが、profile・process・packageを誰が所有するかが違います。

## Better Sidebar: 拡張用registryを公開する

`dsh-better-sidebar 0.25.0`は、第三者がtabやfile viewerを登録する`ctx.betterSidebar`を持ちます。`registerTab()`・`registerFileViewer()`はdisposerを返し、fiberの解除に結び付く構成です。

registryは同期snapshotとlistenerでReactに公開します。tabの重複は一つの`dedupeKey`で表現し、single-instance、pathごと、change IDごとの違いを統一しています。

viewerはpriority、内容検査、extensionの順で選びます。独自のDOM書き換えを各pluginへ散らす前に、こうした小さい登録APIを使えるか確認します。

根拠: [client service](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/client/service.ts)。

### 名前からfilesystemの権限を推測しない

確認版の`path-security.ts`は、workspace containmentを行わない設計です。`ensureWorkspacePath()`という名前を残していますが、処理は絶対pathへのlexicalな解決です。Host userがOS上で触れるpathを操作できる方針が、ソースにも明記されています。

これは作者が選んだ仕様として扱います。自作pluginへコピーする場合は、自分が必要とする範囲に合うか確認してください。Session IDやcwdがあることだけでは、workspace外を拒否する保証になりません。

`trust-fence.ts`も、Origin・Hostの防御と認証を区別しています。UIから直接呼ぶファイル操作の権限を、model toolのsandboxに自動で委譲できるとは説明しません。

根拠: [pathの解決](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/path-security.ts)、[browser trust fence](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/trust-fence.ts)。

### HTML previewの隔離をfeatureごとに見る

preview用のsandbox tokenは、`allow-same-origin`とtop navigationを含めません。表示するHTMLがDSHのoriginでSession情報を読むことを避ける構成です。

ただし、viewerの種類や設定によってsandbox解除の可否が違います。共通定数があるだけで、すべてのpreviewが同じ条件で隔離されると判断しないようにします。

根拠: [previewのsandbox定義](https://github.com/omdsh-dev/DSH-better-sidebar/blob/d0a47bed1175e8214fc45bacf8535cc0b4d386a0/src/client/html-preview.ts)。

## DSH TUI: terminal UIとbackendの契約を分ける

`@deepseek-harness-tui/dsh-tui 0.14.0`は専用のTUIです。DSH Webの設定画面へClient部品を足す構成と同じ導入先を想定しません。

backend registryとbackend admissionを分けています。宣言のschemaが正しいことに加え、Hostが対応する能力、予約ID、permission名とgrantを照合します。知らない名前を設定に書けることと、そのHostが実行できることは別です。

この契約や`@dsh-std/*`の依存は、そのプロジェクトの実装として読んでいます。DSH本体の共通APIに同じ契約があるとみなして、自作pluginの必須依存にしません。

根拠: [backend admission](https://github.com/ccch1mneyyy/dsh-TUI/blob/e30a8ca9a88e536ad5096445cb1c3f29e6f35908/src/dsh-adapter/backend-admission.ts)、[backend registry](https://github.com/ccch1mneyyy/dsh-TUI/blob/e30a8ca9a88e536ad5096445cb1c3f29e6f35908/src/dsh-adapter/backend-registry.ts)。

### patch・entry・依存解決を一緒に確認する

TUIのpatchは、workspace、scene、panelなどのserviceと、起動するfront doorを順序付けます。deploymentのprovider、effort、preset、backendと、保存済みの選択の優先も指定します。

patchには、module側へ必須serviceを増やすと、旧patchと新moduleの組合せで起動待ちになる問題への対応が記録されています。コードだけを更新して、保存された構成や配布patchが必ず同じ版になるとは考えません。

また、間接依存をprofile直下からbare名で読めない配置に備え、自分のpackageの公開subpathから読み込むentryがあります。npmの平たい配置で通っても、pnpmで同じとは限らない例です。

根拠: [TUIのpatch](https://github.com/ccch1mneyyy/dsh-TUI/blob/e30a8ca9a88e536ad5096445cb1c3f29e6f35908/cordis.patch.yml)。

この版のmanifestはDSH `0.2.1-alpha.2`とのpeer条件に不一致があります。npm tarballのentryは確認できましたが、このDSH版でTUIを起動した検証結果ではありません。

## DSH Desktop: 起動元がprofileとpackage操作を所有する

`anywhere-labs/dsh-desktop`は、stable、beta、nextなどのeditionと、同梱DSH runtime、market、profile管理を含むworkspaceです。既存DSH Webへ小さいpluginを足す例とは、配布・起動の責任が違います。

`createDesktopProfileBoot()`はprofile名、directory、home、package-managerのidentityが一致することを検査します。互換性検査が見るmanifestも、実際にmodule loaderが選ぶcopyと揃えます。

package操作とHMRは、このlauncher情報を経由します。plugin側でprofile pathを推測して外部pnpmを呼ぶと、shellのoverlay、無効bundle、market provider、admissionの条件を失う可能性があります。

根拠: [profile context](https://github.com/anywhere-labs/dsh-desktop/blob/7abe94dd037450f8ebaae71d938b8dad2f125610/dsh-plugin-desktop/src/profile-context.ts)。

### 復旧は設定snapshotとruntime差し替えを分ける

healthy-start checkpointは3slotを保持し、対象にした宣言的fileを保存します。復旧処理はpnpmを起動せず、node_modulesをコピーしません。復旧直後の正常起動でcheckpointを上書きしないためのmarkerもあります。

記録にはproduct版、edition、同梱DSH版などのidentityを持ちます。別editionや別配布物のcheckpointを、file名の一致だけで取り込まないための観点です。

「戻す」操作を作るときは、何のfileが戻り、実行runtimeと依存がどうなるかを示します。設定が復旧できることは、更新前のすべての副作用を戻せることとは違います。

根拠: [checkpoint](https://github.com/anywhere-labs/dsh-desktop/blob/7abe94dd037450f8ebaae71d938b8dad2f125610/dsh-plugin-desktop/src/profile-checkpoint.ts)、[channel admission](https://github.com/anywhere-labs/dsh-desktop/blob/7abe94dd037450f8ebaae71d938b8dad2f125610/dsh-plugin-desktop/src/profile-channel-admission.ts)。

## Open Design: DSHを別アプリから操作する接続bundle

リポジトリ全体は別アプリですが、`packages/dsh-runtime`にはDSH bundleがあります。stdio上のJSON frameで、probe・model一覧・execute・cancel・resumeを扱います。

protocol version、runtime名、plugin version、capabilities、request IDを明示します。daemon側でもframeを検証し、model catalogではprovider、model ID、推論強度を読んでいます。

stdoutへ診断文字列を混ぜず、probeはちょうど一つのframeであることを確認します。曖昧なログを読んで接続済みと判断する代わりに、起動したruntimeのidentityを照合する例です。

根拠: [runtime protocol](https://github.com/nexu-io/open-design/blob/0bd8251c9b5c0bed4b3aef87f53f9c1eadc493c7/packages/dsh-runtime/src/protocol.ts)、[DSH entry](https://github.com/nexu-io/open-design/blob/0bd8251c9b5c0bed4b3aef87f53f9c1eadc493c7/packages/dsh-runtime/src/index.ts)、[probe parser](https://github.com/nexu-io/open-design/blob/0bd8251c9b5c0bed4b3aef87f53f9c1eadc493c7/apps/daemon/src/agent-protocol/dsh-profile/probe.ts)。

この調査では`@open-design/dsh-runtime@0.1.0`を公開npmから取得できませんでした。ソースのpackage名があることを、一般利用者向けnpm導入手順が存在することの証明にはしません。

### 内部の版一致と上流への追従を別々に検査する

上流drift確認scriptは、installerと自分のruntime定義が両方同じ古い版を指していると、内部比較のテストだけでは見落とす問題を扱います。公開registryと比較し、installer、runtimeが受け入れる版、peer条件を一緒に確認します。

これを持ち帰る場合は、「固定した互換版で動く」確認と、「新しい上流版が出たことを検知する」確認を分けます。新しい版を検知したことだけで、自動的に対応範囲を広げません。

根拠: [上流drift確認](https://github.com/nexu-io/open-design/blob/0bd8251c9b5c0bed4b3aef87f53f9c1eadc493c7/.github/scripts/dsh-upstream-drift.ts)。通知するscript自体は今回実行していません。

## 自作UIへ持ち帰ること

- tab・viewer・設定欄は、宣言とdisposerを持つ小さいAPIにする。
- filesystem操作とHTML previewの権限を、表示部分とは別に確認する。
- 起動するbackend、保存済みmodel、deployment defaultの優先順位を決める。
- profile・home・package copy・runtime版をlauncherの情報から決める。
- 外部接続ではidentityとcapabilityを検証し、文字列ログだけで起動成功にしない。
