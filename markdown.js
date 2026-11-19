// Minimal dependency-free Markdown reader for reviewed, repository-owned research documents.
// It escapes raw HTML, permits only absolute https Markdown links, protects inline code from
// emphasis parsing, and keeps escaped pipes inside a single table cell.
export function escapeHtml(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}
function inline(s){
 let a=escapeHtml(s);
 const codes=[];
 a=a.replace(/`([^`]+)`/g,(_m,c)=>{codes.push(c);return '\u0000'+(codes.length-1)+'\u0000'});
 a=a.replace(/\[([^\]]+)\]\((https:\/\/[^\s)]+)\)/g,(_m,label,url)=>'<a href="'+escapeHtml(url)+'" target="_blank" rel="noopener noreferrer">'+label+'</a>');
 a=a.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
 a=a.replace(/~~(.+?)~~/g,'<del>$1</del>');
 a=a.replace(/(?<!\*)\*([^*\n]+)\*(?!\*)/g,'<em>$1</em>');
 a=a.replace(/\u0000(\d+)\u0000/g,(_m,i)=>'<code>'+codes[+i]+'</code>');
 return a;
}
const heading=/^(#{1,6})\s+(.+)$/;
export function extractToc(markdown){
 const lines=String(markdown).replace(/\r\n?/g,'\n').split('\n'),toc=[];let code=false,count=0;
 for(const line of lines){if(/^\s*```/.test(line)){code=!code;continue}if(code)continue;const m=line.match(heading);if(m){count++;toc.push({id:'section-'+count,level:m[1].length,text:m[2].replace(/\*\*/g,'').trim()})}}
 return toc;
}
function tableCells(s){let x=s.trim();if(x.startsWith('|'))x=x.slice(1);if(x.endsWith('|')&&!x.endsWith('\\|'))x=x.slice(0,-1);const out=[];let cur='';for(let i=0;i<x.length;i++){const ch=x[i];if(ch==='\\'&&x[i+1]==='|'){cur+='|';i++;continue}if(ch==='|'){out.push(cur);cur='';continue}cur+=ch}out.push(cur);return out.map(a=>a.trim())}
function isSeparator(s){return /^\s*\|?\s*:?-{3,}:?(?:\s*\|\s*:?-{3,}:?)*\s*\|?\s*$/.test(s)}
export function renderMarkdown(markdown){
 const lines=String(markdown).replace(/\r\n?/g,'\n').split('\n'),out=[];let para=[],list=null,quote=false,code=false,codeLines=[],count=0;
 function flush(){if(para.length){out.push('<p>'+para.map(inline).join(' ')+'</p>');para=[]}}
 function closeList(){if(list){out.push('</'+list+'>');list=null}}
 function closeQuote(){if(quote){out.push('</blockquote>');quote=false}}
 function codeEnd(){out.push('<pre><code>'+escapeHtml(codeLines.join('\n'))+'</code></pre>');codeLines=[]}
 for(let i=0;i<lines.length;i++){
  const line=lines[i],trim=line.trim();
  if(/^\s*```/.test(line)){flush();closeList();closeQuote();if(code){codeEnd();code=false}else{code=true}continue}
  if(code){codeLines.push(line);continue}
  if(!trim){flush();closeList();closeQuote();continue}
  if(/^\s*(?:---+|___+)\s*$/.test(line)){flush();closeList();closeQuote();out.push('<hr/>');continue}
  const hd=line.match(heading);if(hd){flush();closeList();closeQuote();count++;const level=Math.min(4,hd[1].length);out.push('<h'+level+' id="section-'+count+'">'+inline(hd[2])+'</h'+level+'>');continue}
  if(line.includes('|')&&i+1<lines.length&&isSeparator(lines[i+1])){flush();closeList();closeQuote();let body='<table><thead><tr>'+tableCells(line).map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>';i+=2;while(i<lines.length&&lines[i].trim()&&lines[i].includes('|')){body+='<tr>'+tableCells(lines[i]).map(c=>'<td>'+inline(c)+'</td>').join('')+'</tr>';i++}i--;out.push(body+'</tbody></table>');continue}
  const qm=line.match(/^\s*>\s?(.*)$/);if(qm){flush();closeList();if(!quote){out.push('<blockquote>');quote=true}out.push('<p>'+inline(qm[1])+'</p>');continue}
  if(quote)closeQuote();
  const lm=line.match(/^\s*(?:([-*+])\s+|(\d+)\.\s+)(.+)$/);if(lm){flush();const typ=lm[2]?'ol':'ul';if(list!==typ){closeList();out.push('<'+typ+'>');list=typ}out.push('<li>'+inline(lm[3])+'</li>');continue}
  closeList();para.push(trim);
 }
 flush();closeList();closeQuote();if(code)codeEnd();return out.join('\n');
}
