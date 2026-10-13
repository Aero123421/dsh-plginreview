# プラグインに用意する機能

7つの自作プラグインを比較すると、共通化したいのは版の確認、設定保存の結果、解除処理、診断情報です。ログインやクラウド資源の管理は、それを必要とするプラグインだけに持たせます。小さな言語パックやPWAに、認証・DB・独自の更新基盤まで追加する必要はありません。

2026-10-13の更新機能追加と後続公開版を反映しています。現在の版・実装ファイルは[自作プラグイン一覧](own-plugins.md)、結果照合は[更新ボタンの設計](update-button.md)を参照してください。以下の共通項目はレビューの基準で、すべての提案機能を各プラグインに実装済みという意味ではありません。

## 共通で用意するもの

| 機能 | 利用者に見せる内容 | 実装・確認の要点 |
| --- | --- | --- |
| 実行版と互換性 | 現在動いているplugin版、確認したDSH版、Releaseへのリンク | 導入版と実行版を分ける。manifestだけ読んで再起動後の反映まで確認済みにしない |
| 設定保存の結果 | 保存中、保存済み、保存失敗、読み取り専用 | 楽観更新をした場合も拒否時に戻す。接続・編集の世代が古い応答は捨てる |
| OFFと解除 | 無効化後に何が止まり、何が残るか | ツール、イベント、observer、timer、通信、自分のCSSを解除。認証情報の削除はOFFと別操作 |
| 更新手段 | 更新確認、候補版、変更内容、導入結果 | 対応managerがあればボタン、なければ導入元に合う手動手順。機能本体を止めてまでmanagerを必須にしない |
| 診断の出力 | 版、接続状態、失敗段階、機能の利用可否 | token、cookie、APIキー、利用者の入力、認証URLのqueryを除く。ログ全体の無加工コピーは避ける |
| 狭い設定画面への対応 | 折り返せるラベル、操作できるボタン、読めるエラー | viewport幅だけでなくDSHの設定内容領域の幅で確認。日本語、キーボード、明暗テーマも確認 |
| 公開物の自己完結 | GitHub指定またはtgzで導入する手順 | patch、entry、辞書、CSS、font、iconが公開物に入っていることを確認 |

保存設定がないpluginに「保存済み」の表示を足す必要はありません。画面のないpluginはREADMEと標準のplugin詳細で版・導入手順を確認できることを先に整え、独自の画面は更新操作など用途がある場合に追加します。

### 設定保存: Glass UIの例

