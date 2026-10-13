# 配布・更新・マーケットの実装比較

同じ「マーケット」でも、npm・GitHubのplugin packageを入れるものと、skin・pet・presetを配るものがあります。更新APIもDSH標準と、第三者プラグインが提供するAPIを分けて確認します。

## dsh-market: プラグイン向け更新APIを公開する

確認した`dshmarket`は`1.66.18`です。Client側の内部responseを直接使わせず、`/dsh-market/api/v1`に小さい更新APIを公開しています。

| API | 役割 |
| --- | --- |
| `GET /capabilities` | schema、安定性、対応操作、profile、再起動の所有者を取得 |
| `GET /updates/summary` | 確認した数と、更新可能な数・対象を取得 |
| `GET /updates?name=...` | 一つの導入済みpackageの候補を確認 |
| `POST /updates` | 更新を開始し、202とoperation IDを受け取る |
| `GET /operations?operationId=...` | 進行・結果・再起動要求を照合 |
| `POST /rollback` | 記録に対応する復旧操作 |

表のpathには`/dsh-market/api/v1`を付けます。DSH本体のAPIではありません。確認コミットの`capabilities`は`stability: beta`を返すため、pathに`v1`があるだけで安定契約と判断しないでください。

このAPIを使う更新ボタンでは、最初にcapabilitiesを取得します。非対応のrestart操作を画面に出さず、Marketがない場合は手動更新へ案内するか、自前の更新確認serviceを使います。第三者APIを必須依存にするかは、配布対象と保守範囲から決めます。

