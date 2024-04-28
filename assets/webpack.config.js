const path = require("path");
const { WebpackManifestPlugin } = require("webpack-manifest-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const RemoveEmptyScriptsPlugin = require("webpack-remove-empty-scripts");

module.exports = {
  entry: {
    main: "./src/index.js",
    styles: "/src/styles.css",
  },
  output: {
    filename: "main.js",
    filename: "[name].[contenthash].js",
    publicPath: "/static/dist/",
    path: path.resolve(__dirname, "..", "app", "static", "dist"),
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
    ],
  },
  plugins: [
    new WebpackManifestPlugin(),
    new CleanWebpackPlugin(),
    new MiniCssExtractPlugin({
      filename: "[name].[contenthash].css",
    }),
    new RemoveEmptyScriptsPlugin(),
  ],
};
