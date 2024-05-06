const path = require('path');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const RemoveEmptyScriptsPlugin = require('webpack-remove-empty-scripts');
const autoprefixer = require('autoprefixer');

module.exports = {
  entry: {
    main: './src/index.coffee',
    styles: '/src/styles.scss',
  },
  output: {
    filename: '[name].[contenthash].js',
    publicPath: '/static/dist/',
    path: path.resolve(__dirname, '..', 'cherrybin', 'static', 'dist'),
    clean: true,
    library: {
      name: 'cherrybin',
      type: 'var',
    },
  },
  module: {
    rules: [
      {
        test: /\.coffee$/,
        loader: 'coffee-loader',
        options: {
          transpile: {
            presets: ['@babel/env'],
          },
        },
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
          },
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [autoprefixer],
              },
            },
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
            },
          },
        ],
      },
    ],
  },
  plugins: [
    new WebpackManifestPlugin(),
    new CleanWebpackPlugin(),
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
    new RemoveEmptyScriptsPlugin(),
  ],
  devtool: 'source-map',
};
