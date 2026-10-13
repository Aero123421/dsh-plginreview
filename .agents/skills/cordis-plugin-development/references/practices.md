# 拡張点と共存

service、provider、event、tool、slotの最も小さい拡張で目的を満たします。保存状態とmodel-visible情報の所有者を確認し、plugin内cacheを永続記録の代わりにしません。

## scopeと権限

global登録の成功は、agentのtool一覧へ出ることの証明ではありません。同名のscoped toolやrestrict、親子Sessionの選択を含めて、実際のschemaとdispatchを確認します。

ツールを減らすrestrict、拒否を追加するguard、引数や結果を書き換えるwaterfall、prompt全体のassemblyは影響が異なります。利用者が求めた動作を満たす範囲を選び、他pluginの拒否を緩めません。waterfallを委譲するときは `next()` を呼び、decisionの関係ないfieldを維持します。

UIやログイン追加を理由に、persona、context gate、token saver、agent loopの変更まで同時に入れません。モデル動作を変える機能はその目的と確認を分けます。

## 所有と非同期処理

process handle、route、CSS、設定namespace、credential key、callback、timerの所有を列挙します。pluginのOFF、接続の再生成、Session終了、service停止は別の寿命です。

古い接続・認証試行・編集の完了を、現在の状態へ反映しません。generation、request ID、candidate ID等は、識別すべき操作に合わせます。値が同じという比較だけで別の編集を同一視しません。

共有DOM/CSS変数の復元は、自分が設定した値をまだ所有する場合に限ります。設定は最新値の対象fieldへ更新します。別pluginの登録やクラウド資源を名前の一致だけで削除しません。

## 併用確認

共有する資源がある組合せを選び、A→BとB→A、片方のOFF/ON・reloadを確認します。proxyはHost/Origin等の管理元判定を変えないこと、PWAは他worker/cacheを一括削除しないことも、対象機能に応じて確認します。

基準となる実例は[共存の調査](https://github.com/Aero123421/dsh-plginreview/blob/main/docs/plugin-coexistence.md)、設計の比較は[横断分析](https://github.com/Aero123421/dsh-plginreview/blob/main/docs/ecosystem/deep-patterns.md)にあります。全組合せの試験を毎回要求せず、今回共有・変更した境界から選びます。
