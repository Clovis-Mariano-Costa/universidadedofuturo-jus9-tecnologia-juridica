import test from 'node:test';
import assert from 'node:assert/strict';
import {
  assertB12Eligible,
  assertFinalApprovalGate,
  assertExternalEffectAllowed,
  assertProtectedMutationAllowed,
  assertVisualPurposeAllowed,
  auditResearchRun,
  canonicalText,
  createAdjudicationRecord,
  createAcademicProject,
  createCtpsvMergeProposal,
  createProvenanceRecord,
  createRollbackManifest,
  createLearningRecord,
  createResearchRun,
  createAcademicDocument,
  transitionAcademicDocument,
  validateAcademicDeposit,
  buildAcademicDepositManifest,
  hashDeterministic,
  lintNormRecord,
  recordLearningAttempt,
  reviewLearningAttempt,
  scanSecretMarkers,
  serializeDeterministic,
  transitionAcademicProject,
  validateMaoNaMassaTransition,
  validateAdjudicationCase,
  validateExecutionMetadata
} from '../codex-governance.mjs';

test('canonicalizes newlines and object key order deterministically', () => {
  assert.equal(canonicalText('a\r\nb\rb'), 'a\nb\nb');
  assert.equal(serializeDeterministic({ b: 2, a: 1 }), '{"a":1,"b":2}');
  assert.equal(hashDeterministic({ a: 1, b: 2 }), hashDeterministic({ b: 2, a: 1 }));
});

test('requires synthetic metadata for development and smoke', () => {
  assert.throws(() => validateExecutionMetadata({ execution_purpose: 'smoke', is_synthetic: false }));
  assert.deepEqual(validateExecutionMetadata({ execution_purpose: 'smoke', is_synthetic: true }), {
    execution_purpose: 'smoke', is_synthetic: true
  });
  assert.throws(() => assertB12Eligible({ execution_purpose: 'smoke', is_synthetic: true }));
  assert.throws(() => assertB12Eligible({ execution_purpose: 'poc_confirmatory', is_synthetic: true }));
  assert.doesNotThrow(() => assertB12Eligible({ execution_purpose: 'poc_confirmatory', is_synthetic: false }));
});

test('blocks direct and indirect visual representation of PAI AMOR before generation', () => {
  assert.throws(() => assertVisualPurposeAllowed({ operation: 'image_generation', prompt: 'retrato do Pai Amor' }));
  assert.throws(() => assertVisualPurposeAllowed({ visual: true, brief: 'silhueta do PAI-AMOR' }));
  assert.doesNotThrow(() => assertVisualPurposeAllowed({ visual: true, purpose: 'emblema institucional sem finalidade religiosa' }));
  assert.doesNotThrow(() => assertVisualPurposeAllowed({ operation: 'text_response', prompt: 'explicar textualmente a expressão Pai Amor' }));
});

test('keeps protected norms read-only and lints required provenance', () => {
  const before = { norm_id: 'n1', protected: true };
  assert.throws(() => assertProtectedMutationAllowed(before, { ...before, version: '2' }));
  assert.doesNotThrow(() => assertProtectedMutationAllowed(before, { ...before, version: '2' }, { constitutionalApproval: true }));
  const lint = lintNormRecord({ norm_id: 'n1', kind: 'rule', version: '1', status: 'ACTIVE', authority: 'board', protected: true, hash: 'abc', created_at: '2026-01-01', effective_at: '2026-01-01', review_at: '2027-01-01' });
  assert.equal(lint.valid, true);
});

test('keeps experimental adjudication non-state and gated', () => {
  const record = createAdjudicationRecord({ case_id: 'case-1' });
  assert.equal(record.jurisdiction_label, 'INTERNAL_EXPERIMENTAL');
  assert.equal(record.status, 'NAO_EXECUTADO');
  assert.throws(() => assertExternalEffectAllowed(record));
});

