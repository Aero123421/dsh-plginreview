# Loaderの記法と適用

基準DSHは `0.2.1-alpha.2` / `d743267388641bc76f17c45ce8b4c231aed1d32c`。別の版はLoaderのparser・patch実装とConfigを確認します。

rowは `id`、`name` と、必要な `config`、`disabled`、`inject`、`intercept`、`isolate` を持ちます。insertされた相対module pathはpatch fileの場所を基準にするため、公開後にそのfileも存在する必要があります。

`group: true` / `name: cordis:group` は `config` がentry listです。`cordis:include` は `config.path` のentry listを読みます。普通のserviceのConfigとgroupのentry listを混同しません。

Loader式は `!!js` です。`config` 内は宣言したinjectのactivation後、そのpluginのcontextで評価します。`disabled` もmount時に評価されます。ほかのmetadataはliteralとして扱い、任意fieldへJSを移しません。

overrideはrow fieldを置換します。`config` のdeep mergeを期待して部分fieldだけを渡すと、残りのfieldが消えます。既存の式・配列・制約を保つか、対象版の所有APIで変更します。

保存、compose、rowのactivation、実Sessionの選択と機能を順に確認します。上位layerのoverrideが勝つ場合は、下位patchを繰り返しても実行状態は変わりません。正確なrow IDとlayerを調べます。

参照: [公式の構成Skill](https://github.com/deepseek-ai/deepseek-harness/blob/d743267388641bc76f17c45ce8b4c231aed1d32c/packages/preset/agent-preset/skills/cordis-composition-reference/SKILL.md)。
