import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../public/', import.meta.url));
const html = readFileSync(root + 'index.html', 'utf8');
test('official native-store routes and honest purchase modes', () => {
  for (const id of ['id6808872450', 'id6815137919', 'art.lazying.landn']) assert.ok(html.includes(id));
  assert.match(html, /free download with in-app purchases/);
  assert.match(html, /US\$0\.99/);
  assert.doesNotMatch(html, /art\.lazying\.bunko|testflight|internaltest|\.apk/);
});
test('physical selection goes through the existing shop', () => {
  for (const slug of ['notebook', 'panda', 'pendant']) assert.ok(html.includes(`https://buy.lazying.art/#${slug}`));
  assert.doesNotMatch(html, /buy\.stripe\.com/);
});
test('coin remains optional and inactive', () => {
  assert.ok(html.includes('https://coin.lazying.art/'));
  assert.match(html, /distribution is not open/);
  assert.match(html, /purchase does not earn an award/);
  assert.doesNotMatch(html, /connectWallet|eth_sendTransaction|claim now|guaranteed income/i);
});
test('no forms, trackers, scripts, secrets or browser credential storage', () => {
  for (const file of readdirSync(root).filter(f => f.endsWith('.html'))) {
    const text = readFileSync(root + file, 'utf8');
    assert.doesNotMatch(text, /<script|<form|<iframe|localStorage|sk_live_|sk_test_|127\.0\.0\.1|\/home\/lachlan/i);
  }
});
test('local assets, anchors and canonical routes exist', () => {
  for (const file of readdirSync(root).filter(f => f.endsWith('.html'))) {
    const text = readFileSync(root + file, 'utf8');
    for (const [, path] of text.matchAll(/(?:src|href)="(\/(?!\/)[^"#?]*)"/g)) assert.ok(existsSync(root + (path === '/' ? 'index.html' : path.slice(1))), path);
  }
  for (const [, id] of html.matchAll(/href="#([^"]+)"/g)) assert.ok(html.includes(`id="${id}"`));
  assert.ok(html.includes('rel="canonical" href="https://platform.lazying.art/"'));
  assert.ok(readFileSync(root + 'sitemap.xml', 'utf8').includes('https://platform.lazying.art/'));
});
