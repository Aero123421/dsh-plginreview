---
name: dsh-lifecycle-audit
description: DSH/Cordisプラグインの可変状態、live effect、解除中の依存資源を追い、停止後の仕事・保存漏れ・解除順序の問題を根拠付きで監査する。
license: MIT
---

# Cordisの所有と解除を監査する

DSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c` の[本家監査Skill](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/cordis-styling-nitpicking/SKILL.md)を独立plugin向けに調整したものです。別版では実際のCordisを確認します。単なる命名・書式の検査ではありません。

## 所有者を追う

公開plugin entryから、module初期化、service、listener、effect、子process、通信とdisposerをたどります。generated fileの問題は生成元へ帰属させます。関係しないCLIやvendorを今回の不具合対象へ広げません。

確認するのは三つです。module globalやstatic等に可変状態の寿命が隠れていないか。解除後にtimer・process・通信・一時資源が残らないか。consumerの終了に必要なwriter・listener・transportが先に閉じないか。

immutableな定数、純粋関数、意図した永続書込みはlive effectの解除漏れとしません。traceable serviceの `this.ctx` が呼出し側contextを指す点を含め、所有するcontextを具体的に特定します。

## 停止完了まで確認する

新規受付を停止し、受け付け済み処理の最終service利用・結果通知・保存を依存資源が使える間に終え、その後にdrain・releaseします。abort/killの呼出しだけで完了としません。cleanupの一つが失敗しても他の必須解除を飛ばさない経路を確認します。

基準版では同じfiberのdisposerは並行し得ます。injectや逆順登録、top-level generatorのyieldだけで資源が最後まで残るとは判断しません。所有された一つの `ctx.effect(function* ...)` に返された実disposerを集める方法はありますが、既存effectをwrapperで包むだけでは所有が移りません。

providerのwithdrawalがconsumerを待つ方法も、既に独立してdispose中のconsumerを見失う場合があります。root/parent停止では実consumerの終了taskを明示的な所有者が待つか確認します。特定のgenerator形を機械的に全serviceへ要求しません。

## 再現と報告

consumerを最終依存利用の直前で止め、providerの置換または親の停止を始めます。必要資源・listenerがまだ利用でき、disposeが未完了であることを確認し、consumerを進めて実際の最終結果と保存内容を検査してから停止完了を観測します。

通常時、consumerだけの停止、provider置換、親停止のうち変更に届く経路を選びます。sleepや呼出し回数だけで順序を証明しません。

対象entry、consumer、資源所有者、失敗順序、影響、修正、受入条件を報告します。上流のP0ラベルをそのまま適用せず、到達可能性と実際の影響で重大度を決めます。再現未実行はソース上の指摘とし、pattern検索だけで安全性を断言しません。
