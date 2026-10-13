# 調査方法と判断の限界

2026-10-13に公開GitHub履歴を調べました。ユーザー指定のGPT-6.1 solを3体使い、認証・モデル・導入、レビュー後の再修正・CI・配布、公式・外部pluginの履歴を分担しました。担当の報告を統合し、件数・時刻・参照先・解決範囲を確認しています。

この章での「確認」は公開記録の確認です。今回の文書編集で、pluginのテスト、実OAuth、実API、外部pluginの起動を再実行したことを意味しません。

## 取得した記録

自作6repositoryについて、Issue、PR、Release、Actions run一覧を取得しました。PRをIssue件数から除外し、Actionsの失敗stepも照合しました。集計は2026-10-13 03:04 UTC時点です。

この集計は最初の調査時点のまま残しています。後から追加した更新操作のprofile分離とPWAの設定欄欠落の事例は、下表の件数や暦時間へ加算していません。7プラグインの現在版・更新Issueの状態は[公開版一覧](../own-plugins.md)、追加確認の取得範囲は[参照元](../sources.md#更新実装後と後続releaseの確認)にあります。

| repository | Issue | PR | merge済みPR | 公開Release | Actions run | failure run |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [dsh-pi-login](https://github.com/Aero123421/dsh-pi-login) | 5 | 3 | 3 | 4 | 54 | 5 |
| [dsh-japanese](https://github.com/Aero123421/dsh-japanese) | 0 | 1 | 1 | 2 | 10 | 0 |
| [dsh-pwa](https://github.com/Aero123421/dsh-pwa) | 0 | 3 | 3 | 0 | 6 | 0 |
| [dsh-search-providers](https://github.com/Aero123421/dsh-search-providers) | 0 | 1 | 1 | 1 | 7 | 2 |
| [dsh-remora](https://github.com/Aero123421/dsh-remora) | 0 | 3 | 3 | 2 | 31 | 1 |
| [dsh-glassui](https://github.com/Aero123421/dsh-glassui) | 0 | 3 | 2 | 1 | 20 | 4 |
| 合計 | 5 | 14 | 13 | 10 | 128 | 13 |

Issueを作らずPRや会話から直した例もあるため、Issue数だけで報告の量や修正の量を測れません。128 runには同じ変更のpushとPR、手動E2E、release、依存更新が含まれます。失敗率を品質点数に変換したり、run数を修正の反復回数と読んだりしていません。

対象runは2026-10-10〜12の短い期間に集中しています。全128 runの`run_attempt`は1でした。同じSHAを使った別run、新しいSHAのrun、同一runの再実行を区別します。GitHubの再実行は元の`GITHUB_SHA`と`GITHUB_REF`を使います。[GitHub Actionsの説明](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)

代表例は、追加修正や責任境界が公開履歴から追えるものを選びました。無作為標本でも、全Issueの監査でもありません。外部はdsh-market 3例、TUI 2例、modlens 1例と、関連する公式discussionを追っています。[外部の事例](ecosystem-cases.md)で一次ソースを示しています。

## 証拠ごとの扱い

| 記録 | 確認できること | 追加の証拠が必要なこと |
| --- | --- | --- |
| Issue本文・comment | 報告した症状、環境、期待値、説明された操作 | 独立した再現、説明の原因が正しいこと |
| commit・diff | 前提の撤回、実装・test・docsの変更 | 変更を決めた会話、変更に使った時間 |
| PR本文 | 作者が報告したレビュー・検証・未確認 | 今回の再実行結果、記載外の実環境 |
| review・inline comment | 記録された審査内容と対象commit | 非公開・ローカルのレビューの有無 |
| Actions run・job | 対象SHA、event、attempt、失敗step、jobの結果 | assertしていない操作、実API、公開物の最終状態 |
| Release・tag・asset | 公開時刻、現在のtag参照、現在のfile一覧 | 過去のasset一覧、利用者への到達、runtimeの動作 |
| 利用者の再確認 | その利用者の条件での更新後の結果 | 別OS・契約・profile・将来版の結果 |

Glass UIの不要asset削除はPR本文の報告と現在のasset一覧で確認しました。削除時刻の監査ログを得たわけではありません。Remoraの画面報告はこの会話にありますが、公開PRに利用者の投稿時刻はなく、公開履歴だけで報告時点を再現できません。

今回見た代表PRではCopilotのquota到達通知とCodeRabbitのskipがありました。それらを「指摘なしの承認」と扱いません。一方、RemoraのPR本文は3agentの相互レビューを報告しており、公開approvalがないことから未レビューとは断定できません。[Remora PR #1](https://github.com/Aero123421/dsh-remora/pull/1)

## 時刻から言えること

履歴の時刻はUTCです。差分は暦時間であり、工数やagentの稼働時間ではありません。

| 観測区間 | 暦時間 | 分かること |
| --- | --- | --- |
| [Pi Issue #1](https://github.com/Aero123421/dsh-pi-login/issues/1)作成→close | 3時間6分43秒 | 公開状態が変わるまでの時間。実装・レビューの内訳は不明 |
| [Pi PR #3](https://github.com/Aero123421/dsh-pi-login/pull/3)作成→merge | 1分48秒 | PR公開後の時間。公開前の調査・実装を含まない |
| [Pi Fast PR #5](https://github.com/Aero123421/dsh-pi-login/pull/5)作成→merge | 4時間16分54秒 | この間に前提の撤回とUI変更があった。待ち時間の内訳は不明 |
| Remora [#1](https://github.com/Aero123421/dsh-remora/pull/1) merge→[#2](https://github.com/Aero123421/dsh-remora/pull/2) merge | 24分47秒 | merge後の保存待ち修正が入るまでの時間 |
| Remora [v0.1.0](https://github.com/Aero123421/dsh-remora/releases/tag/v0.1.0)公開→[画面修正PR](https://github.com/Aero123421/dsh-remora/pull/3)作成 | 31分33秒 | 公開後に画面の追加修正がPR化された |
| Glass UI [v0.1.0](https://github.com/Aero123421/dsh-glassui/releases/tag/v0.1.0)公開→[asset修正PR](https://github.com/Aero123421/dsh-glassui/pull/3)作成 | 2分41秒 | 公開直後に配布工程の修正がPR化された |

PRのcommit数、diff行数、テスト件数も工数や品質の代替値にしていません。Pi #5の24commitには仕様変更、追加検証、文書・配布情報の更新が含まれます。「24回失敗した」「4時間浪費した」とは読みません。

## 閉じた状態と解決した範囲

GitHubはdefault branchへのmergeでlinked Issueを自動closeできます。[IssueとPRのリンク仕様](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

そのため`closed`だけでは公開版、導入経路、利用者の再確認を追えません。逆に、PWAにReleaseがないことだけで配布停止とも言えません。GitHub sourceからの導入が配布経路である場合があります。

未完了のPi #4/#6/#7とGlass UI依存更新PR #1も、openという理由だけで「詰まって放置された仕事」と数えていません。調査条件、設計予定、依存解決の失敗は別です。鍵の不在、担当者待ち、期限超過など、公開記録にない理由を補っていません。

## 同じ分析を更新するとき

1. 対象repository、確認時刻、取得範囲を固定する。
2. Issue本文の症状と原因仮説を分け、linked PR、commit、review、runを追う。
3. 最後の成功SHA、公開tag、package版、取得元、現在のasset一覧を結ぶ。
4. 後続修正が製品、test、CI環境、表示仕様のどれを変えたか読む。
5. 公開記録の事実、作者の検証報告、分析者の推論、未確認を分ける。

一覧取得にはRESTの`issues`、`pulls`、`releases`、`actions/runs`を使えます。100件を超える場合はpaginationを行い、削除済みrunや過去assetなど、取得できない履歴を全件確認済みに含めません。
