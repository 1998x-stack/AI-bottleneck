import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const idx=read('catalog/index.json');
assert.equal(idx.schemaVersion,1,'catalog schema version');
assert.ok(Array.isArray(idx.domains)&&idx.domains.length>0,'at least one published domain');
const unique=(arr,label)=>assert.equal(new Set(arr).size,arr.length,'duplicate '+label);
unique(idx.domains.map(d=>d.id),'domain ID');
let n=0,refs=0;
for(const ref of idx.domains){
 assert.match(ref.path,/^catalog\/domains\/[a-z0-9-]+\.json$/);
 const d=read(ref.path);assert.equal(d.id,ref.id);assert.equal(d.schemaVersion,1);
 assert.equal(d.issueCount,d.issues.length);
 assert.ok(d.title&&d.updatedAt&&d.description);
 unique(d.issues.map(i=>i.id),d.id+' issue ID');
 unique(d.reports.map(r=>r.id),d.id+' report ID');
 assert.ok(d.categories.length>0);
 const sourcePath='catalog/sources/'+d.id+'.json',sourceBundle=read(sourcePath);
 assert.equal(sourceBundle.domainId,d.id);
 unique(sourceBundle.sources.map(s=>s.id),'source ID');
 const sourceIds=new Set(sourceBundle.sources.map(s=>s.id));
 for(const s of sourceBundle.sources){
  assert.match(s.id,/^S\d+$/);
  assert.ok(/^https:\/\//.test(s.url),'source URL must be HTTPS: '+s.id);
  assert.ok(s.title&&s.type,'source title/type missing');
 }
 for(const r of d.reports){
  assert.match(r.path,/^reports\/[a-z0-9-]+\/[a-z0-9-]+\.md$/);
  assert.ok(fs.existsSync(r.path),'missing report '+r.path);
  assert.ok(fs.readFileSync(r.path,'utf8').length>500,'report too short');
 }
 for(const i of d.issues){
  assert.match(i.id,/^[A-Z]{2}-\d{2}$/);
  assert.ok(['P0','P1','P2'].includes(i.priority));
  assert.ok(['M0','M1','M2','M3'].includes(i.maturity));
  assert.ok(d.categories.includes(i.category));
  assert.ok(i.title&&i.summary&&i.rootCause);
  assert.ok(i.symptoms.length>=1&&i.metrics.length>=1);
  assert.ok(i.solutions.length>=1);
  assert.ok(i.sourceIds.length>=1);
  for(const s of i.solutions)assert.ok(s.name&&s.approach&&s.limitations);
  for(const sid of i.sourceIds)assert.ok(sourceIds.has(sid),'missing source '+sid+' for '+i.id);
  n++;refs+=i.sourceIds.length;
 }
 console.log('validated '+d.id+': '+d.issues.length+' issues, '+sourceBundle.sources.length+' sources, '+d.reports.length+' reports');
}
for(const f of ['index.html','styles.css','app.js','markdown.js','assets/favicon.svg','.github/workflows/pages.yml'])assert.ok(fs.existsSync(f),'missing site file '+f);
console.log('VALID: '+idx.domains.length+' domain(s), '+n+' issues, '+refs+' verified source citations.');
