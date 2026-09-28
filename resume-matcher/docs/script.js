const $=id=>document.getElementById(id);
const STOP=new Set("a an the and or of to in for with on at by is are be as from that this it its we you our your will can not have has".split(" "));
const W={sim:.35,sk:.5,exp:.15};
const esc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
const TAX=SKILLS.map(k=>({s:k.s,pats:[k.s,...k.a].map(n=>new RegExp(`(?<![\\w+#])${esc(n.toLowerCase())}(?![\\w+#])`))}));
const RANK={none:0,diploma:1,bachelors:2,masters:3,phd:4};
const DEG={phd:/\b(ph\.?d|doctorate)\b/,masters:/\b(master'?s?|m\.?sc|m\.?tech|mba)\b/,bachelors:/\b(bachelor'?s?|b\.?sc|b\.?tech)\b/,diploma:/\bdiploma\b/};

const skillsIn=t=>{t=t.toLowerCase();return new Set(TAX.filter(k=>k.pats.some(p=>p.test(t))).map(k=>k.s))};
const years=t=>Math.max(0,...[...t.matchAll(/(\d{1,2})\s*\+?\s*(?:years?|yrs?)/gi)].map(m=>+m[1]));
const edu=t=>{t=t.toLowerCase();let b="none";for(const[k,r]of Object.entries(DEG))if(r.test(t)&&RANK[k]>RANK[b])b=k;return b};
const anonymise=t=>t.replace(/[\w.+-]+@[\w-]+\.[\w.-]+/g," ").replace(/\+?\d[\d\s().-]{8,}\d/g," ").replace(/(https?:\/\/\S+|www\.\S+|linkedin\.com\/\S+|github\.com\/\S+)/gi," ").replace(/\b(male|female|he\/him|she\/her|they\/them|mr\.?|mrs\.?|ms\.?)\b/gi," ");

const tok=t=>(t.toLowerCase().match(/[a-z0-9+#.]+/g)||[]).map(w=>w.replace(/^\.+|\.+$/g,"")).filter(w=>w&&!STOP.has(w));
function grams(t){const w=tok(t),m={};w.forEach((x,i)=>{m[x]=(m[x]||0)+1;if(i){const g=w[i-1]+" "+x;m[g]=(m[g]||0)+1}});return m}
function tfidf(a,b){const A=grams(a),B=grams(b);let d=0,na=0,nb=0;new Set([...Object.keys(A),...Object.keys(B)]).forEach(k=>{const df=(A[k]?1:0)+(B[k]?1:0),idf=Math.log(3/(1+df))+1,x=(A[k]||0)*idf,y=(B[k]||0)*idf;d+=x*y;na+=x*x;nb+=y*y});return na&&nb?d/Math.sqrt(na*nb):0}

function analyse(resume,jd){
  const rs=skillsIn(resume),js=skillsIn(jd),ry=years(resume),jy=years(jd),re=edu(resume),je=edu(jd);
  const matched=[...js].filter(s=>rs.has(s)),missing=[...js].filter(s=>!rs.has(s));
  const sim=tfidf(resume,jd),sk=js.size?matched.length/js.size:0;
  const parts=[];if(jy)parts.push(Math.min(ry/jy,1));if(je!=="none")parts.push(RANK[re]>=RANK[je]?1:.5);
  const ex=parts.length?parts.reduce((a,b)=>a+b)/parts.length:1;
  return{overall:W.sim*sim+W.sk*sk+W.exp*ex,sim,sk,ex,matched,missing,ry,re,js};
}

function render(r){
  $("out").hidden=false;
  const p=Math.round(r.overall*100);
  $("arc").style.strokeDashoffset=251.3*(1-Math.min(r.overall/.8,1));
  $("pct").textContent=p+"%";
  $("verdict").textContent=p>=60?"Strong match":p>=40?"Partial match":"Needs work";
  $("detail").textContent=`You cover ${r.matched.length} of ${r.js.size} skills in the job description. Detected ${r.ry} years of experience and education: ${r.re}.`;
  $("parts").innerHTML=[["Text similarity",r.sim],["Skill coverage",r.sk],["Experience fit",r.ex]].map(([n,v])=>`<div class="part"><b>${n}<span>${Math.round(v*100)}%</span></b><i><span style="width:${v*100}%"></span></i></div>`).join("");
  $("strip").innerHTML=[...r.matched.map(s=>`<span class="chip on">${s}</span>`),...r.missing.map(s=>`<span class="chip off">${s}</span>`)].join("")||"No known skills found in the job description.";
  $("recs").innerHTML=r.missing.map(s=>{const x=RECS[s]||{};return `<li><b>${s}</b><br>${x.t||"Add a project or bullet showing hands-on "+s+"."} ${x.r?`<a href="${x.r}" target="_blank" rel="noopener">Learn more</a>`:""}</li>`}).join("")||"<li>No gaps found. Your resume covers every skill listed.</li>";
  $("out").scrollIntoView({behavior:"smooth"});
}

async function readFile(f){
  const ext=f.name.split(".").pop().toLowerCase(),buf=await f.arrayBuffer();
  if(ext==="txt")return new TextDecoder().decode(buf);
  if(ext==="docx")return(await mammoth.extractRawText({arrayBuffer:buf})).value;
  if(ext==="pdf"){pdfjsLib.GlobalWorkerOptions.workerSrc="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
    const d=await pdfjsLib.getDocument({data:buf}).promise;let s="";
    for(let i=1;i<=d.numPages;i++)s+=(await(await d.getPage(i)).getTextContent()).items.map(x=>x.str).join(" ")+"\n";return s}
  throw new Error("Use a PDF, DOCX or TXT file.");
}
async function load(f){
  $("err").textContent="";
  try{$("resume").value=await readFile(f);$("fname").textContent=f.name}
  catch(e){$("err").textContent="Could not read that file: "+e.message+" You can paste the text instead."}
}
$("file").onchange=e=>e.target.files[0]&&load(e.target.files[0]);
const drop=$("drop");
["dragover","dragenter"].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.add("drag")}));
["dragleave","drop"].forEach(ev=>drop.addEventListener(ev,()=>drop.classList.remove("drag")));
drop.addEventListener("drop",e=>{e.preventDefault();e.dataTransfer.files[0]&&load(e.dataTransfer.files[0])});
$("sample").onclick=()=>{$("resume").value=SAMPLE.resume;$("jd").value=SAMPLE.jd;$("fname").textContent="Sample resume loaded"};
$("go").onclick=()=>{
  let r=$("resume").value.trim(),j=$("jd").value.trim();
  if(!r||!j){$("err").textContent="Add both a resume and a job description first.";return}
  $("err").textContent="";render(analyse($("anon").checked?anonymise(r):r,j));
};
