# 公式プラグインの構成と参考になる処理

この章の「公式」は、`deepseek-ai/deepseek-harness`の確認コミットに含まれる実装と、DSH本体が列挙するbundleを指します。第三者のREADMEに「公式推奨」と書かれていることと、DSHの公開元が所有する実装であることは分けます。

確認したDSHは`0.2.1-alpha.2`、コミット`d743267388641bc76f17c45ce8b4c231aed1d32c`です。調査時の`master`先頭もこのコミットでした。

## 通常の構成、任意bundle、後から導入する連携

DSHの通常構成には、agent loop、tools、LLM adapter、MCP、schedule、Web UIなどのプラグインがあります。そのすべてが管理画面で個別導入するbundleとして表示されるわけではありません。

任意bundleは、DSHの配布物に含まれ、利用者が有効化する単位です。確認版の`OPTIONAL_BUNDLES`は次の11種類です。

| package末尾 | 機能・構成 |
| --- | --- |
| `experimental-session-search` | Sessionの検索。専用のquery serviceとtoolを組み合わせる |
| `experimental-ralph-bundle` | 反復workflowとtool。workflowEngineを分離する |
| `experimental-terminal-bundle` | 永続terminal registry、shell provider、tool |
| `experimental-badge-skill-bundle` | Skill用のbadge機能 |
| `experimental-session-titles-bundle` | Sessionのタイトル生成 |
| `experimental-agent-team-profile` | team、team tool、team panelと、既存subagent toolの無効化 |
| `experimental-voice-input-bundle` | 音声service、ローカル認識provider、API、Client入力UI |
| `experimental-cot-translation-bundle` | 表示されるreasoningの翻訳serviceとClient UI |
| `experimental-auto-review` | tool実行前の自動authorization review |
| `experimental-inspector-profile` | fetchを含む診断・Session inspector |
| `experimental-tool-worktree` | worktree serviceと作成tool |

package名の共通prefixは`@deepseek-ai/dsh-`です。`experimental`という区分を、安定APIや全環境での検証済みという意味に置き換えません。

後から導入する公式catalogは、`@deepseek-ai/dsh-subagent-codex`と`@deepseek-ai/dsh-subagent-claude-code`の2種類です。これらは同梱済みのON/OFFだけで使えるものと区別されています。

根拠: [任意bundle一覧](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/app-boot/src/profile.ts)、[後から導入するpackage一覧](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/app-boot/src/official-bundle-packages.ts)。

## 1. bundleを責務ごとに組み立てる

音声入力のpatchは、認識をまとめるservice、SenseVoice provider、API、Client UIを別entryとして登録します。UIが認識processやモデルdownloadまで直接所有する構成ではありません。

SenseVoice providerは、有効化時点ではdownloadもmodel loadingも行わない実装です。登録と、重い準備・実行を分ける例として使えます。実際のモデル準備、通信先、保存先、失敗時の扱いはprovider側まで確認します。

これは「有効化しても何も起きない」という意味ではありません。service登録、cache確認、UI登録は行われます。何が遅延されるかを処理ごとに説明します。

根拠: [voice-inputのpatch](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/voice-input-bundle/cordis.patch.yml)、[SenseVoice entry](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/speech-to-text-sensevoice/src/index.ts)。

## 2. 同じ名前のserviceを別scopeに置く

Session Searchは`sessionQuery`、Ralphは`workflowEngine`、Terminalは`terminals`を、patchのgroup内で`isolate`しています。既存serviceと同じ名前を使っても、親の構成全体を置き換えるとは限らない設計です。

Session SearchのSQLiteは`openAt: first-search`、`:memory:`で登録されています。検索を有効にしただけで、永続的なDBが必ず作られると説明しないようにします。

Terminal bundleはOSごとにshell entryの有効状態を変えます。WindowsではPowerShell dialect、他OSではbash系を使う構成です。文字列の翻訳だけではなく、processとshellの違いを見る必要があります。

根拠: [Session Search](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/session-search/cordis.patch.yml)、[Ralph](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/ralph-bundle/cordis.patch.yml)、[Terminal](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/terminal-bundle/cordis.patch.yml)。

## 3. 機能追加に見えても、既存構成を置き換える

Agent Teamsのpatchは、team entryを加えるだけでなく、`tool-subagent`、fork、control、list-agentsなどの既存entryを無効化します。

レビューでは、追加されたツール数だけでなく、消えるツール、委譲先、親子関係、保存する状態、解除したときの復帰も確認します。複数bundleを同時に使う場合は、patchの適用順と同じIDへの上書きを調べます。

自作の認証・日本語化・検索拡張で、このような構成置換を必要なく取り込まないでください。DSHのエージェント動作を維持する変更と、動作を変更するpresetは別の範囲です。

