import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const runtimeDir = dirname(fileURLToPath(import.meta.url));
const siteRoot = join(runtimeDir, '..', '..', '..');

test('static publication keeps human page, home link and sitemap entry', async () => {
  const [home, humans, sitemap] = await Promise.all([
    readFile(join(siteRoot, 'index.html'), 'utf8'),
    readFile(join(siteRoot, 'para-humanos.html'), 'utf8'),
    readFile(join(siteRoot, 'sitemap.xml'), 'utf8')
  ]);
  assert.match(home, /href="para-humanos\.html"/);
  assert.match(humans, /name="viewport"/);
  assert.match(humans, /<main\b/);
  assert.match(humans, /aria-label="Navegação principal"/);
  assert.match(sitemap, /<loc>https:\/\/universidadedofuturo\.jus9tecnologia\.com\.br\/para-humanos\.html<\/loc>/);
  assert.doesNotMatch(humans, /<img\b/i);
});
