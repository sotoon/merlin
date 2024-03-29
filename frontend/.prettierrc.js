module.exports = {
  "plugins": [require.resolve("@trivago/prettier-plugin-sort-imports")],
  "arrowParens": "always",
  "bracketSpacing": true,
  "embeddedLanguageFormatting": "auto",
  "htmlWhitespaceSensitivity": "css",
  "insertPragma": false,
  "jsxBracketSameLine": false,
  "jsxSingleQuote": false,
  "proseWrap": "preserve",
  "quoteProps": "as-needed",
  "requirePragma": false,
  "semi": true,
  "singleQuote": false,
  "trailingComma": "all",
  "useTabs": false,
  "vueIndentScriptAndStyle": false,
  "printWidth": 80,
  "tabWidth": 2,
  "rangeStart": 0,
  "importOrder": ["^react", "<THIRD_PARTY_MODULES>", "^[./]"],
  "importOrderSeparation": true, 
  "importOrderSortSpecifiers": true 
}