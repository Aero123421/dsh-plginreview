# DSHプラグイン開発の共通ルール

独立したDSHプラグインの実装・レビューに使います。対象リポジトリの既存ルールとユーザーの目的を優先し、文書・Skillsの編集だけなら利用者のprofileやプラグインを変更しません。

## 対象版と読む範囲

2026-10-15確認のDSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`は、日付を固定した歴史的なソース読解記録であり、最新基準ではありません。全pluginの実行互換性も認定しません。[baseline.json](baseline.json)はその固定記録、[upstream.json](upstream.json)は最初の19 Skillsの導入元です。新しい作業では対象版の公開Releaseと所属packageのソースを確認し、過去の固定SHAと試験結果を最新版へ読み替えません。

公開Release、npmの配布先、開発branchを分けます。別の版では実際のAPIを読み、変更されたservice・event・provider・slot・保存形式の所有packageから確認します。Skill本文が同じでも参照APIが同じとは限りません。

## 対象と拡張点

- 公開された拡張点を優先し、HostとClientの依存・ビルド・実行環境を分けます。存在しないAPIや検証コマンドを補いません。
- system prompt、agent loop、権限、modelの挙動を変えるのは、その目的の変更が依頼された場合です。日本語化のために応答言語の指示を追加しません。
- 内部cacheや他pluginのDOMへの依存は、公開拡張点で足りない理由、対象版、解除と障害時の扱いを記録します。

## 状態と解除

- 登録、event、timer、observer、通信、子process、CSSは所有するcontextを決めます。`ctx.effect()` 等への登録だけでなく、停止が完了した時点まで追います。
- 解除は新規受付を止め、受け付け済み処理の結果・保存を、その依存serviceやlistenerが使える間に終えてから資源を閉じます。abort/killしただけ、injectを宣言しただけ、逆順に登録しただけで安全とは判断しません。
- waterfallでは処理しない場合に `next()` へ委譲し、共有decisionの無関係なfieldを保ちます。
- 接続・profile・認証試行・編集の世代を照合します。遅い成功・失敗で、新しい状態やログアウト後の資格情報を復活させません。
- plugin OFF、provider OFF、資格情報削除、クラウド資源削除を分けます。共有設定は所有serviceの原子的更新やrevisionで対象fieldだけを変更します。
- モデルへ渡す情報を記録可能な入口へ通し、resume・fork後にも同じ意味で再構成できるようにします。独立pluginから未知のSession eventや、本体experimental専用 `appendPluginRecord()` を追加しません。
- Session由来の表示は公開projectionを確認し、新しい全履歴scanを増やしません。保存完了が必要な操作では所有serviceのflushを待ちます。動的なport・pathをsystem promptへ無断で埋め込み、既存の会話prefixを書き換えません。

## 呼出し元・資格情報

- 外部要求の認証と操作の認可を分けます。Hostが作るprincipal/Peerを使い、wireの自己申告や暗黙のowner fallbackに依存しません。Remoteと直接HTTPの入口を区別します。
- UIのaccess snapshotは実行許可の証明ではありません。method/resource、一覧の各項目、stream、失効後の操作を所有側で確認します。既に実行中のunary処理はPeer破棄だけで止まるとは限りません。
- storeを持つprofileの保存値優先と、標準headlessのstore省略を区別します。資格情報のsourceを診断し、unset後にenvへfallbackする経路も確認します。試験のために利用者の保存値を消しません。

## UIと入力

- DSHのslot、theme token、localeと既存操作に合わせます。Host SDKや別コピーのReactをClientへ埋め込みません。
- 実際の設定内容幅、日本語、明暗、keyboard、touch、保存中・失敗・切断を変更箇所に応じて確認します。390 CSS pxのviewportだけで、もっと狭いpanelも確認したとはしません。
- model/tool JSON、設定、保存file、process/wireの境界を検証します。同一process内のtypedな値へ根拠なく検証を重ねません。
- 診断には失敗段階・影響・安全な次の操作を出し、token、cookie、APIキー、認証URL、利用者の会話を無加工で出しません。

## 配布・更新・検証

- 案内するGitHub、npm、Release tarball、local pathの配布物とentryを確認します。候補のregistryと実際の導入先、build承認の対象を一致させ、供給元の拒否を勝手に迂回しません。
- alpha.3のHMR下では既存packageへの `installBundle()` が `already-installed` になる経路があります。自己更新で自分を削除する前に、操作の所有者・保存状態・復旧を設計します。
- 候補、導入版、実行版、Client反映を分けます。`restart-required` は手順を案内し、`applied` も対象機能を確認します。`waitForInstall()` のnullを成功にしません。
- base/head、公開物、環境を固定し、差分に合う確認を選びます。旧実装で狙った失敗が起きるか、直接・代替入口でも拒否が効くかを見ます。成功済みの結果は変更で無効になった場合に再実行します。
- Issue、修正、test、merge、公開版、利用者確認を分けます。作者報告と自分の実行結果を混ぜず、未確認を対応済みに含めません。公開tagは差し替えません。

必要なSkillだけを読みます。本家専用の全gate、常設CI、録画、独自updater、operation台帳を全pluginへ一律追加する方針ではありません。
