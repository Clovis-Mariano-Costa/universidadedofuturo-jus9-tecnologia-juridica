import { hashDeterministic, sha256 } from './codex-governance.mjs';

export const GAD_STATES = Object.freeze([
  'RASCUNHO', 'TRIAGEM', 'EM_REVISAO', 'PARA_VISTAS', 'APROVADO_NAO_PROMULGADO',
  'DEPOSITO_INTERNO', 'PUBLICACAO_PENDENTE_GATE', 'PUBLICADO', 'DESCARTE_ELEGIVEL'
]);

export const GAD_GATE_MATRIX = Object.freeze({
  RASCUNHO: { gate: 'documental', authority: 'autor', result: 'TRIAGEM' },
  TRIAGEM: { gate: 'competencia_e_proveniencia', authority: 'relator', result: 'EM_REVISAO' },
  EM_REVISAO: { gate: 'revisao_tecnica', authority: 'revisor_independente', result: 'PARA_VISTAS' },
  PARA_VISTAS: { gate: 'vistas_humanas', authority: 'colegiado_humano', result: 'APROVADO_NAO_PROMULGADO' },
  DEPOSITO_INTERNO: { gate: 'deposito', authority: 'custodio', result: 'PUBLICACAO_PENDENTE_GATE' },
  PUBLICACAO_PENDENTE_GATE: { gate: 'homologacao_humana', authority: 'governanca_humana', result: 'PUBLICADO' }
});

export const EMBLEM_CONTRACT = Object.freeze({
  asset_id: 'assets/images/emblema-universidade-do-futuro-1254.png',
  width: 1254,
  height: 1254,
  sha256: '44D4812A8B6FED95C834310CEC3E19CDC0CE67AD6D72AE2954F3C2F806C41031',
  tips: 9
});

function required(value, name) {
  if (value === undefined || value === null || value === '') throw new Error(`${name} is required`);
  return value;
}

function isoDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) throw new Error('invalid date');
  return date.toISOString();
}

export function createGateRecord(input = {}) {
  const state = required(input.state, 'state');
  const contract = GAD_GATE_MATRIX[state];
  if (!contract) throw new Error(`unknown GAD state: ${state}`);
  return {
    state,
    gate: input.gate ?? contract.gate,
    authority: input.authority ?? contract.authority,
    evidence: input.evidence ?? null,
    result: input.result ?? contract.result,
    actor: input.actor ?? null,
    author: input.author ?? null,
    conflict_check: input.conflict_check ?? 'NOT_CHECKED',
    version: input.version ?? null,
    evidence_hash: input.evidence_hash ?? null,
    human_gate: input.human_gate === true
  };
}

export function validateGateRecord(record = {}) {
  const errors = [];
  for (const field of ['state', 'gate', 'authority', 'result', 'version', 'evidence_hash']) {
    if (record[field] === undefined || record[field] === null || record[field] === '') errors.push(field);
  }
  if (record.actor && record.author && record.actor === record.author) errors.push('self_approval');
  if (record.conflict_check !== 'CLEAR') errors.push('conflict_check');
  if (record.evidence === null || record.evidence === undefined) errors.push('evidence');
  return { valid: errors.length === 0, errors };
}

export function assertNoSelfApproval({ author, reviewer, conflict_check = 'NOT_CHECKED' } = {}) {
  if (author && reviewer && author === reviewer) throw new Error('self-approval is forbidden');
  if (conflict_check !== 'CLEAR') throw new Error('conflict check must be CLEAR');
  return true;
}

export function calculateReviewAt(createdAt, days) {
  const created = new Date(createdAt);
  if (Number.isNaN(created.valueOf()) || !Number.isInteger(days) || days < 0) throw new Error('createdAt and non-negative integer days are required');
  created.setUTCDate(created.getUTCDate() + days);
  return created.toISOString();
}

