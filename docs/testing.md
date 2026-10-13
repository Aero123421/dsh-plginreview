# テストとCI

テストは、変更した契約を確認するために選びます。すべてのプラグインに同じ件数や同じ全テストを要求しません。公開entry、非同期処理、権限、配布形式を変えた場合は、その境界を直接確認します。

## 確認の段階

| 段階 | 分かること | これだけでは分からないこと |
| --- | --- | --- |
| 型検査・lint | 型、import、基本的な実装規則 | runtimeの登録、実通信、配布不足 |
| unit | 変換、検査、状態遷移、保存競合 | DSH Loader全体、実UI、providerの可否 |
| adapter・protocol integration | schema、stream、RPC、再接続 | 実OAuth、課金、検索品質 |
| UI fixture | 部品の表示と操作、特定の競合 | 親DSHのlayout、実remote、profile |
| 実DSH E2E | Loader、設定画面、ツール、実profile保存 | mockで置き換えた外部サービス |
| 配布物smoke | GitHub指定・tarballからの起動と解除 | 未実行のOS・API・画面 |
| 実API smoke | その資格情報・日時・要求での動作 | 他plan、他model、将来の可用性 |

モックで全providerを通した結果は、「対応する入力・応答の変換を確認」と書きます。「全providerに実接続して確認」とは書きません。

## 非同期の不具合を再現する

任意のsleepでタイミングを合わせるのではなく、処理を止めるbarrierやdeferred Promiseを使います。

```text
1. 古いsnapshot取得Aを開始し、応答直前で止める
2. 設定を変更し、新しいsnapshot取得Bを完了させる
3. Aを完了させる
4. Bの状態が残ることを確認する
5. Aを失敗させる版でも、古いエラーが出ないことを確認する
```

同じ方法で、保存失敗、接続切り替え、dispose後のcallback、キャンセルと開始の競合を確認できます。

queueのcallbackは、非同期rejectと、Promiseを返す前の同期throwを別々に確認します。外部pluginのhelperでは、後者だけが呼び出し元をpendingにする条件を再現できました。[入力と確認結果](ecosystem/browser-and-routing.md)を参照してください。

期限はfake clockで進めます。OAuthでは実際のフローの期限を境界にし、キャンセル・期限切れ・plugin timeoutの違いを確認します。

## 修正前でも通るテストを避ける

可能なら、旧実装または問題を再導入した限定差分でテストが失敗することを確認します。これをnegative controlとして記録します。状態を止める位置が誤っていると、見た目は競合テストでも問題の順序を通っていない場合があります。

Remoraの監査ログ修正では、保存のファイルロックを止めて読み取りが待つことを確認しました。Glass UIでは、旧挙動を戻すとlifecycle・状態・大きな設定panelの検査が失敗することを確認しています。

実装の関数呼び出し回数だけを写すテストより、利用者が受け取る値、登録状態、保存結果、実行版を確認します。

## CIで隔離する資源

| 資源 | 隔離・終了の方法 |
| --- | --- |
| profile・設定・資格情報 | テストごとの一時ディレクトリ。実際の開発用profileに触らない |
| 環境変数 | 子processごとのenvを渡す。共有process環境を競合して書き換えない |
| network listener | `listen(0)`などで実際にbindし、そのsocketからportを取得する |
| token・操作ID | テストごとの値。資格情報ファイル・refresh lockも分ける |
| fake clock・module state | 共有scopeを確認し、必要ならprocessを分ける |
| filesystem lock | テストごとのパスと、所有者の終了確認 |
| browser context | cookie・storage・接続先をテストごとに分ける |
| subprocess | process treeの終了と、stdout/stderrのdrainを待つ |

空きportを調べてsocketを閉じ、そのportで別processを起動する方法には競合期間があります。DSHがport 0を受け取れない経路なら、その制約を記録し、衝突検出・起動失敗の処理を用意します。

