# 更新機能の実装記録

2026-10-13に、次の7プラグインへ更新確認・導入・結果照合を追加しました。基準はDSH `0.2.1-alpha.2`です。下表は更新機能追加時の公開版で、後続Releaseも含む現在の版は[一覧](own-plugins.md)を参照してください。

| プラグイン | 更新機能追加時の公開版 | 実装PR | 追加修正PR |
| --- | --- | --- | --- |
| Pi login | [v0.5.1](https://github.com/Aero123421/dsh-pi-login/releases/tag/v0.5.1) | [#10](https://github.com/Aero123421/dsh-pi-login/pull/10) | [#11](https://github.com/Aero123421/dsh-pi-login/pull/11) |
| Search providers | [v0.3.1](https://github.com/Aero123421/dsh-search-providers/releases/tag/v0.3.1) | [#3](https://github.com/Aero123421/dsh-search-providers/pull/3) | [#4](https://github.com/Aero123421/dsh-search-providers/pull/4) |
| 日本語パック | [v0.2.1](https://github.com/Aero123421/dsh-japanese/releases/tag/v0.2.1) | [#3](https://github.com/Aero123421/dsh-japanese/pull/3) | [#4](https://github.com/Aero123421/dsh-japanese/pull/4) |
| Remora | [v0.1.3](https://github.com/Aero123421/dsh-remora/releases/tag/v0.1.3) | [#6](https://github.com/Aero123421/dsh-remora/pull/6) | — |
| Glass UI | [v0.2.0](https://github.com/Aero123421/dsh-glassui/releases/tag/v0.2.0) | [#10](https://github.com/Aero123421/dsh-glassui/pull/10) | — |
| PWA | [v0.2.0](https://github.com/Aero123421/dsh-pwa/releases/tag/v0.2.0) | [#5](https://github.com/Aero123421/dsh-pwa/pull/5) | — |
| CF | [v0.1.0-alpha.4](https://github.com/Aero123421/dsh-cf/releases/tag/v0.1.0-alpha.4) | [#6](https://github.com/Aero123421/dsh-cf/pull/6) | — |

CFはプレリリースです。更新先で安定版とプレリリースを選びます。PWA・CFはGitHubタグのソースを導入でき、添付tgzを更新の前提にしません。Remoraはworkspaceのルートではなく、Releaseのプラグイン用tgzを使います。

## 更新機能追加後の公開分

2026-10-13 12:22 UTCから、次の追加Releaseを確認しました。タグ・mainのpackage・Release assetの一致と、固定コミットのREADME・Releaseノートを照合しています。以下の試験件数は実装側の報告で、この文書更新時の再実行結果ではありません。

| 対象 | 追加された動作 | 根拠・検証報告 |
| --- | --- | --- |
| PWA `0.3.0` | 設定名をPWA・モバイルへ変更。幅768px未満の自動表示、左右ドロワー、ブラウザー別の自動・オン・オフ、設定ダイアログの配置を追加。package/bundle IDと更新先は維持 | [PR #6](https://github.com/Aero123421/dsh-pwa/pull/6)、[Releaseノート](https://github.com/Aero123421/dsh-pwa/blob/e2692d04699294c31b53e54224bc05d81e2b205e/docs/release-0.3.0.md)。33件のunit、実DSHへのtgz導入・再起動、767/768px境界、ドロワーの再選択・解除などを報告 |
| Glass UI `0.2.2` | インラインコードの不透明度と文章プレビュー、透明度操作・会話更新・静止壁紙の描画処理を改善。設定保存や動く壁紙の挙動を維持 | [PR #11](https://github.com/Aero123421/dsh-glassui/pull/11)、[Releaseノート](https://github.com/Aero123421/dsh-glassui/blob/997333b69b1559e4784c58c46c9a01ce47142046/docs/release-0.2.2.md)。142件のunit、58件のintegration、DSH 2版で各14件のnative検査、公開tgzのsmokeを報告 |

PWAのモバイル表示はDSH `0.2.1-alpha.2`のDOMを対象にし、オフで元の表示へ戻せます。Glass UIの性能数値はReleaseノートの測定条件に限ります。ブラウザーのタッチ・DPR・回転のエミュレーションは実機iOS/Android、GPU・電力・長時間利用の検証ではありません。Glass UIの[#8](https://github.com/Aero123421/dsh-glassui/issues/8)、[#9](https://github.com/Aero123421/dsh-glassui/issues/9)は継続確認の対象です。

後続版を含む7件の共存試験は今回行っていません。下の共存結果は、冒頭の更新機能追加時の版に対するものです。

## レビューで再現した問題

実装と独立レビューをGPT-6.1-solのmediumで分担しました。主な再現条件と修正は次のとおりです。

| 条件 | 問題 | 修正・回帰検査 |
| --- | --- | --- |
| 最初の導入応答が失われる | Clientが操作IDを知らず再送する | 送信前にIDを確定し、Hostの記録と同じIDで照合する |
| 同じURLを別のprofileへ使い直す | 前のIDで結果不明が続く | Hostのprofile識別子を取得してから、profile別の保存記録を読む |
| 古い失敗IDがブラウザーに残り、別Clientが更新中 | 最新の操作より古い結果を表示する | Hostが返す最新IDを優先し、ブラウザーのIDは応答喪失時の補助にする |
| 接続先が変わった後に古い導入要求が届く | 新しいprofileへ誤って導入する | Hostで要求のprofile識別子を照合し、導入前に拒否する |
| 前の結果が不明な間に別の新しいReleaseが出る | 新しい候補で未解決操作を上書きする | 候補の版に関係なく、元の操作を先に照合する |
| 記録保存を待つ間に別の画面から新しい版が入る | 古い候補へ下げる | 最後のI/O後に導入情報を読み直し、導入版より新しい候補だけを実行する |
| managerが成功を返すが、実際のmanifestが一致しない | 更新済み・再起動待ちと誤表示する | 版・導入状態・エラー・書き込み可否を照合し、不一致は結果不明にする |
| 取消に伴いpnpmが終了コード130を返す | 取消を失敗と表示する | managerの確定した`application: cancelled`を優先する |
| checksumは正しいがtgz内のpackageが違う | 別packageを導入する | 導入前に実際のアーカイブのpackage名・版・patch・対応DSHを確認する |
| sliderの保存中にGlass UIを更新する | 未保存の値を取りこぼす | 保存完了を待ち、保存拒否は表示して導入を開始しない |

同じ処理をコピーしたプラグインも、各repoのentry・配布名・namespace・保存先を確認します。一方の修正が、もう一方にも入ったことを前提にしません。

## DSHとpnpmの導入条件

CLIではprofileのworkspaceルートへの追加を明示します。

```sh
dsh plugin --profile web add -w github:Aero123421/dsh-pwa#v0.2.0
```

DSH `0.2.1-alpha.2`とpnpm `11.7.0`の実機検査では、画面からの導入が`ERR_PNPM_ADDING_TO_ROOT`で停止しました。確認版のmanagerは`pnpm add`を実行するためです。プラグインの更新ボタンも、このmanagerを使用します。

このエラーが出る場合は、対象profileの`.npmrc`に次を設定します。既存の設定がある場合は必要な行だけを追加してください。

```ini
ignore-workspace-root-check=true
```

通常のWeb profileの設定先は`$DSH_HOME/profiles/web/.npmrc`です。`DSH_HOME`を指定していない場合の場所は、そのDSHのprofile設定で確認してください。別profileへ一括設定したり、プラグインが利用者の設定を自動で書き換えたりはしません。

この設定はprofileルートへ依存を追加する意図を明示するものです。build scriptの実行許可や認証の解除とは別です。失敗時は成功表示にせず、旧版と保存設定が残ることも確認します。

## 更新機能追加時の検証の範囲

各repoの単体検査、配布entry・build・実際のDSHへの導入を確認し、設定されているCIを通しました。CFにはrepo方針に従いCIを追加していません。CFの通常検査ではJOSE/JWTとHTTP・WebSocketの認証境界を確認し、実cloudflaredの検査1件はバイナリー未指定で未実行です。

Glass UIはDSH `0.2.0-rc.2`と`0.2.1-alpha.2`で各12件の画面検査を通しました。旧版で更新元情報が取得できない場合は手動更新を案内し、元の表示機能は維持します。

公開タグとRemoraの公開tgzを隔離したWeb profileへ導入し、7件の同時起動を確認しました。Pi `0.5.0`→`0.5.1`、Search `0.3.0`→`0.3.1`、日本語パック `0.2.0`→`0.2.1`は、実際の更新ボタンから導入し、元の操作IDで再起動待ちと導入版を照合しました。上記のworkspace設定を入れた環境で確認しています。モデル・検索設定は更新前後で一致しました。

再起動後は7件の実行版、全設定項目、PWAのmanifestとPNG、日本語フォント、Glass UIをOFFにしても日本語と他の更新欄が残ることを確認しました。Linux上のChromium、1400×980と600×900で検査し、ページの実行エラー・consoleのエラーと警告はありませんでした。言語変更後の再読み込みも確認しています。個別の390px検査は各実装PRに記録しています。

tgz付きの公開版は、配布後にファイルを取得して`SHA256SUMS`と照合しました。CFはソースのみの配布なので、tgzがないことをエラーとは扱いません。

macOS/Windows/Electronの画面、実Cloudflareアカウント・Tunnel接続、実機iOS/iPadOS/Androidへのホーム画面追加、実プロバイダーでの生成・ログインは今回の確認に含めません。

その後、PWA `0.1.0`から`0.2.0`への更新で、新しい設定欄がサーバー再起動まで出ないことを実DSHで再現しました。新規導入の成功だけでは見つからない条件です。原因・操作順と、新しいClient entryを追加する際の確認は[更新後の反映と再起動](update-and-restart.md)にあります。
