const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const html = fs.readFileSync('index.html', 'utf8');
assert.match(html, /\['빈칸 추론',12,/);
assert.match(html, /\['N번째 항',8,/);

const start = html.indexOf('function makeSeqHard()');
const end = html.indexOf('function genFracSeqHard()', start);
assert(start >= 0 && end > start, 'sequence generator block must exist');
const generatorSource = html.slice(start, end);

function createSeededContext(seed) {
  let state = seed >>> 0;
  const random = () => {
    state = (state * 1664525 + 1013904223) >>> 0;
    return state / 0x100000000;
  };
  const seededMath = Object.create(Math);
  seededMath.random = random;
  const context = {
    Math: seededMath,
    randInt: (min, max) => Math.floor(random() * (max - min + 1)) + min,
    pickOne: items => items[Math.floor(random() * items.length)],
    shuffle: items => {
      const copy = items.slice();
      for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }
      return copy;
    },
    pickN: (items, count) => {
      const copy = items.slice();
      for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }
      return copy.slice(0, count);
    },
    nf: value => Number(value).toLocaleString('en-US'),
    eul: value => value,
    genNthTerm: () => { throw new Error('unexpected Nth-term fallback'); },
  };
  vm.createContext(context);
  vm.runInContext(generatorSource, context);
  return context;
}

for (let seed = 1; seed <= 500; seed++) {
  const q = createSeededContext(seed).genSeqHardNth();
  const n = Number(q.q.match(/(\d+)번째 항/)[1]);
  const answer = Number(q.choices[q.answer]);
  assert(n >= 8 && n <= 12, `Nth index ${n} is outside the intended range`);
  assert(Number.isInteger(answer) && Math.abs(answer) <= 10000,
    `Nth answer ${q.choices[q.answer]} is too large or invalid`);
  assert.equal(q.choices.length, 5);
  assert.equal(new Set(q.choices).size, 5);
  assert.equal(q.choices[q.answer], String(answer));
}

console.log('500 seeded Nth-term questions passed range, answer-size, and choice checks.');
