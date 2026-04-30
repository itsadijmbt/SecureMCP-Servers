const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

const isProduction = process.env.NODE_ENV === 'production';
const outputPath = path.resolve(__dirname, '../../dispatch_cli/router/static');

module.exports = {
  mode: isProduction ? 'production' : 'development',
  entry: './src/index.js',

  output: {
    path: outputPath,
    filename: 'components.js',
    publicPath: '/static/', // This ensures correct paths for static assets
    clean: true, // Clean the output directory before emit
  },

  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ['@babel/preset-env', {
                targets: {
                  browsers: ['> 1%', 'last 2 versions']
                }
              }],
              ['@babel/preset-react', {
                runtime: 'automatic' // Use automatic JSX runtime
              }],
              ['@babel/preset-typescript', {
                isTSX: true,
                allExtensions: true
              }]
            ]
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  require('tailwindcss'),
                  require('autoprefixer'),
                ]
              }
            }
          }
        ]
      }
    ]
  },

  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
    alias: {
      '@': path.resolve(__dirname, '../src'),
      '@shared': path.resolve(__dirname, '../src/shared'),
      '@components': path.resolve(__dirname, '../src/components'),
      '@ui': path.resolve(__dirname, '../../../web-app/src/components/ui'),
      '@layout': path.resolve(__dirname, '../../../web-app/src/components/layout'),
      '@data-table': path.resolve(__dirname, '../../../web-app/src/components/ui/data-table'),
    },
    // Ensure dependencies are resolved from dispatch-local-ui/node_modules even when
    // processing files from web-app/ (which doesn't have its own node_modules in CI)
    modules: [
      path.resolve(__dirname, '../node_modules'),
      'node_modules'
    ]
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: './src/templates/index.html',
      filename: 'index.html',
      inject: 'head', // Inject scripts in head for better loading
      scriptLoading: 'defer',
      minify: false // Disable HTML minification for readability
    }),

    ...(isProduction ? [
      new MiniCssExtractPlugin({
        filename: 'components.css'
      })
    ] : []),

    // Copy additional static assets if needed
    new CopyWebpackPlugin({
      patterns: [
        {
          from: path.resolve(__dirname, '../src/assets'),
          to: outputPath,
          noErrorOnMissing: true // Don't error if assets folder doesn't exist
        }
      ]
    })
  ],

  devServer: {
    static: {
      directory: outputPath,
    },
    port: 3001,
    hot: true,
    open: true,
    historyApiFallback: true,
  },

  // Optimization for production builds
  optimization: {
    minimize: false, // Disable minification for better readability
  },

  // Development configuration for better debugging
  devtool: 'source-map', // Generate source maps for debugging
};