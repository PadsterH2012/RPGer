module.exports = {
  env: {
    browser: false,
    commonjs: true,
    es2021: true,
    node: true,
    jest: true
  },
  extends: [
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    // Possible Errors
    'no-console': 'off',
    'no-unused-vars': ['warn', { 
      vars: 'all', 
      args: 'after-used', 
      ignoreRestSiblings: false 
    }],
    
    // Best Practices
    'eqeqeq': ['error', 'always'],
    'no-eval': 'error',
    'no-implied-eval': 'error',
    'no-return-await': 'error',
    
    // Style
    'indent': ['error', 2, { 
      'SwitchCase': 1 
    }],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
    'no-trailing-spaces': 'error',
    'max-len': ['warn', { 
      code: 120, 
      tabWidth: 2,
      ignoreComments: true,
      ignoreUrls: true
    }],
    
    // Node.js and CommonJS
    'global-require': 'error',
    'handle-callback-err': 'warn',
    
    // Error Handling
    'no-throw-literal': 'error',
    
    // Async/Await
    'require-await': 'warn',
    
    // Logging
    'no-restricted-syntax': [
      'error',
      {
        selector: 'CallExpression[callee.object.name="console"][callee.property.name=/^(debug|trace)$/]',
        message: 'Avoid using console.debug or console.trace in production code.'
      }
    ]
  }
};