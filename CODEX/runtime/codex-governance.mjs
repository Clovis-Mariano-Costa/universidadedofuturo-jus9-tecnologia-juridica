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

export const MAO_NA_MASSA_STATES = Object.freeze([
  'PREPARAR',
  'EMBRULHAR',
  'VALIDAR',
  'APROVAR',
  'EXECUTAR',
  'AUDITAR',
  'ROLLBACK',
  'BLOQUEAR'
]);

export const DICTIONARY_STATES = Object.freeze([
  'SEMENTE_NAO_CANONICA',
  'PROVISORIO',
  'CONSULTADO',
  'REVISADO',
  'CANONICO',
  'SUPERADO_COM_GENEALOGIA'
]);

const maoNaMassaTransitions = Object.freeze({
  PREPARAR: ['EMBRULHAR', 'BLOQUEAR'],
  EMBRULHAR: ['VALIDAR', 'BLOQUEAR'],
  VALIDAR: ['APROVAR', 'BLOQUEAR'],
  APROVAR: ['EXECUTAR', 'BLOQUEAR'],
  EXECUTAR: ['AUDITAR', 'ROLLBACK', 'BLOQUEAR'],
  AUDITAR: ['ROLLBACK', 'BLOQUEAR'],
  ROLLBACK: ['PREPARAR'],
  BLOQUEAR: ['PREPARAR']
});

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

export function validateMaoNaMassaTransition(current, next, evidence = {}) {
  if (!MAO_NA_MASSA_STATES.includes(current) || !MAO_NA_MASSA_STATES.includes(next)) {
    throw new Error('unknown Mão na Massa state');
  }
  if (!maoNaMassaTransitions[current]?.includes(next)) {
    throw new Error(`invalid Mão na Massa transition: ${current} -> ${next}`);
  }
  if (!evidence.actor || !evidence.evidence_ref || !evidence.rollback_ref) {
    throw new Error('Mão na Massa transition requires actor, evidence_ref and rollback_ref');
  }
  if ((next === 'APROVAR' || next === 'EXECUTAR') && evidence.human_gate !== true) {
    throw new Error('approval and execution require human_gate=true');
  }
  return {
    from: current,
    to: next,
    actor: evidence.actor,
    evidence_ref: evidence.evidence_ref,
    rollback_ref: evidence.rollback_ref,
    human_gate: evidence.human_gate === true
  };
}

export function createProvenanceRecord(input = {}) {
  const required = ['entity_id', 'activity', 'agent', 'source_ref', 'version', 'content_hash', 'route', 'rollback_ref'];
  const missing = required.filter((field) => input[field] === undefined || input[field] === null || input[field] === '');
  if (missing.length > 0) throw new Error(`provenance requires: ${missing.join(', ')}`);
  return {
    entity_id: input.entity_id,
    activity: input.activity,
    agent: input.agent,
    source_ref: input.source_ref,
    version: input.version,
    content_hash: input.content_hash,
    route: input.route,
    rollback_ref: input.rollback_ref,
    classification: input.classification ?? 'INTERNAL_SYNTHETIC',
    created_at: input.created_at ?? new Date().toISOString()
  };
}

export function assertFinalApprovalGate(gate = {}) {
  const errors = [];
  if (gate.human_approval !== true) errors.push('human_approval');
  if (!gate.document_sha256) errors.push('document_sha256');
  if (!Array.isArray(gate.board_reviewer_ids) || gate.board_reviewer_ids.length < 2) {
    errors.push('plural_board_review');
  }
  if (gate.empirical_required === true && gate.empirical_evidence_complete !== true) {
    errors.push('empirical_evidence');
  }
  const hashes = Array.isArray(gate.reviewer_document_sha256)
    ? gate.reviewer_document_sha256.filter(Boolean)
    : [];
  if (hashes.length !== gate.board_reviewer_ids?.length || hashes.some((hash) => hash !== gate.document_sha256)) {
    errors.push('common_document_hash');
  }
  if (errors.length > 0) {
    throw new Error(`APROVACAO_FINAL_PENDENTE: ${errors.join(', ')}`);
  }
  return true;
}

