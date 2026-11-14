export default [
  {
    files: ['app/second_brain/desktop/*.js'],
    languageOptions: { ecmaVersion: 2022, sourceType: 'script' },
    rules: {
      curly: ['error', 'all'],
      'one-var': ['error', 'never'],
      'max-statements-per-line': ['error', { max: 1 }],
    },
  },
];
