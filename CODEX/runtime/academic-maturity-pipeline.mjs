import { createHash } from 'node:crypto';

export const MATURITY_STATES = Object.freeze([
  'M00_RASCUNHO_DIDATICO_INTERNO', 'M01_RASCUNHO_CLASSIFICADO',
  'M02_MATERIAL_DE_AULA_INTERNO', 'M03_MATERIAL_DE_ESTUDO_REFERENCIADO',
  'M04_MATERIAL_REVISADO', 'M05_MATERIAL_COM_ANTITESE_E_CONTRAEXEMPLOS',
  'M06_PROJETO_ACADEMICO', 'M07_PROJETO_ORIENTADO',
  'M08_PROJETO_APROVADO_PARA_EXECUCAO', 'M09_PROTOCOLO_PRE_REGISTRADO',
  'M10_EXECUCAO_CONTROLADA', 'M11_RESULTADOS_PRELIMINARES',
  'M12_RESULTADOS_REPRODUZIDOS_OU_REVISADOS', 'M13_MANUSCRITO_PRE_BANCA',
  'M14_SUBMETIDO_A_BANCA', 'M15_BANCA_COM_EXIGENCIAS',
  'M16_APROVADO_PELA_BANCA', 'M17_CORRIGIDO_POS_BANCA',
  'M18_HOMOLOGADO_INTERNAMENTE', 'M19_SANITIZADO_PARA_PUBLICACAO',
  'M20_DEPOSITO_BIBLIOTECARIO_PENDENTE', 'M21_PUBLICACAO_BIBLIOTECA_AUTORIZADA',
  'M22_PUBLICADO_NA_BIBLIOTECA', 'M23_REVISAO_POS_PUBLICACAO'
]);

export const MATURITY_ROLES = Object.freeze([
  'REITORIA', 'DIRECAO_ACADEMICA', 'COORDENACAO', 'SECRETARIA',
  'ORIENTADOR', 'AUTOR_FUNCIONAL', 'AVALIADOR_INTERNO', 'AVALIADOR_EXTERNO',
  'HOMOLOGADOR', 'BIBLIOTECARIO_IA', 'EDITOR_IA', 'REGISTRADOR_PROVENIENCIA',
  'ZELADORIA_DOCUMENTAL', 'GUARDIAO_CIBERSEGURANCA', 'CHARLIE_ECHO_ALUNA',
  'CODEX_TECNICO'
]);

const HUMAN_GATED_STATES = new Set([
  'M08_PROJETO_APROVADO_PARA_EXECUCAO', 'M14_SUBMETIDO_A_BANCA',
  'M16_APROVADO_PELA_BANCA', 'M18_HOMOLOGADO_INTERNAMENTE',
  'M21_PUBLICACAO_BIBLIOTECA_AUTORIZADA', 'M22_PUBLICADO_NA_BIBLIOTECA'
]);

const SECRET_KEYS = /token|secret|password|credential|private[_-]?key/i;

function fail(message) {
  throw new Error(`MATURITY_BLOCKED:${message}`);
}

function assertString(value, name) {
  if (typeof value !== 'string' || value.trim() === '') fail(`${name}_required`);
}

export function validateCybersecurityGate(gate = {}) {
  const blockers = [
    ['critical_open', gate.critical_open === true],
    ['high_unmitigated', gate.high_unmitigated === true],
    ['tenant_isolation_untested', gate.tenant_isolation_tested !== true],
    ['authz_incomplete', gate.authz_complete !== true],
    ['secret_in_artifact', gate.secret_in_artifact === true],
    ['rollback_undemonstrated', gate.rollback_demonstrated !== true],
    ['incident_response_undefined', gate.incident_response_defined !== true],
    ['integration_unknown', gate.integration_surface_known !== true]
  ];
  const failures = blockers.filter(([, blocked]) => blocked).map(([name]) => name);
  if (failures.length) fail(`cyber_gate:${failures.join(',')}`);
  return { status: 'PASSED', failures: [] };
}

export function createTeachingMaterial({ source_id, source_version, source_state, sanitized = false, negative_result = false, content = null }) {
  assertString(source_id, 'source_id');
  assertString(source_version, 'source_version');
  assertString(source_state, 'source_state');
  if (!sanitized || content !== null) fail('teaching_material_must_be_sanitized_reference_only');
  return {
    kind: 'teaching_material', source_id, source_version, source_state,
    sanitized: true, negative_result: Boolean(negative_result), canonical_claim: false
  };
}

