# モデル・認証・画像・記憶の実装比較

この章は、実際の接続成功やサービスの利用条件を検証したものではありません。固定したソースが使っている認証・catalog・contextの処理を比較します。provider固有endpointを、安定した公開APIとみなす根拠には使いません。

## Subscriptions: 動的catalogを認証accountに結び付ける

`dsh-plugin-subscriptions 0.9.9`は、Codex、Claude、Grok、Copilot、Antigravityのprovider routeを持ちます。OAuth store、provider adapter、モデルcatalog、設定UIを分けた構成です。

Codexのcatalog取得は、保存したaccountの認証情報とcatalog用のclient versionを使います。hidden entryを除き、表示名、priority、推論強度などを読み取ります。UI用のモード名とwireに送れる値を区別する処理もあります。

「一覧が取れたので全modelが使える」とはせず、accountが取得できる候補、能力の解決、生成時の認証を同じ境界で扱うことが参考になります。

根拠: [Codex provider](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/codex.ts)、[accountをまたぐ候補取得](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/accounts.ts)。

### 取得loopと最後の正常結果

catalog更新loopは起動時に取得し、その処理が終わってから1時間後に次を開始します。`setInterval()`で遅い取得を重ねる構成ではありません。解除ではAbortとtimer停止を行います。

catalog cacheには世代と進行中Promiseがあり、古い取得が新しいcache状態を上書きしない処理を持ちます。diskにはprovider・accountごとの最後の正常catalogと取得時刻を保存し、再起動後に復元します。

cache fileの破損は、資格情報の破損と区別されています。モデル能力を含む保存値を検証してから使い、不正なcacheで全生成が失敗する状態を避けます。

根拠: [更新loop](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/catalog-refresh.ts)、[cacheと世代管理](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/common.ts)、[永続catalog](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/providers/catalog-store.ts)。

Piログインの動的catalogを作る際には、この所有範囲・cache・取得loopを参考にできます。ただし、endpoint、account ID、保存先、能力を別実装へ丸ごと移しても、Pi SDKが新しいAPIや認証に対応するわけではありません。

### 資格情報の書き込みを直列化する

storeは複数account形式を持ち、旧single-account形式を読み込み時に移行します。writeはtemporary fileとrename、`0600`で保存し、同じpathへのread-modify-writeをPromise chainで直列にします。

同じprocess内のlogin、logout、token refreshが別accountの値を失わせない例です。このMapによる直列化を、複数processに共通のfile lockと同一視しません。複数DSH Hostが同じ保存先を使う配備では、別途検査が必要です。

