# このリポジトリでの作業

ここはDSHプラグインの開発記録と開発エージェント用Skillsを保存する文書リポジトリです。実行プラグイン本体は含みません。

- 主ブランチは `main`、変更先は `Aero123421/dsh-plginreview`。ブランチは原則 `codex/`、commitとPRは日本語にします。
- 現行基準は [docs/current-baseline.md](docs/current-baseline.md) と [.agents/baseline.json](.agents/baseline.json) です。旧調査の固定SHA・実行結果と区別します。
- Skillsの変更では [.agents/AGENTS.md](.agents/AGENTS.md)、[配布方法](.agents/README.md)、[導入元とライセンス](.agents/NOTICE.md) を確認します。初回19種の導入元 `upstream.json` は履歴として保ちます。
- 公開ソース、今回実行した検証、作者報告、提案、未確認を区別します。PRのbase/head・merge先・公開物を確認し、検索結果の欠落を推測で埋めません。
- 他repoの修正、インストール、releaseは依頼された場合だけ行います。文書更新だけで利用者のprofile・認証情報・クラウド資源を変更しません。
- 非公開コード・指示・作業記録、資格情報、実ユーザーのデータを転載しません。
- 文書はリンク・見出し・例と根拠を、Skillsはfrontmatter、同梱参照、単独コピー後のリンクとLICENSEを確認します。必要な変更に絞り、本体専用コマンドや全gateを持ち込みません。
- 検査は `python3 scripts/validate_docs.py`。検査器を変えた場合は `python3 -m unittest discover -s scripts -p 'test_validate_docs.py'` も実行します。部分checkoutでの検査範囲・省略は明記します。
- このrepoにアプリの `package.json` はありません。本体の `pnpm run` をこのrepoの検証として案内しません。