根拠: [Agent Teamsのpatch](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/agent-team-profile/cordis.patch.yml)。

## 4. Codex・Claude Codeは、別の実行系として扱う

Codex providerは、委譲元のworkspaceでpackage-localのCodex wrapperから`app-server --stdio`を起動し、実行ごとのthreadを作ります。Claude Code providerはAgent SDKと、それが起動するCLIを共有subprocessサービスの所有下に置きます。

両方ともprovider名、任意のmodel、permission mode、env、終了の猶予を設定します。親contextの自動継承や、通常のDSH LLMと同じstart能力を当然に持つものとしては公開していません。

参考になる点は、外部productの実行をsubagent providerとして囲い、起動失敗、停止、process所有、workspaceの検査をその境界に集めることです。

これを入れることと、DSHのメインチャットにChatGPTログイン用LLM providerが追加されることは別です。認証・model・permissionは外部productの設定を使う経路もあるため、DSHのmodel pickerをそのまま適用できるとは説明しません。

根拠: [Codex provider](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/subagent/subagent-codex/src/index.ts)、[Claude Code provider](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/subagent/subagent-claude-code/src/index.ts)。

## 5. browser資源はSessionの生きている所有者に結び付ける

公式の`browser-use-runtime`は、永続Session IDだけでなく、その時点のAgentオブジェクトを資源の所有者に使います。Sessionごとのqueueで同じbrowserへの操作を直列にし、別Sessionは別々に進めます。

一つの要求のキャンセルと、Session全体のbrowser初期化・破棄を分けます。待機中の要求がキャンセルされただけで共有初期化を壊さず、所有者が破棄される場合は接続を閉じて実行中処理を起こします。

この違いは、ブラウザー、音声worker、外部CLI、接続poolを作る際にも使えます。「signalを付けた」だけで全資源のlifecycleを確認したことにはなりません。

根拠: [browser runtime](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/browser-use-runtime/src/index.ts)。

## 6. 表示翻訳でも外部通信と保存範囲を確認する

reasoning翻訳のcontrollerは、Hostが受理したprovider・言語設定とClient要求を照合します。provider選択の既定値はBing、言語の`auto`はUI localeを使います。

Hostのlimits APIは、設定・利用可能route・文字数上限を返すだけで、原文を送信しません。翻訳要求は別APIです。inactive Sessionを解決してから再試行する処理と、その待機のキャンセルも分けています。

日本語化プラグインと混同しないでください。locale dictionaryの切り替えと、reasoning本文を翻訳providerへ送る操作は、通信先・対象データ・保存の意味が違います。

根拠: [翻訳controller](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/client-ui-cot-translation/src/index.ts)、[設定の検証](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/client-ui-cot-translation/src/preferences.ts)。

## 7. worktree作成は成功と掃除を分ける

worktree serviceはworking directory、filesystem、subprocess、sandbox policyを使います。新しいcheckoutへSessionのcwdを切り替えるのは、Gitの準備が成功した後です。

disposeではlifetime signalを止め、進行中の作成処理を待ちます。失敗後に作成済みbranchやdirectoryが残る場合でも、無条件の自動削除はしません。削除してよい所有範囲と、利用者が残した作業を区別します。

checkout時のGit filter実行も検討対象です。公式実装は、設定されたclean・smudge・process filterを無効化して準備する処理を持ちます。通常のfilesystemコピーとは違う境界として調べます。

根拠: [worktree service](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/worktree/src/index.ts)。

## 8. 自動review・inspectorは機能の範囲を明示する

Auto Reviewは表示用のbadgeではなく、tool実行のauthorization判断に関わります。native callとPTC内のcallをレビューする一方、外側のtransportを重複レビューしない構成です。採用するときは、拒否、policy、cancel、ログ上の証跡まで確認します。

Inspectorのpatchは`captureFetch: true`を指定します。診断拡張では、何を記録するか、保存先、secretの除去、解除したときに監視が止まるかを確認します。

これらのoptional機能を、すべての自作プラグインの必須依存にする必要はありません。

根拠: [Auto Review](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/auto-review/src/index.ts)、[Inspector patch](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/experimental/inspector-profile/cordis.patch.yml)。

## 9. 公式packageの更新先は実行中DSHが決める

後から導入する公式bundleのtargetは、実行中DSHのrelease版を使って生成されます。ソースcheckoutの場合は、対応するworkspace package、版、bundle patch、ビルド済みruntimeを検査し、`link:`を作ります。

不完全なcheckoutを、黙ってnpm最新版へ切り替える経路にはしていません。共通の任意package updaterで、DSH内部packageを一括して最新へ上げる方針とも区別します。

根拠: [official install target](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/boot/plugin-manager/src/official-install-target.ts)。