export function createMaturityRecord({ id, version, classification = 'internal', origin = 'local_sandbox' }) {
  assertString(id, 'id');
  assertString(version, 'version');
  assertString(classification, 'classification');
  assertString(origin, 'origin');
  return {
    id, version, classification, origin,
    state: MATURITY_STATES[0], history: [],
    teaching_material: createTeachingMaterial({
      source_id: id, source_version: version, source_state: MATURITY_STATES[0], sanitized: true
    })
  };
}

function validateEvent(event, previous, next) {
  for (const key of ['actor_id', 'role', 'origin', 'verb', 'evidence_id', 'version', 'timestamp', 'classification', 'risk', 'justification']) assertString(event[key], key);
  if (!MATURITY_ROLES.includes(event.role)) fail('role_not_registered');
  if (event.previous_state !== previous || event.next_state !== next) fail('state_provenance_mismatch');
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{5}Z$/.test(event.timestamp)) fail('timestamp_must_have_five_milliseconds');
  if (event.rollback_id !== undefined) assertString(event.rollback_id, 'rollback_id');
}

export function transitionMaturity(record, event, { cyber_gate, human_gate = false } = {}) {
  if (!record || !MATURITY_STATES.includes(record.state)) fail('record_state_invalid');
  const fromIndex = MATURITY_STATES.indexOf(record.state);
  const next = MATURITY_STATES[fromIndex + 1];
  if (!next || event.next_state !== next) fail('transition_not_sequential');
  validateEvent(event, record.state, next);
  validateCybersecurityGate(cyber_gate);
  if (HUMAN_GATED_STATES.has(next) && human_gate !== true) fail('human_gate_required');
  if (next === 'M22_PUBLICADO_NA_BIBLIOTECA' && !['BIBLIOTECARIO_IA', 'EDITOR_IA'].includes(event.role)) fail('publication_role_forbidden');
  if (next === 'M18_HOMOLOGADO_INTERNAMENTE' && event.role !== 'HOMOLOGADOR') fail('homologation_role_forbidden');
  const updated = structuredClone(record);
  updated.state = next;
  updated.history.push({ ...event, previous_state: record.state, next_state: next });
  updated.teaching_material = createTeachingMaterial({
    source_id: record.id, source_version: event.version, source_state: next, sanitized: true,
    negative_result: event.negative_result === true
  });
  return updated;
}

export function createDriveIndexEntry(metadata) {
  for (const key of ['file_id', 'folder_id', 'title', 'mime_type', 'classification', 'version']) assertString(metadata[key], key);
  if (!Array.isArray(metadata.parents) || metadata.parents.length === 0) fail('parents_required');
  if (Object.keys(metadata).some(key => SECRET_KEYS.test(key))) fail('secret_key_in_metadata');
  if ('content' in metadata || 'raw_content' in metadata) fail('content_copy_forbidden');
  return {
    file_id: metadata.file_id, folder_id: metadata.folder_id, title: metadata.title,
    mime_type: metadata.mime_type, parents: [...metadata.parents].sort(), version: metadata.version,
    state: metadata.state ?? MATURITY_STATES[0], classification: metadata.classification,
    source_id: metadata.source_id ?? null, supersedes: metadata.supersedes ?? null,
    superseded_by: metadata.superseded_by ?? null, teaching_material_id: metadata.teaching_material_id ?? null,
    hash: metadata.hash ?? null, review_date: metadata.review_date ?? null
  };
}

export function buildMaturityManifest(entries) {
  if (!Array.isArray(entries)) fail('entries_array_required');
  const normalized = entries.map(entry => createDriveIndexEntry(entry)).sort((a, b) => a.file_id.localeCompare(b.file_id));
  const payload = JSON.stringify(normalized);
  return { algorithm: 'SHA-256', entries: normalized, digest: createHash('sha256').update(payload, 'utf8').digest('hex') };
}

export function validatePublication({ state, role, human_gate, cyber_gate, evidence = {} }) {
  if (!['M21_PUBLICACAO_BIBLIOTECA_AUTORIZADA', 'M22_PUBLICADO_NA_BIBLIOTECA'].includes(state)) fail('publication_before_m21');
  if (!['BIBLIOTECARIO_IA', 'EDITOR_IA'].includes(role)) fail('publication_role_forbidden');
  if (human_gate !== true) fail('publication_human_gate_required');
  validateCybersecurityGate(cyber_gate);
  for (const key of ['version', 'hash', 'genealogy', 'sanitization', 'access_classification']) if (!evidence[key]) fail(`publication_evidence_missing:${key}`);
  return { status: 'PUBLICATION_ALLOWED', audit_event: 'PUBLICATION_VALIDADA_COM_EVIDENCIA' };
}