export function createRetentionDryRun(files = [], { asOf = '2026-08-26T00:00:00.000Z', defaultDays = 180 } = {}) {
  const now = new Date(asOf);
  if (Number.isNaN(now.valueOf())) throw new Error('invalid asOf');
  const entries = files.map((file) => {
    const reviewAt = isoDate(file.review_at ?? calculateReviewAt(file.created_at, file.review_days ?? defaultDays));
    const impediments = [...(file.impediments ?? [])];
    const eligible = new Date(reviewAt) <= now && impediments.length === 0 && file.successor_ref == null;
    return {
      id: required(file.id, 'file.id'),
      review_at: reviewAt,
      state: eligible ? 'DESCARTE_ELEGIVEL' : (file.state ?? 'EM_REVISAO'),
      checklist: { successor_checked: file.successor_ref == null, impediments_checked: impediments.length === 0, authority_checked: file.authority_checked === true },
      impediments,
      successor_ref: file.successor_ref ?? null,
      action: 'NO_DELETE_DRY_RUN'
    };
  });
  return { dry_run: true, writes: 0, deletes: 0, as_of: now.toISOString(), entries, receipt: hashDeterministic(entries) };
}

export function createUAAcRecord(input = {}) {
  const record = {
    record_id: required(input.record_id, 'record_id'),
    objective: required(input.objective, 'objective'),
    evidence_hash: required(input.evidence_hash, 'evidence_hash'),
    category: required(input.category, 'category'),
    date: isoDate(required(input.date, 'date')),
    authorship: required(input.authorship, 'authorship'),
    source_ref: input.source_ref ?? null,
    human_review: input.human_review ?? null,
    status: 'RECORDED_NO_CREDIT'
  };
  for (const forbidden of ['hours', 'credits', 'title', 'degree']) delete record[forbidden];
  return record;
}

export function deduplicateUAAcByEvidence(records = []) {
  const seen = new Set();
  const unique = [];
  const duplicates = [];
  for (const record of records) {
    if (seen.has(record.evidence_hash)) duplicates.push(record.record_id);
    else { seen.add(record.evidence_hash); unique.push(record); }
  }
  return { unique, duplicates };
}

export function lintFormalText(text, { mode = 'formal' } = {}) {
  const issues = [];
  if (mode !== 'formal') return { valid: true, issues };
  let fenced = false;
  String(text ?? '').split(/\r?\n/).forEach((line, index) => {
    if (line.trim().startsWith('```')) { fenced = !fenced; return; }
    if (fenced || /^\s*>/.test(line) || /^\s*\[[^\]]+\]:/.test(line)) return;
    if (/\bacho(?:\s+que)?\b/i.test(line)) issues.push({ code: 'UNQUALIFIED_ACHO', line: index + 1, message: 'qualify as hypothesis, inference or another epistemic state' });
  });
  return { valid: issues.length === 0, issues };
}

export function validateEmblemMetadata(metadata = {}) {
  const errors = [];
  for (const field of ['asset_id', 'width', 'height', 'sha256', 'tips']) if (metadata[field] !== EMBLEM_CONTRACT[field]) errors.push(field);
  return { valid: errors.length === 0, errors, contract: EMBLEM_CONTRACT };
}

function normalizeArtifact(artifact) {
  if (!artifact) return null;
  return { path: required(artifact.path, 'artifact.path'), hash: required(artifact.hash, 'artifact.hash'), version: required(artifact.version, 'artifact.version') };
}

export function buildGadAcademicManifest(input = {}) {
  const markdown = normalizeArtifact(input.markdown);
  const pdf = normalizeArtifact(input.pdf);
  const logo = normalizeArtifact(input.logo);
  if (!markdown || !pdf || !logo) throw new Error('markdown, pdf and logo are required');
  const errors = [];
  if (markdown.version !== pdf.version) errors.push('markdown_pdf_version_mismatch');
  if (markdown.hash !== pdf.source_hash && pdf.source_hash) errors.push('markdown_pdf_source_mismatch');
  const publication = input.publication_intent === true;
  if (publication && input.human_gate !== true) errors.push('publication_requires_human_gate');
  const manifest = {
    schema: 'gad-academic-package-v1',
    state: publication && input.human_gate === true ? 'PUBLICADO' : 'DEPOSITO_INTERNO',
    human_gate: input.human_gate === true,
    markdown, pdf, logo,
    attachments: [...(input.attachments ?? [])], opinions: [...(input.opinions ?? [])],
    minutes: [...(input.minutes ?? [])], homologation: input.homologation ?? null,
    errors
  };
  return { valid: errors.length === 0, manifest, receipt: hashDeterministic(manifest) };
}

export function deterministicReceipt(value) {
  return sha256(JSON.stringify(value));
}
