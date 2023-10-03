const path = require("path");
var webpack = require("webpack");

module.exports = {
  entry: "./script.js",
  mode: "development",
  devtool: "eval-source-map",
  target: "web",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "main.js",
  },
  plugins: [
    new webpack.ProvidePlugin({
      process: "process/browser",
    }),
    new webpack.ProvidePlugin({
      Buffer: ["buffer", "Buffer"],
    }),
  ],
};