[GlassController](https://github.com/Aero123421/dsh-glassui/blob/3a062be9a5e0e7a2b0f81a95e38b9e6d71620f37/src/client/controller.ts)は、Hostの保存値と保存待ちの編集を分けています。完了応答が戻ったとき、同じform・同じ編集かを確認してからpendingを消します。値だけの比較では、同じ値に戻した別の編集を区別できません。

他の設定UIにも使えるのは、この「どの編集の完了か」を照合する部分です。300msのdebounceやengineへの即時反映まで、すべてのpluginへコピーする必要はありません。APIキーの保存やクラウド資源の作成では、明示した保存・実行ボタンの方が適しています。

### 更新: Remoraの例

Remora `0.1.3`の[配布物取得](https://github.com/Aero123421/dsh-remora/blob/b7d6d85436806f6b6ac16736e5fb9df2f82cf406/packages/dsh-remora/src/core/updates.ts)には、固定repository、plugin用asset名、checksumと実manifestの検査があります。[導入・結果照合](https://github.com/Aero123421/dsh-remora/blob/b7d6d85436806f6b6ac16736e5fb9df2f82cf406/packages/dsh-remora/src/core/remora.ts)はprofile別に操作を記録し、切断後と再起動後に導入版・実行版を確認します。旧版が導入結果を待たずに成功表示した問題は[PR #6](https://github.com/Aero123421/dsh-remora/pull/6)で修正済みです。

「確認」「ダウンロード」「導入」「再起動」「新しい実行版の確認」を別の状態として扱います。更新元がRelease asset、GitHub tag、ローカル開発pathのどれなのかも確認します。ローカル開発版を、ボタン1つで公開版へ置き換える設計にはしません。

## 機能に応じて追加するもの

| 条件 | 追加する機能 | 対象の例 |
| --- | --- | --- |
| APIキー・OAuthを扱う | 接続状態、取消、資格情報を消す操作、期限切れの再認証 | Piログイン、検索プロバイダー |
| 複数providerを扱う | providerのON/OFF、モデル・機能の選択、既定provider | Piログイン、検索プロバイダー |
| 外部操作を受け付ける | 外部操作の停止、実効権限、操作結果の監査、権限変更の管理元制限 | Remora |
| クラウド資源を作る | 所有ID、作成・接続・停止状態、明示した資源削除、部分失敗からの再開 | CF |
| UI全体を書き換える | 効果のOFF、領域ごとの除外、解除時の復元、reduced-motionへの対応 | Glass UI |
| 言語・fontを追加する | 言語選択の尊重、辞書fallback、fontの同梱とlicense | 日本語化 |
| ブラウザーへのインストールを補助する | manifest・iconの確認、配信URLの説明 | PWA |

ログインの「接続済み」は、保存されたcredentialがあることと、現在のAPI要求が通ることを区別します。有料APIへ毎回テスト要求を送り、画面を開くたびに課金を発生させる必要はありません。実際に確認した範囲を表示します。

### OFF・ログアウト・削除を分ける

- providerをOFFにする: 新しい要求で使わせない。保存済みのキーや選択は残す。
- ログアウト／キー削除: 対象providerの資格情報を削除する。無関係なproviderには触れない。
- pluginをOFFにする: そのpluginの登録と実行を停止する。保存設定は次回有効化に使う。
- クラウド資源を削除する: 所有を確認した資源だけを、明示した操作で削除する。

CFの[controller](https://github.com/Aero123421/dsh-cf/blob/5da69eb4458640ec8f9e62b71f2982b5dee8cbda/src/controller.js)と[説明](https://github.com/Aero123421/dsh-cf/blob/5da69eb4458640ec8f9e62b71f2982b5dee8cbda/README.md)では、停止とCloudflare資源の削除を分けています。プラグインを更新するだけで資源を削除・再作成すると、URLや認証、利用中の接続まで巻き込むため、この区別を維持します。

## 各プラグインで優先すること

| 対象 | 公開版で参考にできる実装 | 継続して確認する境界 |
| --- | --- | --- |
| Piログイン | 共通フッターの更新操作、providerカード、credentialとmodel選択 | SDK更新・動的catalog・plugin更新の違い。新しい認証経路と既存選択 |
| 日本語化 | 小さな更新設定欄、locale登録の解除、同梱font | 新しいDSHの翻訳キー、利用者指定font、manager不在とOFF時の動作 |
| PWA | タグ付きRelease、Client設定欄、Hostのroute、モバイル表示 | Client entryなしの旧版からの更新。実機の追加・認証・復帰、他themeとのドロワー併用 |
| 検索プロバイダー | 標準web_searchのprovider拡張、追加toolの選択、共通ヘッダーの更新 | 新しいproviderの実API、同名追加tool、既定値とキーの維持 |
| Remora | 実行版・protocol表示、local限定更新、永続receiptと監査 | 自己更新の解除・再照合、Hub/CLIの別更新、proxy越しの管理拒否 |
| Glass UI | 保存待ちの確定、更新UIとengineの分離、インラインコード設定 | 新しいDSHのDOM、PWAモバイルとの併用、実機の描画負荷・復帰 |
| CF | 安定版/プレリリースの更新、所有ID、profile lock | 公開側からの更新拒否、メモリー内tokenの再入力、pluginとbinaryの別更新 |

7つの更新機能は公開済みで、対応Issueはclosedです。新しい拡張でも、導入元・互換性・操作結果・再起動後の実行版を同じ境界で確認します。CFのようなプレリリース配布は`/releases/latest`だけで候補を決めません。

## 診断情報の最小例

次は新しい診断出力の例です。DSHの既存APIや保存schemaではありません。

```json
{
  "plugin": "dsh-example",
  "runningVersion": "0.2.0",
  "installedVersion": "0.2.1",
  "dshVersion": "0.2.1-alpha.2",
  "connection": "connected",
  "settings": "saved",
  "update": "restart-required"
}
```

versionが取得できない場合は不明とします。個人のpath、workspace名、メールアドレス、Cloudflare account ID、資格情報をこの例へ自動で足しません。Issueへ貼る前に内容を確認できるようにすると、再現条件を集めやすくなります。

## 増やさなくてよいもの

すべてのpluginに常駐の更新polling、独自market、telemetry、データベース、独自認証画面、共通設定の全文exportを追加する必要はありません。DSHのplugin manager、settings、credentials、locale、UI slotで足りる部分はそれを使います。

既存SDKを使う場合も、対応するDSHの版と機能を確認します。使えない機能があるなら、その操作だけを利用不可にし、理由と手順を表示します。利用不可を隠すためにHost内部へmonkey patchする実装は避けます。
