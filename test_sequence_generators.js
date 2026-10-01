const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const html = fs.readFileSync('index.html', 'utf8');
assert.match(html, /\['빈칸 추론',12,\[genCalSeqBlank\]\]/);
assert.match(html, /\['N번째 항',8,\[genCalSeqNth\]\]/);
assert.match(html, /if\(area==='seq' && t!=='x1'\) return/);

const start = html.indexOf('function makeCalibratedSeq()');
const end = html.indexOf('const PLAN_SEQ=', start);
assert(start >= 0 && end > start, 'calibrated sequence generator block must exist');
const generatorSource = html.slice(start, end);

function createSeededContext(seed) {
  let state = seed >>> 0;
  const random = () => {
    state = (state * 1664525 + 1013904223) >>> 0;
    return state / 0x100000000;
  };
  const seededMath = Object.create(Math);
  seededMath.random = random;
  const shuffle = items => {
    const copy = items.slice();
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  };
  const context = {
    Math: seededMath,
    randInt: (min, max) => Math.floor(random() * (max - min + 1)) + min,
    shuffle,
    pickDistinct: (ans, candidates, positiveOnly) => {
      const distractors = [];
      for (const value of candidates) {
        const rounded = Math.round(value);
        if (!Number.isFinite(rounded) || rounded === ans || distractors.includes(rounded)) continue;
        if (positiveOnly && rounded <= 0) continue;
        distractors.push(rounded);
      }
      for (let delta = 1; distractors.length < 4; delta++) {
        for (const value of [ans + delta, ans - delta]) {
          if (value !== ans && !distractors.includes(value) && (!positiveOnly || value > 0)) distractors.push(value);
          if (distractors.length === 4) break;
        }
      }
      const options = shuffle([ans, ...shuffle(distractors).slice(0, 4)]);
      return {choices: options.map(String), answer: options.indexOf(ans)};
    },
    genMidBlank: () => { throw new Error('unexpected blank fallback'); },
    genNthTerm: () => { throw new Error('unexpected nth-term fallback'); },
  };
  vm.createContext(context);
  vm.runInContext(generatorSource, context);
  return context;
}

for (let seed = 1; seed <= 500; seed++) {
  const context = createSeededContext(seed);
  for (const make of [context.genCalSeqBlank, context.genCalSeqNth]) {
    const q = make();
    assert.equal(q.choices.length, 5);
    assert.equal(new Set(q.choices).size, 5);
    assert(q.difficulty === '기초' || q.difficulty === '표준');
    assert.equal(q.choices[q.answer], q.explain.match(/(?:빈칸은|항은) ([\d-]+)입니다\./)?.[1]);
  }
  const nth = context.genCalSeqNth();
  const n = Number(nth.q.match(/(\d+)번째 항/)[1]);
  assert(n >= 8 && n <= 10, `Nth index ${n} is outside the intended range`);
  assert(Number.isInteger(Number(nth.choices[nth.answer])));
  assert(Math.abs(Number(nth.choices[nth.answer])) <= 2000, 'Nth answer is too large');
}

console.log('500 seeded blank and Nth-term sequence runs passed key, option, difficulty, and size checks.');
