// Dependency-free render regression tests. No DOM, no network.
// Run: node scripts/test_render.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {escapeHtml,renderMarkdown,extractToc} from '../markdown.js';
import {__tests} from '../app.js';

const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const index=read('catalog/index.json');
const domains=index.domains.map(ref=>{const d=read(ref.path);return {...d,sources:read('catalog/sources/'+d.id+'.json').sources||[]}});
const noLeak=html=>{for(const bad of ['undefined','[object Object]','NaN',',,<'] )assert.ok(!html.includes(bad),'template leak "'+bad+'"')};

let failed=0;
function check(name,fn){try{fn();console.log('PASS '+name)}catch(e){failed++;console.error('FAIL '+name+'\n     '+String(e.message).split('\n')[0])}}

// ---- markdown.js ----
check('escapeHtml neutralises markup',()=>{
 assert.equal(escapeHtml('<img src=x onerror=1>'),'&lt;img src=x onerror=1&gt;');
 assert.equal(escapeHtml('a"b\'c&d'),'a&quot;b&#39;c&amp;d');
});
check('raw HTML in reports is escaped',()=>{
 const out=renderMarkdown('<script>alert(1)</script>');
 assert.ok(!out.includes('<script>'),'script tag leaked');
 assert.ok(out.includes('&lt;script&gt;'));
});
check('markdown links are https-only',()=>{
 assert.ok(renderMarkdown('[a](https://example.org/x)').includes('href="https://example.org/x"'));
 assert.ok(!renderMarkdown('[a](http://example.org)').includes('<a '),'http link was linkified');
 assert.ok(!renderMarkdown('[a](javascript:alert(1))').includes('<a '),'javascript: was linkified');
});
check('code spans keep literal formatting markers',()=>{
 const out=renderMarkdown('`a**b**c`');
 assert.ok(out.includes('<code>a**b**c</code>'),'code content was formatted: '+out);
 assert.ok(!out.includes('<strong>'),'bold leaked into a code span');
});
check('tables follow GFM pipe rules',()=>{
 const escaped=['| a | b |','| --- | --- |','| `x\\|y` | z |'].join('\n');
 const row=renderMarkdown(escaped).split('<tbody>')[1]||'';
 assert.equal((row.match(/<td>/g)||[]).length,2,'escaped pipe must stay in one cell: '+row);
 assert.ok(row.includes('<code>x|y</code>'),'escaped pipe inside code broken: '+row);
 const plain=['| a | b |','| --- | --- |','| x \\| y | z |'].join('\n');
 const row2=renderMarkdown(plain).split('<tbody>')[1]||'';
 assert.equal((row2.match(/<td>/g)||[]).length,2,'escaped text pipe must stay in one cell: '+row2);
 assert.ok(row2.includes('x | y'),'escaped pipe lost: '+row2);
 const unescaped=['| a | b |','| --- | --- |','| `x|y` | z |'].join('\n');
 const row3=renderMarkdown(unescaped).split('<tbody>')[1]||'';
 assert.equal((row3.match(/<td>/g)||[]).length,3,'unescaped pipe inside a code span splits per GFM: '+row3);
});
check('heading ids match the table of contents',()=>{
 const md='# One\n\n## Two **bold**\n';
 const toc=extractToc(md),out=renderMarkdown(md);
 assert.equal(toc.length,2);
 assert.deepEqual(toc.map(t=>t.id),['section-1','section-2']);
 for(const t of toc)assert.ok(out.includes('id="'+t.id+'"'),'missing '+t.id);
 assert.deepEqual(toc.map(t=>t.text),['One','Two bold']);
});