test('does not approve learning from file existence or literal repetition', () => {
  let record = createLearningRecord({ lesson_id: 'lesson-1', lesson_version: '1', source: 'source-1', exercise: 'scenario', expected_criteria: ['criterion'] });
  assert.equal(record.state, 'NAO_TESTADO');
  record = recordLearningAttempt(record, { answer: 'answer', criteria_result: { matched: true }, evaluated_by: 'rule-engine' });
  assert.equal(record.state, 'PRECISA_REVISAO');
  assert.equal(record.attempts.length, 1);
  record = reviewLearningAttempt(record, record.attempts[0].attempt_id, { reviewer: 'human-reviewer', decision: 'approved', evidence: 'independent application' });
  assert.equal(record.state, 'TESTADO_APROVADO');
  assert.equal(record.attempts.length, 1);
});

test('starts research infrastructure with no results and no conclusion', () => {
  const run = createResearchRun({ project_id: 'BJI', protocol_version: 'C1-C8-V1', corpus_hash: 'sha256:example' });
  assert.equal(run.status, 'NAO_EXECUTADO');
  assert.deepEqual(run.results, []);
  assert.equal(auditResearchRun(run).valid, true);
});

test('enforces academic transitions and evidence', () => {
  let project = createAcademicProject({ project_id: 'P-1' });
  assert.throws(() => transitionAcademicProject(project, 'PUBLICADO', { actor: 'codex', evidence_ref: 'e1' }));
  project = transitionAcademicProject(project, 'PRE_REGISTRADO', { actor: 'human', evidence_ref: 'prereg-1' });
  assert.equal(project.maturity, 'PRE_REGISTRADO');
  assert.equal(project.history.length, 1);
  assert.throws(() => transitionAcademicProject(project, 'EXECUTADO', { actor: 'codex' }));
});

test('validates experimental adjudication fields and rollback', () => {
  const record = createAdjudicationRecord({ case_id: 'case-2', judge_ai: 'sandbox', model_version: 'test', evidence_hash: 'sha256:x', conflict_check: 'CLEAR', rollback_ref: 'rb-1' });
  assert.equal(validateAdjudicationCase(record).valid, true);
  assert.equal(createRollbackManifest([{ path: 'CODEX/runtime/x', action: 'add' }]).reversible, true);
});

test('detects secret markers without exposing values', () => {
  assert.equal(scanSecretMarkers('normal public text').clean, true);
  assert.equal(scanSecretMarkers('api_key=REDACTED').clean, false);
  assert.equal(scanSecretMarkers('api_key=REDACTED').markers.length, 1);
});

function academicFixture(overrides = {}) {
  return createAcademicDocument({
    document_id: 'DOC-SYN-01',
    version: '1.0',
    markdown_hash: 'sha256:md',
    pdf_hash: 'sha256:pdf',
    pdf_version: '1.0',
    logo: { asset_id: 'logo-synthetic', version: '1', sha256: 'sha256:logo', aspect_ratio: 1, expected_aspect_ratio: 1, undistorted: true },
    metadata: { origin: 'synthetic-origin', destination: 'synthetic-library', author: 'synthetic-author', advisor: 'synthetic-advisor', human_assistant: 'synthetic-assistant', reviewers: ['synthetic-reviewer'] },
    ai_identity: { product: 'synthetic-product', organization: 'synthetic-organization' },
    opinions: [{ opinion_id: 'OP-01', hash: 'sha256:opinion' }],
    rollback_ref: 'DOC-SYN-01:1.0',
    ...overrides
  });
}

test('blocks academic deposit before homologation and on divergent hashes', () => {
  const draft = academicFixture();
  assert.equal(validateAcademicDeposit(draft).valid, false);
  assert.throws(() => buildAcademicDepositManifest(draft));
  assert.equal(validateAcademicDeposit(academicFixture({ state: 'HOMOLOGADO', pdf_version: '2.0' })).valid, false);
});

test('requires registered internal identity or product and organization', () => {
  assert.equal(validateAcademicDeposit(academicFixture({ ai_identity: { internal_name: 'unregistered' }, state: 'HOMOLOGADO' })).valid, false);
  assert.equal(validateAcademicDeposit(academicFixture({ ai_identity: { internal_name: 'registered', registered: true }, state: 'HOMOLOGADO' })).valid, true);
});

