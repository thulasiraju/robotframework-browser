#!/usr/bin/env node
const esbuild = require('esbuild');

esbuild.build({
    logLevel: "info",
    entryPoints: ["./node/playwright-wrapper/index.ts"],
    bundle: true,
    platform: "node",
    outfile: "./Browser/wrapper/index.js",
    external: ["electron"],
    keepNames: true,
    minifyIdentifiers: false,
    minifySyntax: false,
    minify: false,
    /* plugins: [nodeExternalsPlugin()], */
  })
  .catch(() => process.exit(1));
