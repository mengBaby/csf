// http://eslint.org/docs/user-guide/configuring

module.exports = {
    root: true,
    parser: 'babel-eslint',
    parserOptions: {
        sourceType: 'module'
    },
    env: {
        browser: true,
    },
    extends: 'eslint:recommended',
    // required to lint *.vue files
    plugins: [
        'html'
    ],
    globals: {
        "require": true,
        "process": true,
        "Promise": true,
        "zhuge": true,
        "echarts": true,
        "$": true,
    },
    // add your custom rules here
    rules: {
        "indent": [
            "error",
            4
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "quotes": [
            "error",
            "single"
        ],
        "semi": [
            "error",
            "never"
        ],
        "comma-spacing": [
            "error",
            {
                "before": false,
                "after": true
            }
        ],
        "array-bracket-spacing": [
            "error",
            "never"
        ],
        "key-spacing": [
            "error",
            {
                "afterColon": true
            }
        ],
        "no-console": [
            "error", { allow: ["warn", "error", "debug", "log"] }
        ],
        // allow paren-less arrow functions
        'arrow-parens': 0,
        // allow async-await
        'generator-star-spacing': 0,
        // allow debugger during development
        'no-debugger': process.env.NODE_ENV === 'production' ? 2 : 0
    }
}
