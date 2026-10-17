/* Laedt die Seite im Datensparmodus weniger? Zwei Durchgaenge gegen
   dieselbe Seite, einmal normal, einmal mit saveData. */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
const ZIEL = process.argv[2] || 'http://127.0.0.1:8099/index.html';
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe';
async function lauf(sparen, port){
  const ch=spawn(CHROME,['--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',`--user-data-dir=C:/Temp/wij3d/chrome-sp-${port}-${Date.now()}`,`--remote-debugging-port=${port}`,'about:blank'],{stdio:'ignore'});
  let u; for(let i=0;i<80;i++){try{const l=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();const p=l.find(t=>t.type==='page');if(p){u=p.webSocketDebuggerUrl;break}}catch{} await sleep(400);}
  const ws=new WebSocket(u); await new Promise(r=>ws.addEventListener('open',r,{once:true}));
  let id=0; const off=new Map(); const urls=new Map(); const gr=new Map(); const errs=[];
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data); if(m.id&&off.has(m.id)){off.get(m.id)(m);off.delete(m.id)}
    if(m.method==='Network.requestWillBeSent') urls.set(m.params.requestId, m.params.request.url);
    if(m.method==='Network.loadingFinished'){const k=urls.get(m.params.requestId)||'?'; gr.set(k,(gr.get(k)||0)+(m.params.encodedDataLength||0));}
    if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errs.push(m.params.entry.text);});
  const cmd=(m,p={})=>new Promise(r=>{const i=++id;off.set(i,r);ws.send(JSON.stringify({id:i,method:m,params:p}))});
  const js=async e=>(await cmd('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true})).result?.result?.value;
  await cmd('Page.enable'); await cmd('Runtime.enable'); await cmd('Network.enable'); await cmd('Log.enable');
  if (sparen) await cmd('Page.addScriptToEvaluateOnNewDocument', { source:
    "Object.defineProperty(navigator,'connection',{configurable:true,get:function(){return {saveData:true,effectiveType:'4g'};}});" });
  await cmd('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:2,mobile:true});
  await cmd('Page.navigate',{url:ZIEL+'?f='+Date.now()}); await sleep(11000);
  let summe=0; for(const v of gr.values()) summe+=v;
  const gal=[...gr.entries()].filter(([k])=>/gal-/.test(k));
  let galB=0; for(const [,v] of gal) galB+=v;
  const darf = await js('_darfVorladen()');
  const bilder = await js("!!document.querySelector('.modal-slide, #modalBody') || true");
  ws.close(); ch.kill();
  return { summe, dateien:gr.size, gal:gal.length, galB, darf, errs };
}
const a = await lauf(false, 9161);
const b = await lauf(true, 9162);
const P=[]; const ok=(n,v,e)=>P.push(`${(typeof e==='function'?e(v):JSON.stringify(v)===JSON.stringify(e))?'ok   ':'FEHL '} ${n}: ${JSON.stringify(v)}`);
P.push(`     normal:     ${(a.summe/1e6).toFixed(2)} MB, ${a.dateien} Dateien, davon ${a.gal} Galeriebilder (${(a.galB/1e6).toFixed(2)} MB)`);
P.push(`     Datensparen:${(b.summe/1e6).toFixed(2)} MB, ${b.dateien} Dateien, davon ${b.gal} Galeriebilder (${(b.galB/1e6).toFixed(2)} MB)`);
ok('normal laedt vor', a.darf, true);
ok('Datensparen laedt nicht vor', b.darf, false);
ok('Datensparen spart wirklich', a.summe - b.summe, v=>v > 3e6);
ok('Datensparen holt die Galerie nicht vor', b.gal, v=>v <= 8);
ok('normal holt die Galerie vor', a.gal, v=>v > 30);
ok('keine Konsolenfehler', a.errs.concat(b.errs), v=>v.length===0);
console.log(P.join('\n'));
process.exit(P.some(z=>z.startsWith('FEHL'))?1:0);
