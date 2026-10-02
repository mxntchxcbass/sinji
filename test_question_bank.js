'use strict';
const assert=require('assert');
const factory=require('./question_factory.js');
const areas=['lang','data','math','logic','seq'];
for(const area of areas){
  for(const q of factory.generate(area,250)){
    assert.equal(q.area,area);
    assert.equal(q.choices.length,5,`${area}: expected five choices`);
    assert.equal(new Set(q.choices).size,5,`${area}: duplicate choices`);
    assert.ok(q.answer>=0&&q.answer<5,`${area}: invalid answer index`);
    assert.ok(q.explain&&q.explain.length>10,`${area}: missing explanation`);
    assert.ok(q.choices[q.answer]!==undefined,`${area}: missing keyed choice`);
    if(area==='seq'){
      const nums=(q.seq.match(/\d+/g)||[]).map(Number);
      assert.ok(nums.every(n=>n<2000),`sequence has an excessive term: ${nums}`);
      const nth=q.q.match(/(\d+)번째/);
      if(nth) assert.ok(Number(nth[1])<=9,'nth question must use a small n');
    }
  }
}
console.log('1,250 generated questions passed schema checks.');
