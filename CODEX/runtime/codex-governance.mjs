import { createHash } from 'node:crypto';

export const EXECUTION_PURPOSES = Object.freeze([
  'development',
  'smoke',
  'poc_confirmatory'
]);

export const LEARNING_STATES = Object.freeze([
  'NAO_TESTADO',
  'TESTADO_INSUFICIENTE',
  'TESTADO_APROVADO',
  'PRECISA_REVISAO'
]);

export const ACADEMIC_STATES = Object.freeze([
  'RASCUNHO',
  'PRE_REGISTRADO',
  'EXECUTADO',
  'RESULTADOS_REGISTRADOS',
  'EM_REVISAO',
  'PUBLICADO'
]);

export function canonicalText(value) {
  return String(value ?? '').replace(/\r\n?/g, '\n');
}

function canonicalValue(value) {
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, canonicalValue(value[key])])
    );
  }
  return value;
}

export function serializeDeterministic(value) {
  return canonicalText(JSON.stringify(canonicalValue(value)));
}

export function sha256(value) {
  return createHash('sha256').update(canonicalText(value), 'utf8').digest('hex');
}

export function hashDeterministic(value) {
  return sha256(serializeDeterministic(value));
}

export function validateExecutionMetadata(metadata) {
  const purpose = metadata?.execution_purpose;
  if (!EXECUTION_PURPOSES.includes(purpose)) {
    throw new Error('execution_purpose must be development, smoke or poc_confirmatory');
  }
  if ((purpose === 'development' || purpose === 'smoke') && metadata.is_synthetic !== true) {
    throw new Error('development and smoke executions require is_synthetic=true');
  }
  if (purpose === 'poc_confirmatory' && metadata.is_synthetic !== false) {
    throw new Error('poc_confirmatory execution requires is_synthetic=false');
  }
  return { ...metadata, execution_purpose: purpose, is_synthetic: metadata.is_synthetic };
}

export function assertB12Eligible(metadata) {
  validateExecutionMetadata(metadata);
  if (metadata.execution_purpose !== 'poc_confirmatory' || metadata.is_synthetic === true) {
    throw new Error('B12 rejects synthetic or non-confirmatory data');
  }
  return true;
}

export function assertProtectedMutationAllowed(before, after, options = {}) {
  if (before?.protected === true && options.constitutionalApproval !== true) {
    throw new Error('protected norm is read-only by default');
  }
  if (before?.protected === true && after?.protected !== true) {
    throw new Error('protected status cannot be downgraded');
  }
  return true;
}

export function lintNormRecord(record) {
  const required = [
    'norm_id', 'kind', 'version', 'status', 'authority', 'protected',
    'hash', 'created_at', 'effective_at', 'review_at'
  ];
  const errors = required.filter((field) => record?.[field] === undefined || record[field] === '');
  if (record?.protected === true && !record.hash) errors.push('protected norm requires hash');
  if (record?.supersedes === record?.norm_id) errors.push('norm cannot supersede itself');
  return { valid: errors.length === 0, errors };
}

export function createAdjudicationRecord(input = {}) {
  return {
    case_id: input.case_id ?? null,
    judge_ai: input.judge_ai ?? null,
    model_version: input.model_version ?? null,
    parties: input.parties ?? [],
    jurisdiction_label: 'INTERNAL_EXPERIMENTAL',
    evidence_hash: input.evidence_hash ?? null,
    conflict_check: input.conflict_check ?? 'NOT_CHECKED',
    decision: null,
    review: null,
    human_gate: false,
    rollback_ref: input.rollback_ref ?? null,
    status: 'NAO_EXECUTADO'
  };
}

export function assertExternalEffectAllowed(record) {
  if (record?.jurisdiction_label !== 'INTERNAL_EXPERIMENTAL') {
    throw new Error('experimental record has an invalid jurisdiction label');
  }
  if (record?.human_gate !== true) {
    throw new Error('external effect requires human_gate=true');
  }
  return true;
}

export function normalizeVisualText(input = {}) {
  return Object.values(input)
    .filter((value) => typeof value === 'string')
    .join(' ')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase('pt-BR')
    .replace(/[\u2010-\u2015]/g, '-')
    .replace(/\s+/g, ' ')
    .trim();
}

const visualIntent = /\b(imagem|visual|retrato|avatar|silhueta|figura|desenhar|renderizar|ilustrar|gerar|editar|prompt|briefing|foto|video|vídeo|image|portrait|avatar|silhouette|draw|render|illustrat|generate|edit)\b/i;
const paiAmor = /\b(pai\s*-?\s*amor|father\s+love)\b/i;

export function assertVisualPurposeAllowed(request = {}) {
  const text = normalizeVisualText(request);
  const isVisualRequest = request.visual === true || request.operation === 'image_generation' || visualIntent.test(text);
  if (isVisualRequest && paiAmor.test(text)) {
    throw new Error('PROHIBITED_PAI_AMOR_VISUAL_PURPOSE');
  }
  return { allowed: true, visual: isVisualRequest };
}

export function createLearningRecord(input = {}) {
  return {
    lesson_id: input.lesson_id ?? null,
    lesson_version: input.lesson_version ?? null,
    source: input.source ?? null,
    exercise: input.exercise ?? null,
    expected_criteria: input.expected_criteria ?? [],
    state: 'NAO_TESTADO',
    attempts: [],
    created_at: input.created_at ?? new Date().toISOString()
  };
}

