# dsh-pluginトピックの調査条件

2026-10-13に[GitHubのdsh-pluginトピック](https://github.com/topics/dsh-plugin)から候補を洗い直しました。スター数や紹介文に加え、DSHが実際に読み込むpackage、登録先、状態の所有者、Issueの修正先まで確認します。

## 取得した範囲

GitHub Search APIに`q=topic:dsh-plugin&sort=stars&order=desc&per_page=100`を指定し、10ページを取得しました。取得完了は2026-10-13 13:10:09 UTCです。

| 項目 | 取得結果 |
| --- | ---: |
| APIが返した検索該当数 | 19,027 |
| 取得したリポジトリ | 1,000 |
| 重複を除いた数 | 1,000 |
| 取得範囲の最小スター数 | 17 |
| 500 stars以上の別検索の該当数 | 145 |

GitHub検索は一つの検索から取得できる結果が1,000件までです。19,027件を全部読んだ結果ではありません。各ページの`incomplete_results`はfalseでしたが、取得上限と検索結果の完全性は別です。また、ページ取得は一つの時点で原子的に固定されるものではありません。今回の1,000件は重複なし・スター数の降順でした。

[取得した1,000件のCSV](../../data/topic-top1000-2026-10-13.csv)に、検索順、repository、stars、default branch、archived/fork、最終push時刻、取得完了時刻を残しています。CSVにあることは、そのリポジトリの実装をレビュー済みという意味ではありません。

根拠: [検索条件](https://api.github.com/search/repositories?q=topic%3Adsh-plugin&sort=stars&order=desc&per_page=100)、[GitHub Search API](https://docs.github.com/en/rest/search/search)。

## トピック掲載とDSHプラグインを分ける

上位にはDSH本体、大きな別アプリ、Skill集、MCP、プラグイン一覧もあります。例えば図解Skillのスター数を、DSHにnative bundleとして導入するUI拡張の利用者数と比べません。

| 分類 | ソースで確認すること | 比較する範囲 |
| --- | --- | --- |
| DSH native bundle | `dsh.bundle.patch`、Host entry、Client宣言と実登録 | 導入・登録・設定・解除・更新 |
| bundleを含む別アプリ・CLI | DSH接続leaf、別process、runtime/profileの所有 | DSH接続部とアプリ側の起動・更新契約 |
| preset・agent loopの置換 | prompt、tool、permission、log、親子agentへの変更 | DSHの挙動を変える範囲と回復 |
| Skill・MCP・外部CLI | DSHが接続する入口と、別サービスの要件 | 接続・実行・情報の受け渡し。bundle導入とは区別 |
| 一覧・カタログ | 生成元、掲載条件、試験の入力と観測 | 候補発見・診断の意味。各pluginの品質保証とは区別 |

packageが見つかっても、GitHubルートから導入する対象とは限りません。workspaceのleaf、別リポジトリへ移ったadapter、npm配布物のentryを別々に追います。詳しい判定と実例は各分析章にあります。

## 深掘りする対象の選び方

上位のDSH専用拡張と、DSH adapterを持つ大きなプロジェクトから、更新、UI、認証、エージェント、遠隔接続、ブラウザー、画像、記憶の経路を選びました。同じ役割の比較対象も含めます。Subscriptionsは取得時455 starsで、上位のモデル提供pluginとOAuth・複数account・動的catalogを比較するために選んでいます。

選定は人気順位だけのランキングでも、全DSH pluginの監査でもありません。スターが多いことから安全性・保守性・実利用人数を推定せず、具体的なコードと修正の証拠で比較します。人気のある大きな本体にDSH接続leafが一つある場合は、スター数が本体全体の値であることを示します。

[以前の12リポジトリ調査](README.md#外部リポジトリの一覧)は当時の固定SHAを残しています。今回は新しいコミットを取得し、同じSHAだったものは既存コードを深く読み直しています。新しい版がないことを、未調査の理由にはしません。

## npmの取得規模

同じ期間、2026-09-13〜2026-10-12の公開downloads APIを再取得しました。GitHubのスター数とは別の指標です。

| package | 期間内downloads |
| --- | ---: |
| `dshmarket` | 562,173 |
| `dsh-better-sidebar` | 229,589 |
| `dsh-whale-widget` | 167,056 |
| `dsh-context` | 145,741 |
| `@linxin666/dsh-web-all` | 119,410 |
| `@liustack/modlens` | 94,116 |
| `@deepseek-harness-tui/dsh-tui` | 45,149 |
| `@openviking/dsh-memory-plugin` | 37,612 |
| `@wxg-prc-cpg/browser-skill-dsh-plugin` | 25,360 |
| `dsh-plugin-subscriptions` | 11,271 |
| `@memtensor/memos-local-plugin` | 10,136 |
| `@zilliz/memsearch-dsh` | 2,488 |
| `@everos-ai/dsh-plugin` | 455 |

例えば[dsh-contextの期間別応答](https://api.npmjs.org/downloads/point/2026-09-13:2026-10-12/dsh-context)、[OpenViking adapterの応答](https://api.npmjs.org/downloads/point/2026-09-13:2026-10-12/%40openviking%2Fdsh-memory-plugin)、[dshmarketの応答](https://api.npmjs.org/downloads/point/2026-09-13:2026-10-12/dshmarket)で照合できます。downloadsにはCIや再導入も含まれます。GitHubソース・Releaseからの導入はこの値だけでは分かりません。利用者数・品質・市場占有率へは変換していません。

## 一覧サイトをどう使ったか

[awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/blob/5b1340c419ebd83b620c10e9e54a7095afa7a47e/README.md)と[awesome-deepseek-harness](https://github.com/0xsline/awesome-deepseek-harness/blob/9f7826c98f7c41cbd054b27c2847cb69ca1be143/README.md)は、接続方式と候補を探す補助に使いました。掲載条件や一行説明を、今回の実行結果には転記しません。

カタログに「検証済み」とあっても、manifest確認、起動、ツール呼び出し、画面、解除、実APIのどれを試したかで意味が変わります。人気指標と同じく、判定する処理と観測対象まで見ます。

## 読解・再現・作者報告を分ける

分析はGPT-6.1-solのmediumで分担しています。各担当はdefault branchのコミットを固定し、packageから主要な実行経路、解除、関連Issue/PRまで追いました。公開PRがclosedでも、merge・公開・利用者の再確認が済んだとは扱いません。

| 証拠 | 記載する内容 |
| --- | --- |
| ソースで確認 | 固定SHA、ファイルと行、実際の呼び出し・保存・解除 |
| 限定した再現 | 実行したhelper、入力・順序、環境、結果。plugin全体の成功へ広げない |
| 作者の検証報告 | PR・ReleaseのURLと、作者が確認した版・操作・未確認 |
| 未確認・確認案 | まだ実行していない検査。想定を成功結果で埋めない |

外部pluginのinstall/build script、実OAuth、課金API、実ユーザーのブラウザーprofile、クラウド配備は、このソース分析のために実行していません。純粋helperの限定再現は各章に条件を残します。基準DSHは`0.2.1-alpha.2`、[d743267](https://github.com/deepseek-ai/deepseek-harness/tree/d743267388641bc76f17c45ce8b4c231aed1d32c)で、取得時のdefault HEADとも一致しました。
