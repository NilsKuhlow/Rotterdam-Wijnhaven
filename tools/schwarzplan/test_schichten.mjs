/* Der Schichtstapel: Reihenfolge, Schalter, Regler in 20er Schritten,
   und was das Ganze an Rechenzeit im Leerlauf kostet. */
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';
const ZIEL = process.argv[2] || 'http://127.0.0.1:8099/index.html';
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe', PORT=9141;
const chrome=spawn(CHROME,['--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',`--user-data-dir=C:/Temp/wij3d/chrome-sch-${Date.now()}`,`--remote-debugging-port=${PORT}`,'about:blank'],{stdio:'ignore'});
let u; for(let i=0;i<80;i++){try{const l=await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();const p=l.find(t=>t.type==='page');if(p){u=p.webSocketDebuggerUrl;break}}catch{} await sleep(400);}
const ws=new WebSocket(u); await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let id=0; const off=new Map(); const errs=[]; const req=[];
ws.addEventListener('message',e=>{const m=JSON.parse(e.data); if(m.id&&off.has(m.id)){off.get(m.id)(m);off.delete(m.id)}
  if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errs.push(m.params.entry.text);
  if(m.method==='Runtime.exceptionThrown')errs.push(m.params.exceptionDetails.text);
  if(m.method==='Network.requestWillBeSent')req.push(m.params.request.url);});
