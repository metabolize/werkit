import type { Linter } from 'eslint'
import prettierConfig from 'eslint-config-prettier'
import simpleImportSort from 'eslint-plugin-simple-import-sort'
import neostandard from 'neostandard'

const config: Linter.Config[] = [
  { ignores: ['**/dist/**', '**/node_modules/**', '.venv/**', 'htmlcov/**'] },
  ...neostandard({ ts: true }),
  {
    plugins: { 'simple-import-sort': simpleImportSort },
    rules: {
      'simple-import-sort/imports': 'error',
      'simple-import-sort/exports': 'error',
    },
  },
  prettierConfig,
]

export default config
