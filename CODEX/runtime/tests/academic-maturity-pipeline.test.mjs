import test from 'node:test';
import assert from 'node:assert/strict';
import {
  MATURITY_STATES, buildMaturityManifest, createDriveIndexEntry,
  createMaturityRecord, createTeachingMaterial, transitionMaturity,
  validateCybersecurityGate, validatePublication
} from '../academic-maturity-pipeline.mjs';

const gate = { critical_open:false, high_unmitigated:false, tenant_isolation_tested:true, authz_complete:true, secret_in_artifact:false, rollback_demonstrated:true, incident_response_defined:true, integration_surface_known:true };
const event = (record, next, role = 'CODEX_TECNICO') => ({ actor_id:'synthetic-actor', role, origin:'local-sandbox', verb:'advance', evidence_id:'synthetic-evidence', previous_state:record.state, next_state:next, version:'v1', timestamp:'2026-08-23T12:00:00.00000Z', classification:'internal', risk:'low', justification:'synthetic test', rollback_id:'rollback-1' });

test('defines the complete M00-M23 state vocabulary', () => assert.equal(MATURITY_STATES.length, 24));
test('creates sanitized teaching material without copying content', () => {
  const result = createTeachingMaterial({ source_id:'doc-1', source_version:'v1', source_state:MATURITY_STATES[0], sanitized:true });
  assert.equal(result.canonical_claim, false);
  assert.throws(() => createTeachingMaterial({ source_id:'doc-1', source_version:'v1', source_state:MATURITY_STATES[0], sanitized:true, content:'real' }), /content_copy_forbidden|reference_only/);
});
test('blocks an academic transition when the cyber gate is not proven', () => {
  const record = createMaturityRecord({ id:'doc-1', version:'v1' });
  assert.throws(() => transitionMaturity(record, event(record, MATURITY_STATES[1]), { cyber_gate:{} }), /cyber_gate/);
});
test('requires five millisecond timestamp precision and provenance', () => {
  const record = createMaturityRecord({ id:'doc-1', version:'v1' });
  const invalid = { ...event(record, MATURITY_STATES[1]), timestamp:'2026-08-23T12:00:00Z' };
  assert.throws(() => transitionMaturity(record, invalid, { cyber_gate:gate }), /timestamp/);
});
test('advances with a complete fail-closed event', () => {
  const record = createMaturityRecord({ id:'doc-1', version:'v1' });
  const result = transitionMaturity(record, event(record, MATURITY_STATES[1]), { cyber_gate:gate });
  assert.equal(result.state, MATURITY_STATES[1]);
  assert.equal(result.history.length, 1);
});
test('requires human gate at approval states', () => {
  let record = createMaturityRecord({ id:'doc-1', version:'v1' });
  for (let i = 0; i < 8; i += 1) record = transitionMaturity(record, event(record, MATURITY_STATES[i + 1]), { cyber_gate:gate, human_gate:i === 7 });
  assert.equal(record.state, MATURITY_STATES[8]);
});
test('blocks publication by a non-library role', () => {
  assert.throws(() => validatePublication({ state:'M21_PUBLICACAO_BIBLIOTECA_AUTORIZADA', role:'CODEX_TECNICO', human_gate:true, cyber_gate:gate, evidence:{ version:'v1', hash:'h', genealogy:'g', sanitization:'s', access_classification:'internal' } }), /publication_role/);
});
test('allows publication only with role, evidence, cyber and human gates', () => {
  const result = validatePublication({ state:'M21_PUBLICACAO_BIBLIOTECA_AUTORIZADA', role:'BIBLIOTECARIO_IA', human_gate:true, cyber_gate:gate, evidence:{ version:'v1', hash:'sha256:h', genealogy:'g', sanitization:'s', access_classification:'internal' } });
  assert.equal(result.status, 'PUBLICATION_ALLOWED');
});
test('indexes Drive metadata only and rejects content or secrets', () => {
  const entry = createDriveIndexEntry({ file_id:'f1', folder_id:'d1', title:'Synthetic', mime_type:'text/markdown', parents:['p2','p1'], version:'v1', classification:'internal' });
  assert.deepEqual(entry.parents, ['p1','p2']);
  assert.throws(() => createDriveIndexEntry({ file_id:'f1', folder_id:'d1', title:'Synthetic', mime_type:'text/markdown', parents:['p1'], version:'v1', classification:'internal', raw_content:'x' }), /content_copy/);
  assert.throws(() => createDriveIndexEntry({ file_id:'f1', folder_id:'d1', title:'Synthetic', mime_type:'text/markdown', parents:['p1'], version:'v1', classification:'internal', access_token:'x' }), /secret_key/);
});
test('builds a deterministic manifest independent of input order', () => {
  const a = { file_id:'a', folder_id:'d', title:'A', mime_type:'text/plain', parents:['p'], version:'v1', classification:'internal' };
  const b = { file_id:'b', folder_id:'d', title:'B', mime_type:'text/plain', parents:['p'], version:'v1', classification:'internal' };
  assert.equal(buildMaturityManifest([a,b]).digest, buildMaturityManifest([b,a]).digest);
});
test('cyber gate fails closed for unknown integration surface', () => {
  assert.throws(() => validateCybersecurityGate({ ...gate, integration_surface_known:false }), /integration_unknown/);
});
