---
name: cordis-plugin-development
description: DSH向けの独立したHost・UI・MCPプラグインを設計、実装、導入、検証する。配布・更新・解除の変更にも使う。
license: MIT
---

# DSHプラグインの開発

利用者が使えるbundleを対象DSHの拡張点で実装します。設計・レビューだけの依頼では調査と指摘を返し、profileの変更まで進めません。

## 対象を確認する

2026-10-15の確認基準はDSH `0.2.1-alpha.3` / `2fbf4359b82fb94c03dcce0b831660d87f12ea5c`です。別版では所有packageのREADME・型・登録実装を確認します。公開版と開発branch、Host/Client、profile、配布元を区別します。DSH内で使えるinspectionか、固定版のソースを読み、存在しないtoolやmanager APIを仮定しません。

| 作業 | 参照資料 |
| --- | --- |
| bundle、Host entry、Config、表示metadata | [Hostとbundle](references/host-plugin.md) |
| 設定ページ、panel、装飾、Client artifact | [UIプラグイン](references/ui-plugin.md) |
| MCP接続だけのbundle | [MCP](references/mcp-bundle.md) |
| 状態、context、event、Session、他pluginとの併用 | [拡張点と共存](references/practices.md) |
| UI操作やagent toolの入口 | [操作と呼出し元](references/user-actions.md) |
| GitHub、npm、Releaseでの配布 | [配布](references/distribution.md) |
| 更新確認、自己更新、再起動、結果照合 | [更新](references/updates.md) |
| 導入、解除、旧版からの更新の確認 | [検証](references/verification.md) |

全資料を毎回読む必要はありません。参照内の古い確認版を、現在のAPIへ自動的に読み替えません。

## 実装から確認へ

1. 必要なservice・provider・event・slotを選び、contextと解除の順序を決めます。model指示や権限の変更は依頼された範囲に限ります。
2. manifest・patch・実装を作り、コード、辞書、CSS、iconが公開entryから解決できる構成にします。
3. 入力、保存・通信、非同期結果の世代、失敗・取消を扱います。既存serviceを使い、独自installerでprofileを直接編集しません。
4. 新規pluginやentry/Loader変更は、隔離profileで公開経路の導入を確認します。managerのmockが新しい拒否・再構成の契約を再現しているかも確認します。
5. 資源の寿命を変えたらOFF/ON・削除、保存や更新を変えたら旧版からの導入・再開を検査します。自己更新には、解除されるpluginより長く生きる操作所有者が必要かを判断します。

導入成功、slot登録、HTTP成功、実行版、Client反映は別の観測です。現在の[manager](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/boot/plugin-manager/README.md)・[Session](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/core/session/README.md)・[Remote権限](https://github.com/deepseek-ai/deepseek-harness/blob/2fbf4359b82fb94c03dcce0b831660d87f12ea5c/packages/api/remote-access/README.md)を変更領域に応じて読みます。実行した範囲と未検証を報告します。