共有cacheを使う場合は、cacheを作る処理と読む処理の排他を確認します。一時ディレクトリやpackage cacheを、別のテストの終了処理で消さないようにします。

## 終了を確認してから次へ進む

serverの停止要求を出しただけで、終了したとは限りません。socket、timer、queue、writer、worker、processの終了を待ちます。停止中に完了した処理から、監視や接続が再作成されないことも確認します。

readinessは、実際のHTTP応答、接続通知、service登録などを期限付きで待ちます。「数秒待てば起動している」とはしません。失敗時には、どの段階を待っていたかと、そのprocessの診断を返します。

flakeを隠すために、無条件の再試行、timeout延長、全テスト直列化を足しません。共有processのglobal stateなど直列化が必要な理由がある場合は、その範囲を絞って記録します。

## 配布物の確認

公開entryやbuildを変更したら、GitHub取得物と`.tgz`を実DSHへ導入します。テスト側が`src/`を直接importするだけでは、配布entryの欠落を見つけられません。

新規導入、旧版からの更新、OFF状態の維持、再起動、解除を確認します。Release公開後は、公開URLから取得したassetのchecksumと起動を確認します。CI内の未公開artifactの確認だけで終わりません。

### 新規導入と旧版からの更新

新しいClient entryや`dsh.client`宣言を追加した場合は、旧版を起動したまま更新する経路を選びます。導入版、新しい設定欄の有無、Host再起動後の実行版を記録します。PWA `0.1.0`→`0.2.0`では、新規導入で使えた設定欄が、旧版からの更新ではHost再起動まで出ませんでした。[再現条件](update-and-restart.md)を参照してください。

更新処理を変えた場合は、最初の応答喪失、同一originでのprofile A→B→A、別Clientの最新操作、receipt保存中の外部更新、取消の終了コード、manifest不一致を確認します。前のIDを保存したまま戻り、同じ操作を再送しないことまで検査します。

共存試験にはplugin版の組み合わせを残します。初期更新版7件の成功を、後続PWAのモバイル表示とGlass UIの描画変更へそのまま適用しません。今回共有するDOM・CSS・保存先から、追加検査を選びます。

## GitHub Actionsの最小構成

通常のGitHub-hosted runnerを使います。PRではread権限とkeylessの確認を基本にし、release jobだけに必要なwrite権限を付けます。

依存をlockfileから導入し、型検査・関連テスト・buildを実行します。Gitに生成物を含む構成なら、build後に追跡した生成物との差分を確認します。pack後はfile一覧と公開entryを確認します。

Windows・macOSで差があるkeychainやprocess処理には、そのOSのjobまたは実機確認を選びます。純粋なUI辞書変更だけのために、関係のない全OS・実APIの確認を追加する必要はありません。

## 報告の書き方

実行したコマンド、DSH・browser・pluginの版、成功した範囲、未実行の範囲を記録します。過去のPRのテスト件数を、そのまま今回の実行結果へ転記しません。

この文書リポジトリの編集だけなら、Markdownの構造・内部リンク・参照の確認を行います。plugin runtimeを変えていないのに、過去のplugin全テストを実行したことにはしません。

成功したPR CIからmerge後の失敗へ進んだ例や、環境・test・製品の原因の分け方は[詰まりどころの分析](workflow/bottlenecks.md)にあります。件数や暦時間を品質・工数へ変換しない扱いは[調査方法](workflow/evidence.md)を参照してください。

## 実例

- [Piの取得競合・期限テスト](https://github.com/Aero123421/dsh-pi-login/pull/3)
- [Remoraの保存待ちテスト](https://github.com/Aero123421/dsh-remora/pull/2)
- [Glass UIの競合・解除・描画テスト](https://github.com/Aero123421/dsh-glassui/pull/2)
- [Remoraの実DSH E2E構成](https://github.com/Aero123421/dsh-remora/blob/ed7e99736b0cc8e72a956722fb6fc72fda927239/docs/e2e.md)