const forbiddenCtpsvField = /(^|_)(address|home|domestic|family|password|secret|token|private|religion|health|cpf|rg)(_|$)/i;

export function createCtpsvMergeProposal(input = {}) {
  const fields = input.fields ?? {};
  const forbidden = Object.keys(fields).filter((field) => forbiddenCtpsvField.test(field));
  if (forbidden.length > 0) throw new Error(`CTPSV rejects domestic or sensitive fields: ${forbidden.join(', ')}`);
  const required = ['proposal_id', 'holder_id', 'source_ref', 'source_version', 'source_hash', 'rollback_ref'];
  const missing = required.filter((field) => input[field] === undefined || input[field] === null || input[field] === '');
  if (missing.length > 0) throw new Error(`CTPSV proposal requires: ${missing.join(', ')}`);
  return {
    proposal_id: input.proposal_id,
    holder_id: input.holder_id,
    fields: { ...fields },
    source_ref: input.source_ref,
    source_version: input.source_version,
    source_hash: input.source_hash,
    rollback_ref: input.rollback_ref,
    conflicts: input.conflicts ?? [],
    status: 'PENDENTE_REVISAO_TITULAR',
    human_approval: false
  };
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

export const ACADEMIC_DOCUMENT_STATES = Object.freeze([
  'RASCUNHO',
  'EM_REVISAO',
  'SUBMETIDO_A_BANCA',
  'CORRECOES',
  'APROVADO',
  'HOMOLOGADO',
  'PUBLICADO_BIBLIOTECA'
]);

const academicDocumentTransitions = Object.freeze({
  RASCUNHO: ['EM_REVISAO'],
  EM_REVISAO: ['SUBMETIDO_A_BANCA'],
  SUBMETIDO_A_BANCA: ['CORRECOES', 'APROVADO'],
  CORRECOES: ['SUBMETIDO_A_BANCA'],
  APROVADO: ['HOMOLOGADO'],
  HOMOLOGADO: ['PUBLICADO_BIBLIOTECA'],
  PUBLICADO_BIBLIOTECA: []
});

export function createAcademicDocument(input = {}) {
  return {
    document_id: input.document_id ?? null,
    version: input.version ?? null,
    state: input.state ?? 'RASCUNHO',
    canonical_source: 'MARKDOWN',
    markdown_hash: input.markdown_hash ?? null,
    pdf_hash: input.pdf_hash ?? null,
    pdf_version: input.pdf_version ?? null,
    logo: input.logo ?? null,
    metadata: input.metadata ?? {},
    ai_identity: input.ai_identity ?? null,
    opinions: input.opinions ?? [],
    history: input.history ?? [],
    rollback_ref: input.rollback_ref ?? null,
    created_at: input.created_at ?? new Date().toISOString()
  };
}

function academicDocumentMetadataErrors(document = {}) {
  const errors = [];
  const required = ['document_id', 'version', 'markdown_hash', 'rollback_ref'];
  for (const field of required) {
    if (document[field] === undefined || document[field] === null || document[field] === '') errors.push(`${field}_REQUIRED`);
  }
  const metadata = document.metadata ?? {};
  for (const field of ['origin', 'destination', 'author', 'advisor', 'human_assistant', 'reviewers']) {
    if (metadata[field] === undefined || metadata[field] === null || metadata[field] === '') errors.push(`metadata.${field}_REQUIRED`);
  }
  if (!Array.isArray(metadata.reviewers) || metadata.reviewers.length === 0) errors.push('metadata.reviewers_REQUIRED');
  const identity = document.ai_identity ?? {};
  if (identity.internal_name && identity.registered !== true) errors.push('UNREGISTERED_INTERNAL_AI_NAME');
  if (!identity.internal_name && (!identity.product || !identity.organization)) errors.push('PRODUCT_AND_ORGANIZATION_REQUIRED_WHEN_INTERNAL_NAME_ABSENT');
  const logo = document.logo ?? {};
  if (logo.asset_id || logo.version || logo.sha256 || logo.aspect_ratio || logo.expected_aspect_ratio || logo.undistorted !== undefined) {
    for (const field of ['asset_id', 'version', 'sha256', 'aspect_ratio', 'expected_aspect_ratio']) {
      if (logo[field] === undefined || logo[field] === null || logo[field] === '') errors.push(`logo.${field}_REQUIRED`);
    }
    if (logo.undistorted !== true) errors.push('logo.undistorted_REQUIRED');
    if (Number(logo.aspect_ratio) !== Number(logo.expected_aspect_ratio)) errors.push('logo.ASPECT_RATIO_MISMATCH');
  }
  return errors;
}

export function validateAcademicDeposit(document = {}) {
  const errors = academicDocumentMetadataErrors(document);
  if (document.state !== 'HOMOLOGADO' && document.state !== 'PUBLICADO_BIBLIOTECA') errors.push('HOMOLOGATION_REQUIRED');
  if (!document.pdf_hash) errors.push('pdf_hash_REQUIRED');
  if (document.pdf_version !== document.version) errors.push('PDF_MARKDOWN_VERSION_MISMATCH');
  if (!document.logo) errors.push('logo_REQUIRED');
  if (!Array.isArray(document.opinions) || document.opinions.length === 0) errors.push('opinions_REQUIRED');
  for (const opinion of document.opinions ?? []) {
    if (!opinion.opinion_id || !opinion.hash) errors.push('opinion.hash_and_id_REQUIRED');
  }
  return { valid: errors.length === 0, errors };
}

export function buildAcademicDepositManifest(document = {}) {
  const validation = validateAcademicDeposit(document);
  if (!validation.valid) throw new Error(`academic deposit blocked: ${validation.errors.join(',')}`);
  const manifest = {
    manifest_version: '1',
    document_id: document.document_id,
    version: document.version,
    state: document.state,
    canonical_source: document.canonical_source,
    markdown_hash: document.markdown_hash,
    pdf_hash: document.pdf_hash,
    pdf_version: document.pdf_version,
    logo: document.logo,
    metadata: document.metadata,
    ai_identity: document.ai_identity,
    opinions: document.opinions,
    rollback_ref: document.rollback_ref
  };
  return { ...manifest, integrity_sha256: hashDeterministic(manifest) };
}

export function transitionAcademicDocument(document, nextState, evidence = {}) {
  const current = document?.state;
  if (!ACADEMIC_DOCUMENT_STATES.includes(nextState) || !academicDocumentTransitions[current]?.includes(nextState)) {
    throw new Error(`invalid academic document transition: ${current} -> ${nextState}`);
  }
  if (!evidence.actor || !evidence.evidence_ref) throw new Error('academic document transition requires actor and evidence_ref');
  if (nextState === 'APROVADO' && (evidence.human_gate !== true || !document.opinions?.length)) {
    throw new Error('approval requires opinions and human_gate=true');
  }
  const candidate = {
    ...document,
    state: nextState,
    history: [...(document.history ?? []), {
      from: current,
      to: nextState,
      actor: evidence.actor,
      evidence_ref: evidence.evidence_ref,
      at: evidence.at ?? new Date().toISOString()
    }]
  };
  if (nextState === 'HOMOLOGADO') {
    if (evidence.human_gate !== true) throw new Error('homologation requires human_gate=true');
    const validation = validateAcademicDeposit(candidate);
    if (!validation.valid) throw new Error(`homologation blocked: ${validation.errors.join(',')}`);
  }
  if (nextState === 'PUBLICADO_BIBLIOTECA') {
    const validation = validateAcademicDeposit(candidate);
    if (!validation.valid) throw new Error(`publication blocked: ${validation.errors.join(',')}`);
    if (evidence.human_gate !== true) throw new Error('publication requires human_gate=true');
  }
  return candidate;
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
