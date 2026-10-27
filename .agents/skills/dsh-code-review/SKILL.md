---
name: dsh-code-review
description: 独立したDSHプラグインのPR・commit・差分をレビューし、現行API、解除、権限、保存、配布と検証の問題を根拠付きで報告する。
license: MIT
---

# プラグインのレビュー

live base/headを確認し、要求と所有する契約を読んでからdiff・consumerを追います。レビューだけなら修正・push・Issue投稿・merge・releaseへ広げません。

## 版と根拠を固定する

2026-10-15時点の固定ソース記録はDSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`であり、最新基準ではありません。公開Release、開発branch、実インストール版、packageの宣言を分けます。[本家レビュー規約](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-code-review/SKILL.md)の専用コマンドや承認経路を、独立repoにもあると仮定しません。

## 追う経路

- manifest、patch、Host/Client entry、公開exportsから実際のLoader、agent schema・dispatch、UIへつなぎます。手でmountしたmockだけで公開経路の互換性を判断しません。
- 呼出し、境界入力、保存、外部副作用、表示、取消、解除を追います。Hostが固定するprincipal/Peer、method/resource、直接HTTP、一覧・streamを区別します。
- 非同期の認証・接続・編集の世代を照合します。古い成功だけでなく古い失敗、同期throw、途中切断も検査します。
- resource取得から、受け付け済みconsumerの最終利用・保存・結果通知が終わるまで所有を追います。abort/killだけ、injectだけで解除順を保証したとしません。
- Session由来の値をprojectionと別に保持して二重の正本を作っていないか、動的prompt値がresume時に履歴prefixを変えないかを確認します。
- 更新は候補、削除、導入、実行版、Client反映を分けます。alpha.3のHMR下の `already-installed`、削除後の失敗、自己解除、nullの照合結果を試験の条件へ含めます。
- 共有namespace、CSS、route、tool、processは登録順・OFF/ON・復元を確認します。pathは生成側と解釈側の基準を比較し、別の同名fileを正常に開く誤りも対象にします。

## 指摘と検証

動作不良、データ損失、権限、解除漏れ、配布不能を優先します。指摘にはfile・行、到達可能な条件、観測結果、根拠、修正後に守る性質を付けます。上流がP0と呼ぶ規則を、そのまま全pluginの重大度にしません。

回帰試験は未修正側で意図した失敗になるかを確認します。新しいテストfileが存在しないためrunnerが失敗しただけでは、動作の判別力は証明されません。受け入れる例と拒否すべき反例、wrapperを通らない入口も確認します。

作者報告、コード読解、自分の再現、公開物、利用者確認を分けます。mockが上流の新しい拒否結果を再現しているかを見ます。環境要因という説明には同じbaseでの対照を求め、関係ないstyle指摘を障害件数へ足しません。

head/base、先行PR、生成物が変わったら、無効になった指摘と検証だけを見直します。closed、merged、devへmerge、公開済みは同じ状態ではありません。