根拠: [公開APIの説明](https://github.com/dsh-market/dsh-market/blob/840cd0a4e952aae6cf77c5e4a85df42ab105c718/UPDATE-API-V1.md)、[operation型とstore](https://github.com/dsh-market/dsh-market/blob/840cd0a4e952aae6cf77c5e4a85df42ab105c718/src/update-api-v1.ts)、[実際のroutes](https://github.com/dsh-market/dsh-market/blob/840cd0a4e952aae6cf77c5e4a85df42ab105c718/src/routes.ts)。

### 結果の記録が残る範囲

operationは`queued`、`running`、`succeeded`、`failed`、`cancelled`、`rolled-back`を持ちます。開始前と導入後の版、構造化progress、失敗理由、refresh・restart、復旧の可否を返します。

operation storeはHost process内のMapで、既定上限は50件です。IDにboot IDを入れるので、古いブラウザーのIDを、新しいprocessの仕事と取り違えにくくしています。

これは再接続の結果照合に使える設計です。ただし、Hostの再起動後まで履歴を永続化する仕組みではありません。更新を待つ画面は、process変更や記録消失を「成功」に変換せず、導入版・実行版を再確認します。

### 更新、未公開commit、channel、取得元の変更

更新検知は、保存済みのpackage sourceを調べてから行います。Git sourceを同名のnpm packageと取り違えないようにしています。

- 指定branchと、既定branchの差分を混同しない。
- 版が進まないcommit差分は、`unreleasedCommit`として別に扱う経路を持つ。
- betaからstableへ戻るなど、版が下がるchannel変更を「新しい更新」と混同しない。
- `git-to-npm`の取得元移行は、通常の更新とは別の状態で返す。
- 通常の依存libraryを、bundleの更新対象へ混ぜない。
- Desktop側が所有する`generation`のlinkは、Marketから更新を適用しない。

この分離は、GitHub配布だけの小さいプラグインにも使えます。更新候補が見つかったことを理由に、pinや取得先を黙って変更しないようにします。

根拠: [updates.ts](https://github.com/dsh-market/dsh-market/blob/840cd0a4e952aae6cf77c5e4a85df42ab105c718/src/updates.ts)。fallbackを含む全経路で同じ判断になるかは、さらに実操作で確認する必要があります。

### Desktopの管理処理をCLIで代替しない

公式Desktop用のbridgeは、起動中アプリが所有する`pluginManager`を使います。CLIへ戻すとprofileの制約・lockにぶつかるため、対応しない引数も黙って捨てずに拒否します。

package processがexit 0でも適用失敗なら失敗を返します。`restart-required`や`overridden`を、ファイル保存まで失敗したものとして巻き戻さないよう、結果の意味を分けています。

一方、このbridgeの`installBundle()`呼び出しは`requestId`を渡す形です。その部分だけをコピーして汎用updaterにする場合は、更新前のOFF状態を保持する`enabled`も、自分の更新経路で明示して確認してください。今回、Marketの実画面からOFF状態の更新は試していません。

根拠: [official-desktop.ts](https://github.com/dsh-market/dsh-market/blob/840cd0a4e952aae6cf77c5e4a85df42ab105c718/src/official-desktop.ts)。

### timeoutを解除完了と扱わない

`waitForLifecycle()`は、待機がtimeoutしても、元のLoader操作が終わるまでpendingを保持します。同じLoader objectへ二つ目のmutationを開始させません。遅れて失敗したPromiseの扱いも残します。

「待つ時間が終わった」と「処理が止まった」は違う、という実装例です。pluginを停止・reloadする経路に、無条件の再試行を足す前に確認してください。

根拠: [lifecycle.ts](https://github.com/dsh-market/dsh-market/blob/840cd0a4e952aae6cf77c5e4a85df42ab105c718/src/lifecycle.ts)。

## dsh-web: 集約bundleとasset市場

確認した`dsh-web`は、ルートのbundleから`@linxin666/dsh-web-all`へ依存する構成です。集約packageの`aggregate.yml`は、各packageのpatchをまとめ、子entryへnamespaceを付ける処理の入力です。

機能をまとめる利点に加え、読み込む依存、登録順、entry衝突、ユーザーの無効設定、旧版との互換性を、まとめた状態で保守する必要があります。単独packageの成功だけで集約版も成功としません。

根拠: [集約manifest](https://github.com/zhu1090093659/dsh-web/blob/c76357950f341db57ef8852420f989dd7314d9e2/packages/dsh-web-all/package.json)、[aggregate.yml](https://github.com/zhu1090093659/dsh-web/blob/c76357950f341db57ef8852420f989dd7314d9e2/packages/dsh-web-all/aggregate.yml)。

### skin・pet・presetはnpm package更新と別の導入

asset installerは、Clientから任意URLを受け取らず、asset IDから固定marketのmanifestと配布pathを組み立てます。manifest・file数・fileサイズに上限があり、streamを読みながら累積byte数を検査します。

fileはstagingへ揃えてから配置し、導入済みdirectoryの上書きは別条件で扱います。presetはライブラリに置かれた時点ではまだ実行せず、登録の段階を分けています。

参考になるのは、取得すること、配置すること、実行することを分ける点です。導入provenanceのhashは、配置後の内容の照合には使えますが、配布サーバーやmanifestの署名検証と同じものではありません。

また、file数と各fileの上限だけで、asset全体の十分小さい容量が保証されるわけではありません。採用する場合は、全体byte数、空き容量、並列download、stagingの掃除も確認します。

根拠: [asset installer](https://github.com/zhu1090093659/dsh-web/blob/c76357950f341db57ef8852420f989dd7314d9e2/packages/dsh-market/src/core/installer.ts)。

### 一括更新は管理対象の範囲を固定する

plugin-manager側の一括更新候補は、`@deepseek-ai/`のpackageを除外し、互換条件を満たす第三者packageに絞っています。DSH本体のrelease familyが所有するpackageを、UI pluginの一括操作でばらばらに更新しないためです。

別の`dsh-update`実装は、所有profileでpnpmを起動する処理を持ちます。package更新を扱うコードがあるからといって、DSH標準managerのlock・復元・restart所有まで同じになるとは考えません。

根拠: [一括更新のfilter](https://github.com/zhu1090093659/dsh-web/blob/c76357950f341db57ef8852420f989dd7314d9e2/packages/dsh-plugin-manager/src/core/updates.ts)、[profile更新処理](https://github.com/zhu1090093659/dsh-web/blob/c76357950f341db57ef8852420f989dd7314d9e2/packages/dsh-update/src/update.ts)。

## 自作updaterへ持ち帰ること

小さいプラグインでは、まずDSHのinstallerに委譲する[更新ボタンの設計](../update-button.md)を使います。MarketのAPIを利用する場合は、存在、schema、安定性、profile、再起動の対応を確認する層を加えます。

どちらでも、候補版、実際に導入された版、現在の実行版、保存されたON/OFFを照合します。別プロジェクトの大きなinstall・rollback engineを、更新ボタン一つのために複製することは避けます。
