const path = require('path');

module.exports = {
    entry: './index.js', // replace with the path to your main JS file
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist'),
    },
    mode: 'development'
};