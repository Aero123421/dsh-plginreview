---
name: dsh-client-ui-ux
description: DSHプラグインの画面を設計・レビューし、既存UI、内容幅、locale、theme、権限、保存・失敗状態への適合を確認する。
license: MIT
---

# DSHに合わせたUI

対象DSHの同じ種類の画面とslot・props・tokenを確認します。panel、page、sidebar、overlayの置き場を決めてから実装します。

## 表示と入力

既存の色、文字サイズ、weight、余白、角丸、row、iconを使います。primitiveの公開module契約を確認し、injectだけでimport可能とは判断しません。Host SDKや別コピーのReactをClientに埋め込みません。

文字・ラベル・tooltip・accessibility textはlocaleに従います。長い日本語・model名を含め、実際の設定内容幅とライト/ダークで確認します。390 CSS pxのviewportを一次確認の基準にしつつ、狭いpanelの幅を別に扱います。折返し・配置変更を先に選び、全体clipや文字縮小でエラー・主操作を隠しません。

hoverはviewport幅でなく `@media (hover: hover)` で分けます。touchの後にhover用背景が残らないこと、resize後のfocus、不要なmobile keyboardの自動表示を確認します。[本家responsive UI](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-responsive-ui/SKILL.md)が具体的な基準です。

## 操作とfeedback

保存待ちと保存済みを分け、失敗時は入力と既存データを保ちます。古い編集・接続の応答で新しい状態を消しません。主画面が閉じる操作は閉じた後も結果を確認できる既存のfeedbackを使い、残る画面のquery失敗やfield検証はその場で示します。toastをすべての操作へ追加しません。

権限で操作表示を変える場合は[Remote access](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/api/remote-access/README.md)のClient側状態を確認します。表示上の許可とHostの引数付き判断は異なり得るため、実行時の拒否と失効を扱います。

menu・popoverはEscape、外側クリック、focus、Portal、overflow親のclippingを検査します。CSSを自分の範囲へ限定し、observer、timer、Portal、共有theme変更の解除を所有します。登録順だけで他pluginの値を復元しません。

## 確認と報告

保存中・拒否・切断・結果不明、狭い幅、日本語、keyboard、touch、Desktop chromeを変更範囲で確認します。catalogの画像検査を通ったことと実Clientで表示されたことも別です。

画像やGIFは役立つ場合に用意します。buildまでしか確認できなければ実画面未確認と報告し、emulationを実機や実GPUの確認としません。UIの都合で共有の会話計算・Markdown処理に機能固有の分岐を増やさず、公開されたrenderer/slotから拡張します。
