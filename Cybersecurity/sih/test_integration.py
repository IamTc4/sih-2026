from fraud_detector import FraudDetector, DetectorConfig, TransactionGraph
from evidence_trail import EvidenceTrailService
from policy import RBACEnforcer, UserContext, UserRole, redact_payload, DataClassification

# Test 1: Fraud detector creates graph and detects
graph = TransactionGraph()
now = 1000000.0
for i in range(15):
    graph.add_transaction(f'tx{i}', f'src{i}', 'mixer', 1.0, now+i)
for i in range(15):
    graph.add_transaction(f'tx{15+i}', 'mixer', f'dst{i}', 1.0, now+20+i)

detector = FraudDetector(DetectorConfig(scam_blacklist={'bad'}))
results = detector.detect(graph)
print(f'FraudDetector: {len(results)} results')
for r in results:
    print(f'  {r.signature}: conf={r.confidence:.2f}, evidence={len(r.evidence)} txs')

# Test 2: Evidence trail logs the detection
trail = EvidenceTrailService('integration_test.db')
for r in results:
    entry = trail.log_event('fraud_detection', {
        'address': r.metadata.get('address'),
        'signature': r.signature,
        'confidence': r.confidence,
        'evidence': r.evidence
    })
    print(f'Logged entry {entry.entry_id}: chain_hash={entry.chain_hash[:16]}...')

# Test 3: Verify chain integrity
verify = trail.verify_chain()
print(f'Chain valid: {verify["valid"]}, entries: {verify["entries_checked"]}')

# Test 4: RBAC filters detection results for different roles
rbac = RBACEnforcer()
sample_result = {
    'address': '0xabc',
    'signatures': results[0].__dict__ if results else {},
    'risk_score': 0.85,
    'victim_name': 'John Doe',
    'victim_email': 'john@example.com'
}

viewer = UserContext('u1', UserRole.VIEWER)
investigator = UserContext('u2', UserRole.INVESTIGATOR)

filtered_viewer = rbac.filter_response(sample_result, viewer)
filtered_inv = rbac.filter_response(sample_result, investigator)

print(f'Viewer sees: {list(filtered_viewer.keys())}')
print(f'  victim_name: {filtered_viewer.get("victim_name")}')
print(f'Investigator sees: {list(filtered_inv.keys())}')
print(f'  victim_name: {filtered_inv.get("victim_name")}')

# Test 5: Redaction
redacted = redact_payload(sample_result, 'viewer')
print(f'Redacted for viewer: victim_email={redacted.get("victim_email")}')

print('\nAll integrations working!')