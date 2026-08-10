import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const files = [
  'painel-estados.html',
  'biblioteca/index.html',
  'biblioteca/estudantes/charlie-logos-da-costa/index.html',
];
const checks = [
  ['<!doctype html>', 'documento HTML5'],
  ['lang="pt-BR"', 'idioma declarado'],
  ['class="skip-link" href="#conteudo"', 'atalho para conteúdo'],
  ['id="conteudo" class="', 'main identificado'],
  ['aria-label="Navegação principal"', 'landmark de navegação'],
  ['universidade-v2.css', 'camada visual acessível'],
];

const failures = [];
for (const relative of files) {
  const file = path.join(root, relative);
  const content = fs.readFileSync(file, 'utf8');
  for (const [needle, label] of checks) {
    if (!content.includes(needle)) failures.push(`${relative}: ${label}`);
  }
}

const dashboard = fs.readFileSync(path.join(root, 'painel-estados.html'), 'utf8');
for (const [needle, label] of [
  ['Matriz de gates', 'dashboard de gates'],
  ['Proveniência', 'proveniência visível'],
  ['PENDENTE', 'estado pendente explícito'],
  ['NÃO_EXECUTADO', 'não execução explícita'],
  ['Casa-Lar', 'separação da Casa-Lar'],
  ['Casa de Trabalho', 'separação da Casa de Trabalho'],
  ['CTPSV / CITAT', 'ponte allowlisted explícita'],
  ['<caption class="visually-hidden">', 'tabela com caption acessível'],
]) {
  if (!dashboard.includes(needle)) failures.push(`painel-estados.html: ${label}`);
}

if (failures.length) {
  console.error('FAIL');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`PASS: ${files.length} rotas e ${checks.length + 5} grupos de critérios verificados.`);
