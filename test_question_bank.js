const assert = require('node:assert/strict');
const fs = require('node:fs');

const bank = JSON.parse(fs.readFileSync('bank.json', 'utf8'));
const extra = JSON.parse(fs.readFileSync('extra.json', 'utf8'));
const allowedAreas = new Set(['lang', 'data', 'math', 'logic', 'seq']);

for (const [id, item] of Object.entries(extra.q)) {
  assert(allowedAreas.has(item.area), `unknown area at ${id}`);
  assert(Array.isArray(item.c) && item.c.length === 5, `expected five choices at ${id}`);
  assert.equal(new Set(item.c).size, 5, `duplicate choices at ${id}`);
  assert(Number.isInteger(item.a) && item.a >= 0 && item.a < item.c.length, `invalid key at ${id}`);
  assert(item._meta?.skill && item._meta?.difficulty && item._meta?.source_basis, `missing metadata at ${id}`);
  assert.match(item._meta.source_basis, /창작 연습문항/);
}

const seq = Object.entries(extra.q).filter(([, item]) => item.area === 'seq');
assert.equal(seq.length, 15, 'active sequence bank should contain the curated 15 items');
const expectedSequenceAnswers = {
  51: '20', 52: '96', 53: '37', 54: '11', 55: '63', 56: '34', 57: '36',
  58: '31', 59: '90', 60: '120', 61: '49', 62: '34', 63: '101', 64: '56', 65: '384',
};
for (const [id, expected] of Object.entries(expectedSequenceAnswers)) {
  const item = extra.q[id];
  assert.equal(item.c[item.a], expected, `sequence key mismatch at ${id}`);
  if (Number(id) >= 58) {
    const n = Number(item.q.match(/(\d+)번째 항/)?.[1]);
    assert(n >= 8 && n <= 12, `Nth index outside target range at ${id}`);
  }
}

assert.equal(extra.q['35'].c[extra.q['35'].a], '26,400원');
assert.equal(extra.q['40'].c[extra.q['40'].a], '13,200원');
assert.equal(extra.q['102'].c[extra.q['102'].a], '27개');
assert.equal(extra.q['103'].c[extra.q['103'].a], '62개');
assert.equal(extra.q['104'].c[extra.q['104'].a], 'A-C-B-D');

const legacySeqCount = Object.values(bank)
  .flatMap(set => Object.values(set.q || {}))
  .filter(item => item.area === 'seq').length;
assert(legacySeqCount > 0, 'expected legacy source sequence items to remain archived in bank.json');
const page = fs.readFileSync('index.html', 'utf8');
assert.match(page, /if\(area==='seq' && t!=='x1'\) return/,
  'legacy bank sequences must remain excluded from active sequence practice');

console.log(`Validated ${Object.keys(extra.q).length} active extra items, including 15 calibrated sequences and targeted answer checks.`);
