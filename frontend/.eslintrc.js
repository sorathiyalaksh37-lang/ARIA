module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'react-app',
    'react-app/jest',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'prettier',
  ],
  plugins: ['react', 'prettier'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: { jsx: true },
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    // Prettier integration
    'prettier/prettier': ['error', { endOfLine: 'auto' }],

    // React
    'react/react-in-jsx-scope': 'off',       // Not needed with React 17+ JSX transform
    'react/prop-types': 'off',               // We use TypeScript instead
    'react/display-name': 'warn',
    'react/no-unescaped-entities': 'off',

    // Hooks
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // General
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-unused-vars': 'off',                 // Handled by @typescript-eslint
    'prefer-const': 'error',
    'no-var': 'error',
  },
  settings: {
    react: { version: 'detect' },
  },
};