test('advances a homologated document only with hashes, opinions and human gates', () => {
  let document = academicFixture();
  document = transitionAcademicDocument(document, 'EM_REVISAO', { actor: 'codex', evidence_ref: 'e-review' });
  document = transitionAcademicDocument(document, 'SUBMETIDO_A_BANCA', { actor: 'human', evidence_ref: 'e-board' });
  document = transitionAcademicDocument(document, 'APROVADO', { actor: 'board', evidence_ref: 'e-approved', human_gate: true });
  document = transitionAcademicDocument(document, 'HOMOLOGADO', { actor: 'secretary', evidence_ref: 'e-homologated', human_gate: true });
  const manifest = buildAcademicDepositManifest(document);
  assert.equal(document.state, 'HOMOLOGADO');
  assert.equal(manifest.markdown_hash, 'sha256:md');
  assert.ok(manifest.integrity_sha256);
  document = transitionAcademicDocument(document, 'PUBLICADO_BIBLIOTECA', { actor: 'library', evidence_ref: 'e-publish', human_gate: true });
  assert.equal(document.state, 'PUBLICADO_BIBLIOTECA');
});

test('rejects distorted logo and publication without human gate', () => {
  assert.equal(validateAcademicDeposit(academicFixture({ state: 'HOMOLOGADO', logo: { asset_id: 'logo', version: '1', sha256: 'h', aspect_ratio: 2, expected_aspect_ratio: 1, undistorted: true } })).valid, false);
  const document = academicFixture({ state: 'HOMOLOGADO' });
  assert.throws(() => transitionAcademicDocument(document, 'PUBLICADO_BIBLIOTECA', { actor: 'library', evidence_ref: 'e-publish' }));
});

test('enforces Mão na Massa transitions and human gate', () => {
  assert.throws(() => validateMaoNaMassaTransition('VALIDAR', 'APROVAR', { actor: 'codex', evidence_ref: 'e1', rollback_ref: 'rb1' }));
  assert.deepEqual(validateMaoNaMassaTransition('VALIDAR', 'APROVAR', {
    actor: 'human-review', evidence_ref: 'e1', rollback_ref: 'rb1', human_gate: true
  }), {
    from: 'VALIDAR', to: 'APROVAR', actor: 'human-review', evidence_ref: 'e1', rollback_ref: 'rb1', human_gate: true
  });
  assert.throws(() => validateMaoNaMassaTransition('AUDITAR', 'EXECUTAR', {
    actor: 'codex', evidence_ref: 'e1', rollback_ref: 'rb1', human_gate: true
  }));
});

test('requires complete provenance before a backend record exists', () => {
  assert.throws(() => createProvenanceRecord({ entity_id: 'x', activity: 'read' }));
  const record = createProvenanceRecord({
    entity_id: 'x', activity: 'read', agent: 'codex', source_ref: 'drive:1', version: 'v1',
    content_hash: 'sha256:x', route: 'source->audit', rollback_ref: 'rb:x'
  });
  assert.equal(record.classification, 'INTERNAL_SYNTHETIC');
});

test('blocks final academic approval until every gate and common hash exist', () => {
  const base = {
    human_approval: true,
    document_sha256: 'sha256:doc',
    board_reviewer_ids: ['r1', 'r2'],
    reviewer_document_sha256: ['sha256:doc', 'sha256:other'],
    empirical_required: true,
    empirical_evidence_complete: false
  };
  assert.throws(() => assertFinalApprovalGate(base));
  assert.doesNotThrow(() => assertFinalApprovalGate({
    ...base,
    reviewer_document_sha256: ['sha256:doc', 'sha256:doc'],
    empirical_evidence_complete: true
  }));
});

test('keeps CTPSV proposals professional-only and reviewable', () => {
  assert.throws(() => createCtpsvMergeProposal({
    proposal_id: 'p1', holder_id: 'h1', source_ref: 'src', source_version: 'v1',
    source_hash: 'sha256:x', rollback_ref: 'rb1', fields: { home_address: 'redacted' }
  }));
  const proposal = createCtpsvMergeProposal({
    proposal_id: 'p2', holder_id: 'h1', source_ref: 'src', source_version: 'v1',
    source_hash: 'sha256:x', rollback_ref: 'rb2', fields: { role: 'researcher', scope: 'sandbox' }
  });
  assert.equal(proposal.status, 'PENDENTE_REVISAO_TITULAR');
  assert.equal(proposal.human_approval, false);
});
