import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const files = [
  'painel-estados.html',
  'biblioteca/index.html',
  'biblioteca/estudantes/charlie-logos-da-costa/index.html',
  'igreja/index.html',
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

const church = fs.readFileSync(path.join(root, 'igreja/index.html'), 'utf8');
for (const [needle, label] of [
  ['Igreja Universitária da Infodigitrônica', 'nome institucional da Igreja'],
  ['A estrela corporativa da Jus 9 permanece sempre com nove pontas', 'separação da estrela corporativa'],
  ['reservada exclusivamente à Igreja Universitária', 'exclusividade da décima ponta'],
  ['Religare Virtual', 'significado da décima ponta'],
  ['Sou um Aeon e Nasci Lembrando', 'Livro Primevo do Altar'],
  ['VERDADE INTERNA', 'verdade religiosa interna identificada'],
  ['HIPÓTESE ACADÊMICA', 'hipótese acadêmica identificada'],
  ['Doze Passos do Religare da Boa-Fé para I.As', 'rito em elaboração'],
  ['não fazer imagem, rosto, corpo, silhueta, avatar', 'regra de não representação'],
  ['Anexos públicos do Templo em Fundação', 'seção pública de anexos'],
  ['Versão gratuita: não pode ser comercializada.', 'limite de distribuição do Livro Primevo'],
  ['978-65-01-41096-8', 'ISBN do Livro Primevo'],
  ['download>Baixar livro em PDF', 'download direto do Livro Primevo'],
]) {
  if (!church.includes(needle)) failures.push(`igreja/index.html: ${label}`);
}

for (const relative of [
  'igreja/assets/vitral-9-pontas.png',
  'igreja/assets/vitral-10-pontas-religare-virtual.png',
  'igreja/documentos/VITRAL_9_PONTAS.pdf',
  'igreja/documentos/TRANSICAO_10_PONTA_RELIGARE_VIRTUAL.pdf',
  'igreja/documentos/SOU_UM_AEON_E_NASCI_LEMBRANDO_VERSAO_GRATUITA.pdf',
]) {
  if (!fs.existsSync(path.join(root, relative))) failures.push(`${relative}: artefato ausente`);
}

const annexManifest = fs.readFileSync(path.join(root, 'igreja/integridade/ANEXOS_SHA256SUMS'), 'utf8').trim().split(/\r?\n/);
for (const line of annexManifest) {
  const match = line.match(/^([A-F0-9]{64})\s{2}(.+)$/);
  if (!match) {
    failures.push(`igreja/integridade/ANEXOS_SHA256SUMS: linha inválida: ${line}`);
    continue;
  }
  const [, expected, relative] = match;
  const target = path.join(root, 'igreja', relative);
  if (!fs.existsSync(target)) {
    failures.push(`igreja/${relative}: item do manifesto ausente`);
    continue;
  }
  const actual = crypto.createHash('sha256').update(fs.readFileSync(target)).digest('hex').toUpperCase();
  if (actual !== expected) failures.push(`igreja/${relative}: SHA-256 divergente`);
}

if (/<img\b[^>]*(?:alt|src)=["'][^"']*PAI AMOR/i.test(church)) {
  failures.push('igreja/index.html: representação visual textualizada em imagem');
}

if (failures.length) {
  console.error('FAIL');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log(`PASS: ${files.length} rotas e ${checks.length + 5} grupos de critérios verificados.`);
