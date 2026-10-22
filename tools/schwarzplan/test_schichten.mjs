/* Der Kartenstand: ein Knopf, zwei Staende, kein Dazwischen.
   Geprueft wird die Reihenfolge im Stapel, dass die Regler wirklich weg
   sind, dass die Karte von 1940 erst beim ersten Umschalten geladen wird,
   und was die Seite im Leerlauf an Rechenzeit kostet. */
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
ok('1940 liegt unter heute', await js(`(function(){
  var g=document.getElementById('mapSvg');
  var n=[...g.children].map(function(c){return c.id||c.className.baseVal||c.tagName});
  return [n.indexOf('ov-1940'), n.indexOf('ov-heute')];})()`),
   v=>Array.isArray(v) && v[0]===0 && v[1]>0);

/* ── Die Regler sind weg, und zwar ganz ── */
ok('keine Regler mehr im Kartenfeld', await js("document.querySelectorAll('#ebenen input[type=range]').length"), 0);
ok('keine Regler mehr auf der Seite', await js("document.querySelectorAll('input[type=range]').length"), 0);
ok('keine Schichtzeilen mehr', await js("document.querySelectorAll('.eb-zeile').length"), 0);
ok('keine Wiederaufbauebene im Plan', await js("!!document.getElementById('ov-ebene')"), false);

/* ── Anfangszustand ── */
ok('ein Zeitknopf', await js("document.querySelectorAll('#ebenen .eb-zeit').length"), 1);
ok('Heute zu sehen', await js("document.getElementById('ov-heute').getAttribute('opacity')"), '1.00');
ok('1940 nicht zu sehen', await js("document.getElementById('ov-1940').getAttribute('opacity')"), '0.00');
ok('1940 noch nicht geladen', req.filter(u=>/plan-1940-ebene/.test(u)).length, 0);
ok('Quellenzeile still', await js("document.getElementById('eb-quelle').hidden"), true);
/* Der Knopf nennt den naechsten Stand, nicht den jetzigen. */
ok('Knopf zeigt nach 1940', await js("document.getElementById('eb-zeit').textContent"),
   t=>typeof t==='string' && t.startsWith('\u2192') && /1940/.test(t));
await knipse('Q1_heute.png');

/* ── Umschlagen, und zwar mit einem echten Klick ── */
await js("document.getElementById('eb-zeit').click()"); await sleep(2500);
ok('1940 zu sehen', await js("document.getElementById('ov-1940').getAttribute('opacity')"), '1.00');
ok('Heute nicht zu sehen', await js("document.getElementById('ov-heute').getAttribute('opacity')"), '0.00');
ok('1940 jetzt geladen', req.filter(u=>/plan-1940-ebene/.test(u)).length, n=>n>=1);
ok('Quellenzeile da', await js("document.getElementById('eb-quelle').hidden"), false);
ok('Quellenzeile nennt das Stadsarchief', await js("document.getElementById('eb-quelle').textContent"),
   t=>typeof t==='string' && /Stadsarchief/.test(t));
ok('Knopf zeigt zurueck nach heute', await js("document.getElementById('eb-zeit').textContent"),
   t=>typeof t==='string' && t.startsWith('\u2192') && !/1940/.test(t));
await knipse('Q2_1940.png');

/* ── Und zurueck ── */
await js("document.getElementById('eb-zeit').click()"); await sleep(900);
ok('wieder heute', await js("document.getElementById('ov-heute').getAttribute('opacity')"), '1.00');
ok('1940 wieder weg', await js("document.getElementById('ov-1940').getAttribute('opacity')"), '0.00');
ok('Quellenzeile wieder still', await js("document.getElementById('eb-quelle').hidden"), true);
/* Zweimal geladen waere ein Fehler: das Bild haengt am href und bleibt. */
ok('kein zweiter Abruf von 1940', req.filter(u=>/plan-1940-ebene/.test(u)).length, 1);

/* ── dreisprachig, in beiden Staenden ── */
for (const [l,heute,alt] of [['nl','Vandaag','Stad 1940'],['en','Today','City 1940']]){
  await js(`setLang('${l}')`); await sleep(500);
  ok(`${l}: Knopf zeigt nach 1940`, await js("document.getElementById('eb-zeit').textContent"), '\u2192 '+alt);
  await js("document.getElementById('eb-zeit').click()"); await sleep(600);
  ok(`${l}: Knopf zeigt nach heute`, await js("document.getElementById('eb-zeit').textContent"), '\u2192 '+heute);
  ok(`${l}: Quellenzeile mitgewandert`, await js("document.getElementById('eb-quelle').textContent"),
     t=>typeof t==='string' && t.length>40);
  await js("document.getElementById('eb-zeit').click()"); await sleep(500);
}
await js("setLang('de')"); await sleep(400);
ok('Name fuer Hilfsmittel', await js("document.getElementById('eb-zeit').getAttribute('aria-label')"),
   t=>typeof t==='string' && t.length>8);

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
const leer = await ruhe(8);
P.push(`     Leerlauf, heute:  Skript ${(leer.skript*1000).toFixed(1)} ms/s, Layout ${(leer.layout*1000).toFixed(1)}, Stil ${(leer.stil*1000).toFixed(1)}, gesamt ${(leer.gesamt*100).toFixed(2)} % einer CPU`);
await js("document.getElementById('eb-zeit').click()"); await sleep(1200);
const alt = await ruhe(8);
P.push(`     Leerlauf, 1940:   Skript ${(alt.skript*1000).toFixed(1)} ms/s, Layout ${(alt.layout*1000).toFixed(1)}, Stil ${(alt.stil*1000).toFixed(1)}, gesamt ${(alt.gesamt*100).toFixed(2)} % einer CPU`);
ok('Leerlauf kostet fast nichts', Math.max(leer.gesamt, alt.gesamt), v=>v < 0.02);
ok('kein Dauerlaeufer im Skript', Math.max(leer.skript, alt.skript), v=>v < 0.01);

ok('keine Konsolenfehler', errs, a=>a.length===0);
console.log(P.join('\n'));
if (errs.length) console.log('Fehler:', errs.slice(0,4));
ws.close(); chrome.kill(); process.exit(P.some(z=>z.startsWith('FEHL'))?1:0);