// ---- app.js render layer, exercised against the real catalog ----
const viewFns={overview:'renderOverview',issues:'renderIssues',reports:'renderReports',evidence:'renderEvidence',methods:'renderMethods',compare:'renderCompare'};
check('every view renders clean HTML from real catalog data',()=>{
 const markers={overview:'跨领域研究收录矩阵',issues:'id="issueResults"',reports:'report-grid',evidence:'id="sourceResults"',methods:'method-card',compare:'comparison-grid'};
 for(const [view,fn] of Object.entries(viewFns)){
  __tests.setData({index,domains,active:domains[0]});
  __tests.setRoute({view,issue:null,report:null});
  __tests.setFilters({term:'',priority:'all',category:'all',maturity:'all',sort:'priority'});
  const html=__tests[fn]();
  assert.ok(html.length>500,view+' rendered too little');
  assert.ok(html.includes(markers[view]),view+' missing marker '+markers[view]);
  noLeak(html);
 }
});
check('overview includes the cross-domain coverage matrix',()=>{
 __tests.setData({index,domains,active:domains[0]});
 __tests.setRoute({view:'overview',issue:null,report:null});
 const html=__tests.renderOverview();
 assert.ok(!html.includes('+renderCrossDomainMatrix()'),'dead call leaked into HTML');
 assert.ok(html.includes('跨领域研究收录矩阵'),'coverage matrix missing');
 for(const d of domains)assert.ok(html.includes('data-domain="'+d.id+'"'),'matrix row missing for '+d.id);
});
check('drawer markup numbers sections uniquely and honours optional fields',()=>{
 const domain=domains.find(d=>d.id==='ai-music');
 __tests.setData({index,domains,active:domain});
 const issue=domain.issues.find(i=>i.sop&&i.verification&&i.residualRisk&&i.evidenceLevel);
 assert.ok(issue,'fixture issue missing optional fields');
 const html=__tests.issueDrawerMarkup(domain,issue);
 const nums=[...html.matchAll(/<h3>(\d{2}) \/ /g)].map(m=>m[1]);
 assert.equal(new Set(nums).size,nums.length,'duplicate section numbers: '+nums.join(','));
 const expected=5+(issue.sop.length?1:0)+(issue.verification?1:0)+(issue.evidenceLevel?1:0)+(issue.residualRisk?1:0);
 assert.equal(nums.length,expected,'section count '+nums.length+' != '+expected);
 assert.ok(html.includes('执行 SOP')&&html.includes('核验方法')&&html.includes('证据等级')&&html.includes('残余风险'));
 assert.ok(html.includes('data-report="'+domain.reports[domain.reports.length-1].id+'"'));
 noLeak(html);
});
check('drawer survives a domain with no reports',()=>{
 const domain=domains.find(d=>d.id==='ai-fiction');
 __tests.setData({index,domains,active:domain});
 const html=__tests.issueDrawerMarkup({...domain,reports:[]},domain.issues[0]);
 assert.ok(!html.includes('data-report='),'report button shown without a report');
 noLeak(html);
});
check('search haystack matches tools and empty terms',()=>{
 const domain=domains.find(d=>d.id==='ai-coding');
 __tests.setData({index,domains,active:domain});
 const issue=domain.issues.find(i=>(i.solutions[0].tools||[]).length);
 const tool=issue.solutions[0].tools[0];
 __tests.setFilters({term:tool,priority:'all',category:'all',maturity:'all',sort:'priority'});
 assert.ok(__tests.filterIssues().some(x=>x.id===issue.id),'tool search missed '+issue.id+' for '+tool);
 __tests.setFilters({term:'',priority:'all',category:'all',maturity:'all',sort:'priority'});
 assert.equal(__tests.filterIssues().length,domain.issues.length,'empty term must match all');
 __tests.setFilters({term:'zzz-no-such-term-zzz',priority:'all',category:'all',maturity:'all',sort:'priority'});
 assert.equal(__tests.filterIssues().length,0);
});
check('filters narrow by priority and maturity',()=>{
 const domain=domains.find(d=>d.id==='ai-fiction');
 __tests.setData({index,domains,active:domain});
 __tests.setFilters({term:'',priority:'P0',category:'all',maturity:'all',sort:'priority'});
 const p0=__tests.filterIssues();
 assert.ok(p0.length>0&&p0.every(x=>x.priority==='P0'),'priority filter leaked');
 __tests.setFilters({term:'',priority:'all',category:'all',maturity:'M0',sort:'priority'});
 assert.ok(__tests.filterIssues().every(x=>x.maturity==='M0'),'maturity filter leaked');
});
check('metrics agree with the catalog',()=>{
 __tests.setData({index,domains,active:domains[0]});
 const m=__tests.metrics();
 assert.equal(m.domainCount,domains.length);
 assert.equal(m.issueCount,domains.reduce((n,d)=>n+d.issues.length,0));
 assert.equal(m.reportCount,domains.reduce((n,d)=>n+d.reports.length,0));
 assert.equal(m.sources,domains.reduce((n,d)=>n+d.sources.length,0));
 assert.equal(__tests.metrics(),m,'metrics must be memoised');
});

if(failed){console.error(failed+' render test(s) failed');process.exit(1)}
console.log('render tests: all passed');
