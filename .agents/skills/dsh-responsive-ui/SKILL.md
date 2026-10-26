---
name: dsh-responsive-ui
description: DSHプラグインの狭い画面、長い日本語、折返し、省略、touch/hover、tooltip、resize時のfocusを設計・確認する。
license: MIT
---

# 狭い画面でも操作できるUI

[本家alpha.3のresponsive UI](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/.agents/skills/dsh-responsive-ui/SKILL.md)を独立plugin向けに調整しています。基本の確認viewportは390 CSS pxです。設定panelの実内容幅はそれより狭い場合があるため、viewportとcontainerを別々に記録します。

## 配置と文字

空間の割当てと折返しを先に調整し、その後に省略・icon化・More menuを検討します。主操作・主状態・エラーを隠さず、globalなclip、文字の一律縮小、小さすぎる操作領域で収めません。

titleはできるだけ全文を表示し、必要なら操作群を次の行へ移します。tab・selector・buttonを省略するときも全文への到達手段を残します。重要情報が他に出ない場合は省略しません。長い日本語、model/provider名、異常時の文章で確認します。

## 入力の種類

icon-onlyは意味が明確な操作に限り、localeに従うaccessible nameを持たせます。mouse用補助tooltipをtouch後に残しません。説明を補うtooltipにはtapで開ける経路を用意します。

hover効果は `@media (hover: hover)` で選びます。画面幅だけで端末の入力手段を推測しません。selected、pressed、keyboard focusはhoverと独立して保ちます。

resizeでfocus対象が残る場合はfocusを維持します。意図なくmobile keyboardを自動表示しません。Escape、tab移動、menu/Portalのclipping、拡大文字、保存中・失敗・切断を変更に応じて確認します。

## 証拠

実際のDSH slot内で見ることと、単体storybookやviewport emulationを見ることを区別します。390px未満の要件は製品側で決め、全画面を一律に対応済みとしません。画像は操作の確認に役立つ場合に残し、実端末・GPU未確認を明記します。
