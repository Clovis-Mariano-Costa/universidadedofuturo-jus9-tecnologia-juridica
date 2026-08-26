import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildGadAcademicManifest, calculateReviewAt, createGateRecord, createRetentionDryRun,
  createUAAcRecord, deduplicateUAAcByEvidence, lintFormalText, validateEmblemMetadata,
  validateGateRecord
} from '../gad-incremental.mjs';

test('gate matrix requires evidence, version, conflict check and independent actor', () => {
  const record = createGateRecord({ state: 'EM_REVISAO', actor: 'reviewer', author: 'author', evidence: { ref: 'e1' }, version: '1', evidence_hash: 'sha256:e1', conflict_check: 'CLEAR' });
  assert.equal(validateGateRecord(record).valid, true);
  assert.equal(validateGateRecord({ ...record, actor: 'author' }).valid, false);
});

test('retention computes review_at and never deletes in dry-run', () => {
  assert.equal(calculateReviewAt('2026-01-01T00:00:00Z', 32), '2026-02-02T00:00:00.000Z');
  const result = createRetentionDryRun([{ id: 'f1', created_at: '2026-01-01T00:00:00Z', review_days: 32, authority_checked: true }], { asOf: '2026-03-01T00:00:00Z' });
  assert.equal(result.entries[0].state, 'DESCARTE_ELEGIVEL');
  assert.equal(result.deletes, 0);
});

test('UAAc remains evidence record and deduplicates without credits', () => {
  const first = createUAAcRecord({ record_id: 'u1', objective: 'test', evidence_hash: 'sha256:x', category: 'estudo', date: '2026-01-01', authorship: 'charlie' });
  const second = createUAAcRecord({ record_id: 'u2', objective: 'test copy', evidence_hash: 'sha256:x', category: 'estudo', date: '2026-01-02', authorship: 'charlie' });
  assert.equal('hours' in first, false);
  assert.deepEqual(deduplicateUAAcByEvidence([first, second]).duplicates, ['u2']);
});

test('formal linter ignores code, citations and exploratory dialogue', () => {
  assert.equal(lintFormalText('Conclusão: acho que funciona').valid, false);
  assert.equal(lintFormalText('> acho que funciona\n```\nacho\n```').valid, true);
  assert.equal(lintFormalText('acho que funciona', { mode: 'exploratory' }).valid, true);
});

test('emblem and academic package contracts fail closed', () => {
  assert.equal(validateEmblemMetadata({ asset_id: 'assets/images/emblema-universidade-do-futuro-1254.png', width: 1254, height: 1254, sha256: '44D4812A8B6FED95C834310CEC3E19CDC0CE67AD6D72AE2954F3C2F806C41031', tips: 9 }).valid, true);
  const base = { path: 'a.md', hash: 'sha256:a', version: '1' };
  assert.equal(buildGadAcademicManifest({ markdown: base, pdf: { path: 'a.pdf', hash: 'sha256:b', source_hash: 'sha256:a', version: '1' }, logo: { path: 'logo.png', hash: 'sha256:l', version: '1' }, publication_intent: true, human_gate: false }).valid, false);
});
