import test from 'node:test';
import assert from 'node:assert/strict';
import {
  assertB12Eligible,
  assertExternalEffectAllowed,
  assertProtectedMutationAllowed,
  assertVisualPurposeAllowed,
  auditResearchRun,
  canonicalText,
  createAdjudicationRecord,
  createLearningRecord,
  createResearchRun,
  hashDeterministic,
  lintNormRecord,
  recordLearningAttempt,
  reviewLearningAttempt,
  serializeDeterministic,
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
