import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../public/', import.meta.url));
const html = readFileSync(root + 'index.html', 'utf8');
test('official native-store routes and honest purchase modes', () => {
  for (const id of ['id6808872450', 'id6815137919', 'art.lazying.landn', 'art.lazying.bunko', 'art.lazying.landn.pro']) assert.ok(html.includes(id));
  assert.match(html, /Android Pro is a separate paid edition/);
  assert.match(html, /US\$0\.99/);
  assert.doesNotMatch(html, /testflight|internaltest|\.apk/);
});
test('physical selection goes through the existing shop', () => {
  for (const slug of ['notebook', 'panda', 'pendant']) assert.ok(html.includes(`https://buy.lazying.art/#${slug}`));
  assert.doesNotMatch(html, /buy\.stripe\.com/);
});
test('L&N offers an ungated sample while retaining native purchase actions', () => {
  const card = html.match(/<article class="app-card speech" id="landn">[\s\S]*?<\/article>/)[0];
  assert.equal((card.match(/https:\/\/l-and-n\.lazying\.art\/lessons\/light-vs-night\//g) || []).length, 1);
  assert.match(card, /Try the free light \/ night audio lesson/);
  assert.match(card, /id6808872450/);
  assert.match(card, /art\.lazying\.landn/);
  assert.doesNotMatch(card, /\/account|buy\.stripe\.com|<form/);
});
test('new product introductions retain their guides and qualified Mac release', () => {
  const section = html.match(/<section[^>]+id="explore"[\s\S]*?<\/section>/)[0];
  for (const id of ['3862', '3864', '3866']) assert.ok(section.includes(`/computer_internet/${id}/`));
  assert.doesNotMatch(section, /apps\.apple\.com|play\.google\.com/);
  const mac = html.match(/<article[^>]+id="onlyideas"[\s\S]*?<\/article>/)[0];
  assert.match(mac, /id6816392935\?platform=mac/);
  assert.match(mac, /Mac App Store <span>US\$0\.99/);
  assert.match(mac, /art\.onlyideas\.app/);
  assert.match(mac, /iPhone edition remains in review/);
  assert.match(mac, /paid plans are not open/);
  for (const id of ['3849', '3853', '3857', '3867']) assert.ok(html.includes(`/${id}/`));
});
test('new live app cards expose only qualified platform routes', () => {
  const cards = new Map([...html.matchAll(/<article class="app-card [^"]+" id="([^"]+)">([\s\S]*?)<\/article>/g)].map(m => [m[1], m[2]]));
  assert.equal(cards.size, 7);
  for (const [id, routes] of Object.entries({
    aimemo: ['id6757573920', 'art.lazying.aimemo'],
    shi: ['id6816377548', 'art.lazying.shi'],
    lazyoracle: ['art.lazying.lazyoracle'],
    lightmind: ['id6794785684', 'art.lightmind.mobile'],
  })) for (const route of routes) assert.ok(cards.get(id).includes(route), `${id}: ${route}`);
  assert.doesNotMatch(cards.get('onlyideas'), /href="https:\/\/apps\.apple\.com[^"?]*id6816392935"/);
  assert.doesNotMatch(cards.get('aimemo'), /platform=mac/);
  assert.doesNotMatch(cards.get('lazyoracle'), /apps\.apple\.com/);
  assert.match(cards.get('aimemo'), /Account required/);
  assert.match(cards.get('lightmind'), /LightMind Tech Limited, a separate company/);
  assert.match(cards.get('shi'), /Chapter I/);
  const css = readFileSync(root + 'styles.css', 'utf8');
  assert.match(css, /\.app-shelf\s*\{[^}]*flex-wrap:\s*wrap/);
});
test('top app shelf includes every LazyingArt app once, including LazyOracle', () => {
  const shelf = html.match(/<div class="app-shelf"[^>]*>([\s\S]*?)<\/div>/)[1];
  const anchors = [...shelf.matchAll(/<a href="#([^"]+)">/g)].map(m => m[1]);
  assert.deepEqual(anchors, ['landn', 'bunko', 'onlyideas', 'aimemo', 'shi', 'lazyoracle', 'chat']);
  assert.match(shelf, /href="#lazyoracle"><img src="\/assets\/lazyoracle\.png"[^>]*><span>LazyOracle<\/span>/);
});
test('EchoMind uses official released stores and the existing first-party chat', () => {
  for (const route of ['https://chat.lazying.art/', 'id6793615455', 'art.lazying.echomind']) assert.ok(html.includes(route));
  assert.match(html, /iPhone\/iPad: US\$0\.99/);
  assert.match(html, /full EchoMind access needs an invitation/);
  assert.doesNotMatch(html, /Continue with (Google|Apple|GitHub)|unified login is live/i);
});
test('coin remains optional and inactive', () => {
  assert.ok(html.includes('https://coin.lazying.art/'));
  assert.match(html, /distribution is not open/);
  assert.match(html, /purchase does not earn an award/);
  assert.doesNotMatch(html, /connectWallet|eth_sendTransaction|claim now|guaranteed income/i);
});
test('shared account entry describes only the qualified password method', () => {
  const section = html.match(/<section[^>]+id="account"[\s\S]*?<\/section>/)[0];
  assert.match(section, /username or email and password/);
  assert.match(section, /no invitation needed/);
  assert.match(section, /Each app keeps its own workspace, permissions and purchases/);
  assert.match(section, /browse the products without signing in/);
  assert.match(section, /href="\/account"/);
  assert.doesNotMatch(section, /Coming next|Google|Apple|GitHub|not available/);
  assert.match(section, /\/3873\/lazyingart-platform-tools-shared-account.html/);
  assert.doesNotMatch(section, /href="\/api\/|<form|<button|claim now|automatic access/i);
});
test('company brand, prominent EchoMind actions and accessible motion', () => {
  assert.doesNotMatch(html, /Lachlan Chen|by Lachlan|I make small tools/);
  assert.ok((html.match(/https:\/\/chat\.lazying\.art\//g) || []).length >= 3);
  assert.ok(html.includes('Get the iPhone app'));
  assert.ok(html.includes('/assets/echomind.png'));
  const css = readFileSync(root + 'styles.css', 'utf8');
  assert.ok(css.includes('prefers-reduced-motion: reduce'));
  assert.ok(css.includes('animation: none !important'));
  assert.ok(css.includes('@keyframes arrive'));
  assert.doesNotMatch(css, /infinite/);
});
test('no forms, trackers, scripts, secrets or browser credential storage', () => {
  for (const file of readdirSync(root).filter(f => f.endsWith('.html'))) {
    const text = readFileSync(root + file, 'utf8');
    assert.doesNotMatch(text, /<script|<form|<iframe|localStorage|sk_live_|sk_test_|127\.0\.0\.1|\/home\/lachlan/i);
  }
});
test('privacy distinguishes optional sessions from anonymous browsing', () => {
  const privacy = readFileSync(root + 'privacy.html', 'utf8');
  assert.match(privacy, /browse the products without an account/);
  assert.match(privacy, /up to 30 days/);
  assert.match(privacy, /encrypted on our server/);
  assert.match(privacy, /does not sign you out of every other app/);
  assert.match(privacy, /separate read-only permission/);
  assert.match(privacy, /Unlinked profiles have no balance to show/);
  assert.match(privacy, /Personal summaries are not cached/);
  assert.match(privacy, /stop sharing in your shared account settings/);
  assert.doesNotMatch(privacy, /does not.*ask for a login/);
});
test('local assets, anchors and canonical routes exist', () => {
  for (const file of readdirSync(root).filter(f => f.endsWith('.html'))) {
    const text = readFileSync(root + file, 'utf8');
    for (const [, path] of text.matchAll(/(?:src|href)="(\/(?!\/)[^"#?]*)"/g)) {
      if (path === '/account') {
        assert.match(readFileSync(new URL('../server/http.py', import.meta.url), 'utf8'), /\('\/account',AccountPage\)/);
      } else assert.ok(existsSync(root + (path === '/' ? 'index.html' : path.slice(1))), path);
    }
  }
  for (const [, id] of html.matchAll(/href="#([^"]+)"/g)) assert.ok(html.includes(`id="${id}"`));
  assert.ok(html.includes('rel="canonical" href="https://platform.lazying.art/"'));
  assert.ok(readFileSync(root + 'sitemap.xml', 'utf8').includes('https://platform.lazying.art/'));
});
