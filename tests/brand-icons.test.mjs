import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
const root = new URL('../public/', import.meta.url);
const html = readFileSync(new URL('index.html', root), 'utf8');
function png(file, size) {
  const bytes = readFileSync(new URL(file, root));
  assert.equal(bytes.subarray(0, 8).toString('hex'), '89504e470d0a1a0a', file);
  assert.equal(bytes.readUInt32BE(16), size, file);
  assert.equal(bytes.readUInt32BE(20), size, file);
  return bytes;
}
test('seated panda header and explicit favicons replace the prior brand', () => {
  assert.ok(html.includes('/assets/panda-v1/logo-256.png'));
  assert.ok(html.includes('rel="apple-touch-icon"'));
  assert.ok(html.includes('rel="manifest"'));
  assert.ok(html.includes('/assets/panda-v1/favicon-96x96.png'));
  assert.doesNotMatch(html, /data:image\/svg\+xml,[^"]*🎨/);
  assert.equal(png('assets/panda-v1/logo-256.png', 256)[25], 6, 'Logo retains alpha');
  for (const size of [32, 96]) png('assets/panda-v1/favicon-' + size + 'x' + size + '.png', size);
  png('apple-touch-icon.png', 180);
  const ico = readFileSync(new URL('favicon.ico', root));
  assert.equal(ico.readUInt16LE(2), 1);
  assert.equal(ico.readUInt16LE(4), 6);
});
test('manifest has valid same-origin square icons and separate maskable artwork', () => {
  const manifest = JSON.parse(readFileSync(new URL('site.webmanifest', root), 'utf8'));
  assert.equal(manifest.name, 'LazyingArt');
  assert.equal(manifest.start_url, '/');
  assert.equal(manifest.display, 'browser');
  assert.equal(manifest.icons.length, 3);
  for (const icon of manifest.icons) {
    assert.match(icon.src, /^\/(?!\/)/);
    assert.ok(existsSync(new URL(icon.src.slice(1), root)));
    const size = Number(icon.sizes.split('x')[0]);
    png(icon.src.slice(1), size);
  }
  assert.equal(manifest.icons.filter(i => i.purpose === 'maskable').length, 1);
});