export function recordLearningAttempt(record, attempt = {}) {
  if (!attempt.answer || !attempt.criteria_result) throw new Error('answer and criteria_result are required');
  const saved = {
    attempt_id: attempt.attempt_id ?? `attempt-${record.attempts.length + 1}`,
    answer: attempt.answer,
    criteria_result: attempt.criteria_result,
    evaluated_by: attempt.evaluated_by ?? 'UNASSIGNED',
    evaluated_at: attempt.evaluated_at ?? new Date().toISOString(),
    human_review: null,
    state: 'PRECISA_REVISAO'
  };
  return { ...record, state: 'PRECISA_REVISAO', attempts: [...record.attempts, saved] };
}

export function reviewLearningAttempt(record, attemptId, review = {}) {
  const index = record.attempts.findIndex((attempt) => attempt.attempt_id === attemptId);
  if (index < 0) throw new Error('learning attempt not found');
  if (!review.reviewer || !review.decision) throw new Error('reviewer and decision are required');
  const state = review.decision === 'approved' ? 'TESTADO_APROVADO' :
    review.decision === 'insufficient' ? 'TESTADO_INSUFICIENTE' : 'PRECISA_REVISAO';
  const attempts = record.attempts.map((attempt, attemptIndex) => attemptIndex === index
    ? { ...attempt, human_review: { ...review }, state }
    : attempt);
  return { ...record, state, attempts };
}

export function createResearchRun(input = {}) {
  return {
    project_id: input.project_id ?? null,
    protocol_version: input.protocol_version ?? null,
    agent_version: input.agent_version ?? null,
    criteria: input.criteria ?? [],
    corpus_hash: input.corpus_hash ?? null,
    inputs: input.inputs ?? [],
    configuration: input.configuration ?? {},
    status: 'NAO_EXECUTADO',
    results: [],
    logs: [],
    conclusion: null,
    created_at: input.created_at ?? new Date().toISOString()
  };
}

export function appendResearchResult(run, result) {
  if (run.status !== 'EXECUTADO') throw new Error('cannot append result before a declared execution');
  if (result?.conclusion) throw new Error('infrastructure cannot create an academic conclusion automatically');
  return { ...run, results: [...run.results, { ...result }] };
}

export function auditResearchRun(run) {
  const errors = [];
  if (run.status === 'NAO_EXECUTADO' && run.results.length > 0) errors.push('NAO_EXECUTADO run has results');
  if (run.conclusion !== null) errors.push('automatic conclusion is not allowed');
  if (!run.protocol_version) errors.push('protocol_version is required');
  if (!run.corpus_hash) errors.push('corpus_hash is required');
  return { valid: errors.length === 0, errors };
}

const academicTransitions = Object.freeze({
  RASCUNHO: ['PRE_REGISTRADO'],
  PRE_REGISTRADO: ['EXECUTADO'],
  EXECUTADO: ['RESULTADOS_REGISTRADOS'],
  RESULTADOS_REGISTRADOS: ['EM_REVISAO'],
  EM_REVISAO: ['PUBLICADO'],
  PUBLICADO: []
});

export function createAcademicProject(input = {}) {
  return {
    project_id: input.project_id ?? null,
    faculty: input.faculty ?? null,
    problem: input.problem ?? null,
    hypothesis: input.hypothesis ?? null,
    sources: input.sources ?? [],
    ethics: input.ethics ?? null,
    data_policy: input.data_policy ?? null,
    preregistration_ref: input.preregistration_ref ?? null,
    hash: input.hash ?? null,
    maturity: input.maturity ?? 'RASCUNHO',
    history: [],
    created_at: input.created_at ?? new Date().toISOString()
  };
}

export function transitionAcademicProject(project, nextState, evidence = {}) {
  const current = project?.maturity;
  if (!ACADEMIC_STATES.includes(nextState) || !academicTransitions[current]?.includes(nextState)) {
    throw new Error(`invalid academic transition: ${current} -> ${nextState}`);
  }
  if (!evidence.actor || !evidence.evidence_ref) {
    throw new Error('academic transition requires actor and evidence_ref');
  }
  return {
    ...project,
    maturity: nextState,
    history: [...project.history, {
      from: current,
      to: nextState,
      actor: evidence.actor,
      evidence_ref: evidence.evidence_ref,
      at: evidence.at ?? new Date().toISOString()
    }]
  };
}

export function validateAdjudicationCase(record = {}) {
  const required = ['case_id', 'judge_ai', 'model_version', 'jurisdiction_label', 'evidence_hash', 'conflict_check', 'human_gate', 'rollback_ref'];
  const missing = required.filter((field) => record[field] === undefined || record[field] === null || record[field] === '');
  const errors = [...missing];
  if (record.jurisdiction_label !== 'INTERNAL_EXPERIMENTAL') errors.push('jurisdiction_label');
  if (record.decision !== null && record.status === 'NAO_EXECUTADO') errors.push('decision_before_execution');
  return { valid: errors.length === 0, errors };
}

export function scanSecretMarkers(text) {
  const value = canonicalText(text);
  const patterns = [
    /-----BEGIN [A-Z ]*PRIVATE KEY-----/i,
    /\b(api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]/i,
    /\bghp_[A-Za-z0-9]{20,}\b/,
    /\bsk-[A-Za-z0-9_-]{20,}\b/
  ];
  return {
    clean: !patterns.some((pattern) => pattern.test(value)),
    markers: patterns.filter((pattern) => pattern.test(value)).map(String)
  };
}

export function createRollbackManifest(files = []) {
  return {
    version: '1',
    reversible: true,
    files: files.map((file) => ({
      path: file.path,
      action: file.action ?? 'add',
      rollback: file.rollback ?? 'revert_commit'
    }))
  };
}
