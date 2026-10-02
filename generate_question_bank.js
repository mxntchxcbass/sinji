#!/usr/bin/env node
'use strict';
const fs=require('fs');
const factory=require('./question_factory.js');
const arg=(name,def)=>{const i=process.argv.indexOf(name);return i>=0?process.argv[i+1]:def;};
const seed=Number(arg('--seed','20261002'))>>>0;
const count=Math.max(1,Math.min(40,Number(arg('--count','10'))||10));
const output=arg('--output','extra.json');
let state=seed||1;
Math.random=()=>{state=(state+0x6D2B79F5)>>>0;let t=state;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};
const q={};let id=1;
for(const [area] of factory.areas) for(const raw of factory.generate(area,count)) q[String(id++)]=factory.toBankItem(raw);
const doc={title:`창작 SKCT 유형 연습은행 · seed ${seed}`,q};
fs.writeFileSync(output,JSON.stringify(doc)+'\n','utf8');
console.log(`${Object.keys(q).length} items -> ${output} (seed=${seed})`);