根拠: [auth store](https://github.com/V1ki/dsh-plugin-subscriptions/blob/9930c5ee5e3fa239db9031f47a0f6f30f7ffc443/src/auth/store.ts)。

この確認版のpeer条件はDSH `0.2.1-alpha.2`と一致しません。参考実装の読解と、現行DSHへそのまま導入できることは分けます。[照合結果](package-checks.md)を参照してください。

## Our Free Model: provider拡張と独自の配布channelを持つ

`dsh-our-free-model 2.1.0`は、モデルcatalog・利用可否確認、provider集約、設定画面、forward listener、案内feed、独自updaterなどを持つ構成です。providerを一つ追加する小さいadapterとは、所有する機能の範囲が違います。

model routeやcatalogのIDを表示名から決めず、通信先、認証、能力、生成時の経路を確認します。「無料」「無制限」といった紹介文は、実API・plan・将来の可用性をこの調査で確認した結果ではありません。

### 署名付きmanifestとchecksumを分ける

updaterは、固定されたEd25519公開鍵でmanifestの署名を検証し、fileごとのsize・SHA-256も検査します。mutableな配布refをcommitへ固定する経路もあります。

manifestのhashだけを配布物と一緒に取得する方法に比べ、導入済みコードに信頼する鍵を固定する設計として参考になります。署名の対象field、鍵の更新・失効、旧版への戻し、正規の配布channelが侵害された場合の扱いは、署名があることだけで終えず確認します。

根拠: [updater](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/updater.js)。

### packageを直接置き換える更新の保守範囲

このupdaterはplugin directoryをstaging・backup・file置換・検証・reloadする方式です。DSHの通常installerへ渡す方式ではありません。

参考にする場合は、package-managerのmanifest・lock、共有package copy、複数process、依存の変化、途中停止、実行中のmodule graph、旧cacheの解除を確認します。fileごとのatomic renameがあることは、更新全体が一つのtransactionであることの証明にはなりません。

普通のbundle更新ではDSH managerを使い、こうした所有範囲を追加する必要がある場合だけ設計を広げます。

根拠: [reload](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/reload.js)、[Host entry](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/index.js)。

### token削減はモデルへの入力を変更する

adapterには、設定に応じたtoken saver処理を生成payloadへ適用する経路があります。UIの装飾や認証追加と違い、modelへ送る情報・promptを変更する機能として扱います。

それを採用する場合は、元の指示、tool result、履歴、画像、reasoning、再送への影響を検証します。自作の認証・日本語化pluginへ、こうした挙動変更を暗黙に取り込まないでください。

根拠: [adapter](https://github.com/Ebony-Vinyl/dsh-our-free-model/blob/ddb451c2f24bac0b0f8b03b2473efbb1f0aefb68/src/adapter.js)。

## Modlens: text modelへ画像を渡す橋を作る

`@liustack/modlens 3.26.6`は、同梱CLIを使う`modlens_read_image`と、画像解析を使うprovider wrapperを持ちます。元のtext-only modelへ、画像の解析結果を情報として渡す構成です。

wrapper用のprovider IDを分け、元のmodel一覧と能力を調べます。modelの表示名だけで画像対応を判断すると、wrapperを通常のtext modelと取り違えるため、structured metadataと登録済みwrapperの区別が必要です。

画像cacheではpathだけをIDにせず、fileのinode・timestampなどを使う処理があります。同じpathの画像を差し替えた場合と、同じ画像を繰り返し読む場合を分ける実装例です。

根拠: [DSH entry](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/index.js)、[model scopeのテスト](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/src/dshModelScope.test.ts)。

tool名を`modlens_read_image`にしている理由もソースにあります。DSHではscoped toolがglobal toolを隠すため、同名を登録できても、そのSessionが追加した方を使うとは限りません。登録成功と、実際に解決されるtoolを別々に確認する例です。

採用時は、画像がどの解析providerへ送られるか、OCR・解釈・不確実性をどう返すか、元画像の保持、画像変更の検知、生成履歴を確認します。wrapperがimage inputを受け付けることを、元のmodelが直接画像を理解したことと同一視しません。

wrapperが別providerを登録する場合は、元provider・modelのOFF状態、Fast・effortの選択、認証変更がwrapperにも反映されるか確認します。元のpickerだけを制限して、wrapper経由では使えてしまう経路を残さないようにします。

Windowsのchild processは一つの`spawnHidden()`へ集め、`windowsHide`を最後に指定して上書きされないようにしています。機能ごとにprocess起動オプションを散らさない例です。

根拠: [spawnHidden.js](https://github.com/liustack/modlens/blob/1d8b20fc97a33b456e0d500037d4d66febaeb80a/dsh/spawnHidden.js)。

## Memsearch: 保存、注入、recallを別の処理にする

`@zilliz/memsearch-dsh 0.1.6`は、完了turnのcapture、要約の保存、次のturnへの検索結果注入、recall Skillを持ちます。既定ではcapture・injectが有効です。

captureはSession eventを読み、要約をprojectの`.memsearch/memory/`へ保存します。処理をqueueで直列化し、Session・turnのanchorで再送を照合します。要約はmemsearch側のproviderか、pluginを無効にしたheadless DSHを使い、再帰captureを避けます。

注入は`agent/pre-step`の最初のmodel stepで行い、検索結果がない場合はdecisionを変えません。追加messageは`plugin:memsearch`をsourceにしたsnapshotとして生成します。取得した記憶を人間の新しい指示と同じ出所にしないための例です。

根拠: [DSH entry](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/plugins/dsh/index.js)、[処理の流れ](https://github.com/zilliztech/memsearch/blob/09e07d86b31ff81938b4f44a57099b6a9fc8723f/docs/platforms/dsh/how-it-works.md)。

### UIだけの拡張ではない

記憶が見えるUIに加えて、会話内容の保存、別modelへの要約送信、modelへのcontext注入が行われます。外部embedding・要約provider、保存scope、検索した記憶の出所、削除・解除後の保存内容を確認します。

projectごとの保存が既定でも、`MEMSEARCH_DIR`を明示すると共有先を変えられます。同じDSH Web processで複数projectを開く場合は、設定による共有と意図しない混在を区別します。

Web previewはread-onlyで、`.memsearch`内へのlexical containmentとrealpath検査、file種類、256 KiB上限を持ちます。これは[Sidebarの広いファイル操作](ui-and-runtimes.md)とは異なる境界です。

captureの重複防止は、その記録単位についての対策です。要約API、file保存、index反映、process停止をまたぐ全体のexactly-once保証としては扱いません。

## 自作pluginへ持ち帰ること

- 動的catalogの取得・保存・無効化は、生成adapterと同じprovider所有者に置く。
- 複数account・複数processの同時更新を区別する。
- 認証、表示、context追加、要約、token削減の範囲をREADMEと設定で示す。
- 追加した情報をSession履歴から再構成できるか、sourceの意味まで確認する。
- 画像や記憶を送る外部providerを、メインチャットのproviderと混同しない。