const cmd=(m,p={})=>new Promise(r=>{const i=++id;off.set(i,r);ws.send(JSON.stringify({id:i,method:m,params:p}))});
const js=async e=>(await cmd('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true})).result?.result?.value;
const knipse=async n=>{const s=await cmd('Page.captureScreenshot',{format:'png'});writeFileSync('C:/Temp/wij3d/pres/'+n,Buffer.from(s.result.data,'base64'));};
await cmd('Page.enable'); await cmd('Runtime.enable'); await cmd('Log.enable');
await cmd('Network.enable'); await cmd('Performance.enable');
await cmd('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:2,mobile:true});
await cmd('Page.navigate',{url:ZIEL+'?f='+Date.now()}); await sleep(8000);
const P=[]; const ok=(n,v,e)=>P.push(`${(typeof e==='function'?e(v):JSON.stringify(v)===JSON.stringify(e))?'ok   ':'FEHL '} ${n}: ${JSON.stringify(v)}`);
await js('window.scrollTo(0, Math.round(getIntroH()*0.95))'); await sleep(1800);

/* ── Reihenfolge im Stapel ── */
ok('aelteste Karte zuunterst', await js(`(function(){
  var g=document.getElementById('mapSvg');
  var n=[...g.children].map(function(c){return c.id||c.className.baseVal||c.tagName});
  return n.slice(0,4);})()`), v=>Array.isArray(v) && v.indexOf('ov-1940')===0
     && v.indexOf('ov-heute')>0 && v.indexOf('ov-ebene')>v.indexOf('ov-heute'));
ok('drei Zeilen, oben zuerst', await js("[...document.querySelectorAll('#ebenen .eb-zeile')].map(z=>z.id)"),
   ['eb-zeile-revisie','eb-zeile-heute','eb-zeile-1940']);
ok('gesperrte Zeile ist weg', await js("document.getElementById('eb-zeile-revisie').hidden"), true);

/* ── Anfangszustand ── */
ok('Heute an', await js("document.getElementById('eb-an-heute').getAttribute('aria-checked')"), 'true');
ok('Heute voll', await js("document.getElementById('ov-heute').getAttribute('opacity')"), '1.00');
ok('1940 aus', await js("document.getElementById('eb-an-1940').getAttribute('aria-checked')"), 'false');
ok('1940 Regler gesperrt', await js("document.getElementById('eb-regler-1940').disabled"), true);
ok('1940 noch nicht geladen', req.filter(u=>/plan-1940-ebene/.test(u)).length, 0);

/* ── Schritte von 20 ── */
ok('Regler in 20er Schritten', await js("[...document.querySelectorAll('#ebenen input[type=range]')].map(r=>r.step)"),
   ['20','20','20']);

/* ── Schalten ── */
await js("ebeneSchalten('1940')"); await sleep(2500);
ok('1940 an', await js("document.getElementById('eb-an-1940').getAttribute('aria-checked')"), 'true');
ok('1940 mit Vorgabewert', await js("document.getElementById('ov-1940').getAttribute('opacity')"), '0.60');
ok('1940 jetzt geladen', req.filter(u=>/plan-1940-ebene/.test(u)).length, n=>n>=1);
ok('Quellenzeile da', await js("document.getElementById('eb-quelle').hidden"), false);

await js("ebeneSchalten('heute')"); await sleep(700);
ok('Heute aus: durchsichtig', await js("document.getElementById('ov-heute').getAttribute('opacity')"), '0.00');
ok('Heute aus: Regler gesperrt', await js("document.getElementById('eb-regler-heute').disabled"), true);
ok('Heute aus: Wert bleibt stehen', await js("EBENEN['heute'].wert"), 100);
await knipse('Q1_nur1940.png');
await js("ebeneSchalten('heute')"); await sleep(700);
ok('Heute wieder an, mit altem Wert', await js("document.getElementById('ov-heute').getAttribute('opacity')"), '1.00');

/* ── Regler auf null heisst aus ── */
await js("ebeneDeckung('1940', 0)"); await sleep(500);
ok('auf null gezogen: Schalter aus', await js("document.getElementById('eb-an-1940').getAttribute('aria-checked')"), 'false');
ok('auf null gezogen: Quellenzeile weg', await js("document.getElementById('eb-quelle').hidden"), true);
await js("ebeneSchalten('1940')"); await sleep(600);
ok('wieder an: nicht bei null stehengeblieben', await js("EBENEN['1940'].wert"), 60);
await js("ebeneDeckung('1940', 40)"); await sleep(600);
ok('40 Prozent', await js("document.getElementById('ov-1940').getAttribute('opacity')"), '0.40');
ok('Anzeige stimmt', await js("document.getElementById('eb-zahl-1940').textContent"), '40 %');
await knipse('Q2_stapel.png');

/* ── dreisprachig ── */
for (const [l,t] of [['nl','Vandaag'],['en','Today']]){
  await js(`setLang('${l}')`); await sleep(500);
  ok(`${l}: Heute`, await js("document.getElementById('eb-an-heute').textContent"), t);
}
await js("setLang('de')"); await sleep(400);

/* ── Was kostet die Seite im Leerlauf? ── */
const metrik = async () => {
  const r = await cmd('Performance.getMetrics');
  const o = {}; (r.result?.metrics||[]).forEach(m=>o[m.name]=m.value); return o;
};
async function ruhe(sekunden){
  const a = await metrik(); await sleep(sekunden*1000); const b = await metrik();
  return { skript:(b.ScriptDuration-a.ScriptDuration)/sekunden,
           layout:(b.LayoutDuration-a.LayoutDuration)/sekunden,
           stil:(b.RecalcStyleDuration-a.RecalcStyleDuration)/sekunden,
           gesamt:(b.TaskDuration-a.TaskDuration)/sekunden };
}
await js("ebeneSchalten('1940')"); await sleep(600);   /* beide Schichten aus bis auf heute */
const leer = await ruhe(8);
P.push(`     Leerlauf, nur heute:   Skript ${(leer.skript*1000).toFixed(1)} ms/s, Layout ${(leer.layout*1000).toFixed(1)}, Stil ${(leer.stil*1000).toFixed(1)}, gesamt ${(leer.gesamt*100).toFixed(2)} % einer CPU`);
await js("ebeneDeckung('1940', 60)"); await sleep(1200);
const beide = await ruhe(8);
P.push(`     Leerlauf, zwei Schichten: Skript ${(beide.skript*1000).toFixed(1)} ms/s, Layout ${(beide.layout*1000).toFixed(1)}, Stil ${(beide.stil*1000).toFixed(1)}, gesamt ${(beide.gesamt*100).toFixed(2)} % einer CPU`);
ok('Leerlauf kostet fast nichts', Math.max(leer.gesamt, beide.gesamt), v=>v < 0.02);
ok('kein Dauerlaeufer im Skript', Math.max(leer.skript, beide.skript), v=>v < 0.01);

ok('keine Konsolenfehler', errs, a=>a.length===0);
console.log(P.join('\n'));
if (errs.length) console.log('Fehler:', errs.slice(0,4));
ws.close(); chrome.kill(); process.exit(P.some(z=>z.startsWith('FEHL'))?1:0);
