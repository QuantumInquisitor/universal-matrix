import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {validate, frameAt, project, mechanicalLabel} from '../docs/docs/material-viewer-model.mjs';
const read=()=>JSON.parse(readFileSync(new URL('../docs/docs/material-viewer-example.json',import.meta.url),'utf8'));
test('example provenance matches committed source and executed modules',()=>{
 const source=readFileSync(new URL('../docs/experiments/material-viewer-source.json',import.meta.url),'utf8').replace(/\r\n/g,'\n');
 const sha=text=>createHash('sha256').update(text).digest('hex');
 assert.equal(sha(source),read().source_report.sha256_normalized_text);
 for(const [name,hash] of Object.entries(JSON.parse(source).sources))assert.equal(sha(readFileSync(new URL('../scripts/'+name,import.meta.url),'utf8').replace(/\r\n/g,'\n')),hash,name);
});
test('computed export keeps source geometry and ledgers',()=>{const d=validate(read());assert.equal(d.module_count,4);assert.ok(d.frames.length>1);assert.equal(d.frames.at(-1).time_s,.4);assert.match(d.source_report.sha256_normalized_text,/^[a-f0-9]{64}$/);});
test('displayed states and ledgers equal the computed source samples',()=>{
 const source=JSON.parse(readFileSync(new URL('../docs/experiments/material-viewer-source.json',import.meta.url),'utf8')).cases.powered.samples;
 const frames=read().frames;assert.equal(frames.length,source.length);
 frames.forEach((f,i)=>{const s=source[i];assert.equal(f.time_s,s.time_s);assert.deepEqual(f.edge_potential_j,s.edge_potential_j);assert.deepEqual(f.edge_work_j,s.edge_work_j);
 f.modules.forEach((m,j)=>{assert.deepEqual(m.q,s.q[j]);assert.deepEqual(m.rates,s.rates[j]);for(const key of ['mechanical_j','reserve_j','delivered_work_j','input_j'])assert.equal(m[key],s[key][j]);for(const key of ['damping','conversion','leakage'])assert.equal(m.losses_j[key],s[key+'_loss_j'][j]);});});
});
for(const [name,change] of [
 ['units',d=>d.units.source_length='mm'],
 ['time order',d=>d.frames[1].time_s=d.frames[0].time_s],
 ['scale mismatch',d=>d.frames[0].modules[0].bodies[0].vertices_display[0][0]+=1],
 ['missing loss',d=>delete d.frames[0].modules[0].losses_j.damping],
 ['nonfinite geometry',d=>d.frames[0].modules[0].bodies[0].vertices_m[0][0]=Infinity],
 ['changing identity',d=>d.frames[1].modules[0].id='other'],
])test(`reject ${name}`,()=>{const d=read();change(d);assert.throws(()=>validate(d));});
test('nonuniform playback uses physical timestamps and clamps',()=>{const f=[{time_s:0},{time_s:.03},{time_s:.2}];assert.equal(frameAt(f,.02),0);assert.equal(frameAt(f,.03),1);assert.equal(frameAt(f,4),2);});
test('projection rotates all three source dimensions without changing norm',()=>{const p=project([1,2,3],.6,.4);assert.ok(Math.abs(Math.hypot(...p)-Math.sqrt(14))<1e-12);assert.notDeepEqual(project([1,2,0],.6,.4).slice(0,2),p.slice(0,2));});

test('mechanical display preserves values and legacy absence',()=>{
 const d=read();assert.equal(mechanicalLabel(d.frames[0].modules[0]),d.frames[0].modules[0].mechanical_j.toExponential(6)+' J');
 for(const f of d.frames)for(const m of f.modules)delete m.mechanical_j;
 validate(d);assert.equal(mechanicalLabel(d.frames[0].modules[0]),'Unavailable in this export');
});
for(const value of [undefined,NaN,Infinity,'0'])test(`reject partial or invalid mechanical energy ${value}`,()=>{
 const d=read();d.frames[1].modules[0].mechanical_j=value;assert.throws(()=>validate(d));
});
