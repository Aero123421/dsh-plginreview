---
name: dsh-speed-up-perf
description: DSHプラグインの起動、UI、Session、networkと障害中の負荷を計測し、履歴・保存・権限・復旧の意味を保って改善する。
license: MIT
---

# 利用経路の性能改善

遅い操作、対象版、入力規模、時間・CPU・memoryの観測を決めます。大きなfileや疑わしいloopだけでbottleneckと断定しません。

## 平常時と障害時を測る

productionのconsumerを通し、起動、設定、検索、model選択、会話描画を測ります。件数、byte、turn、DOM、cold/warmに加え、idle、offline backlog、再接続、取消後を機能に応じて含めます。同じ環境・入力でbefore/afterとばらつきを比較し、推定を実測値にしません。

[Session表示の規約](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/docs/defensive-patterns/conversation-and-session.md)を確認し、projectionと別の全件fold・Client全log scanを増やしません。streamの高頻度deltaは増分計算とbatchingを確認します。構造・終了通知まで無条件に遅らせる方針ではありません。

## 削減と正しさを別に確認する

不要なsubscription、polling、再描画、重複要求、I/Oを追います。queueが空のときと、通信できないときに読むpayloadを分けます。offline時に解析を減らしてもpending、retry数、復旧後の再送、保存完了を維持します。

cacheは所有context、identity、失効、容量、共有要求・取消、資格情報の分離を決めます。module globalのcacheへ移すだけで速くしません。modelへ渡る履歴や結果を削って達成した数値を、同じ挙動の最適化としません。

negative controlでは古い実装に戻すと測定対象の不要処理が増えることを確認し、同時に外部状態・保存内容が同じであることを検査します。空queueとI/O失敗を同じ値に畳むhelperは、そのエラー契約も読む必要があります。

## 報告

入力、環境、回数、ばらつき、変えなかった挙動、未確認を記録します。OFF/ON・再起動・失敗・取消後の残存資源を必要な範囲で確認します。benchmark閾値や常設CIは維持する目的がある場合だけ追加します。
