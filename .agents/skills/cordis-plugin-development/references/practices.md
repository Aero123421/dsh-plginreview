# 拡張点と共存

確認基準: DSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`。service、provider、event、tool、slotの小さい拡張で目的を満たします。

## Sessionとモデル入力

[Sessionの契約](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/core/session/README.md)を読み、モデルへ渡す内容を記録済みmessage・tool結果等の確認済み入口へ通します。独立pluginは未知のevent typeを `Session.append()` へ追加せず、本体experimental専用 `appendPluginRecord()` を使いません。

Session由来の表示・計算は[projection](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/docs/defensive-patterns/conversation-and-session.md)を確認します。新しいproductionコードに `eventAt()` / `snapshotEvents()` / `ownEvents()` の全履歴scanを足しません。cache missはunknown等の状態にし、Clientで自動的に全log読取りへfallbackしません。Hostに必要なcold readまで一律禁止するルールではありません。

projectionのfoldや保存stateを変えたら `stateVersion` を更新し、resume・forkを検査します。Sessionの保持は明示的な参照と解除で追います。保存完了を約束する処理は、必要な所有serviceのflushをawaitし、そのlistenerを先に閉じません。

[動的prompt値の事例](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/notes/implemented/bug-fix/2026-10-11-process-specific-prompt-values-in-runtime-context.md)のように、port・path変更も過去のprefixを壊し得ます。記録されるruntime contextと安定した指示を分け、旧履歴の意味を無断で変えません。UI追加を理由にpersona、token saver、context gateまで変更しません。

## scopeと権限

global登録成功だけで実agentのtool一覧・schema・dispatchを保証しません。restrict、guard、waterfall、prompt assemblyは異なる影響を持ちます。自分が処理しないwaterfallは `next()` へ渡し、他pluginの拒否や無関係なdecision fieldを保ちます。

[Remote access](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/api/remote-access/README.md)ではHostが所有するprincipalとmethod/resourceを照合します。認証済みというだけでownerへfallbackせず、直接HTTP・一覧・stream・失効後を別に確認します。UIの表示条件だけで認可を代用しません。globalとSession/Workspaceの許可は自動継承されません。

## 所有と非同期処理

process、route、CSS、credential、callback、timerの所有者を列挙します。plugin OFF、接続再生成、Session終了、service停止は別の寿命です。module globalの可変cacheを、contextごとの状態と混ぜません。

[本家のlifecycle監査](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/cordis-styling-nitpicking/SKILL.md)が示す通り、同じfiberの解除が並行すると、consumerの最終保存より先にwriterが閉じる場合があります。必要な資源を保って受け付け済み処理を終え、その後に解除する所有関係を明示します。injectや逆順登録だけで完了順を推測せず、root/parent停止も確認します。

古い接続・認証試行・編集の完了を現在へ反映しません。共有DOM/CSSの復元はまだ自分が所有する値に限り、設定は対象fieldだけを原子的・revision付きで更新します。排他を自前で持つ場合は最新値の読取りから保存までを内側へ置きます。

## 併用確認

共有資源を持つ組合せについてA→B、B→A、片方のOFF/ON・reloadを選びます。別pluginのCSS・worker/cache・process・クラウド資源を名前一致で一括削除しません。全組合せの毎回試験ではなく、今回共有・変更した境界から確認範囲を選びます。
