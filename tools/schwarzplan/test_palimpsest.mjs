/* Der dritte Knopf: beide Karten uebereinander, die alte mit 70
   Prozent. Geprueft wird der Zustand der Schichten, das Verhaeltnis
   zum Zeitknopf und die Beschriftung in allen drei Sprachen. */
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';
const ZIEL = process.argv[2] || 'http://127.0.0.1:8099/index.html';
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe', PORT=9151;
const chrome=spawn(CHROME,['--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',`--user-data-dir=C:/Temp/wij3d/chrome-pa-${Date.now()}`,`--remote-debugging-port=${PORT}`,'about:blank'],{stdio:'ignore'});
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
await cmd('Page.enable'); await cmd('Runtime.enable'); await cmd('Log.enable'); await cmd('Network.enable');
await cmd('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:2,mobile:true});
await cmd('Page.navigate',{url:ZIEL+'?p='+Date.now()}); await sleep(9000);
const P=[]; const ok=(n,v,e)=>P.push(`${(typeof e==='function'?e(v):JSON.stringify(v)===JSON.stringify(e))?'ok   ':'FEHL '} ${n}: ${JSON.stringify(v)}`);
await js('window.scrollTo(0, Math.round(getIntroH()*0.95))'); await sleep(2000);

ok('Knopf da', await js("!!document.getElementById('eb-palimpsest')"), true);
ok('zuerst aus', await js("document.getElementById('eb-palimpsest').getAttribute('aria-pressed')"), 'false');
ok('Fuellungen noch nicht geladen', req.filter(u=>/palimpsest\.webp/.test(u)).length, 0);

await js("document.getElementById('eb-palimpsest').click()"); await sleep(3000);
ok('gedrueckt', await js("document.getElementById('eb-palimpsest').getAttribute('aria-pressed')"), 'true');
ok('heute bleibt voll', await js("document.getElementById('ov-heute').getAttribute('opacity')"), '1.00');
ok('Fuellungen bei 70 Prozent', await js("document.getElementById('ov-palimpsest').getAttribute('opacity')"), '0.70');
ok('alte Vollkarte bleibt aus', await js("document.getElementById('ov-1940').getAttribute('opacity')"), '0.00');
ok('Fuellungen jetzt geladen', req.filter(u=>/palimpsest\.webp/.test(u)).length, n=>n>=1);
/* Die Fuellungen liegen ueber dem heutigen Plan und unter der Route. */
ok('Reihenfolge im Stapel', await js(`(function(){
  var n=[...document.getElementById('mapSvg').children].map(function(c){return c.id||c.tagName});
  return [n.indexOf('ov-heute'), n.indexOf('ov-palimpsest'), n.indexOf('routeTrail')];})()`),
   v=>Array.isArray(v) && v[0] < v[1] && v[1] < v[2]);
ok('Quellenzeile da', await js("document.getElementById('eb-quelle').hidden"), false);
ok('Quellenzeile nennt den Palimpsest', await js("document.getElementById('eb-quelle').textContent"),
   t=>typeof t==='string' && /Palimpsest/.test(t));
await knipse('P1_palimpsest.png');

/* Der Zeitknopf verlaesst den Palimpsest. */
await js("document.getElementById('eb-zeit').click()"); await sleep(1200);
ok('Zeitknopf loest den Palimpsest', await js("document.getElementById('eb-palimpsest').getAttribute('aria-pressed')"), 'false');
ok('danach genau ein Stand', await js("[document.getElementById('ov-heute').getAttribute('opacity'),document.getElementById('ov-1940').getAttribute('opacity')]"),
   v=>Array.isArray(v) && v.filter(o=>o==='1.00').length===1 && v.filter(o=>o==='0.00').length===1);

/* Wieder an, dann wieder aus. */
await js("document.getElementById('eb-palimpsest').click()"); await sleep(900);
ok('wieder an', await js("document.getElementById('ov-palimpsest').getAttribute('opacity')"), '0.70');
await js("document.getElementById('eb-palimpsest').click()"); await sleep(900);
ok('wieder aus', await js("document.getElementById('eb-palimpsest').getAttribute('aria-pressed')"), 'false');
ok('aus: Fuellungen weg', await js("document.getElementById('ov-palimpsest').getAttribute('opacity')"), '0.00');

/* dreisprachig */
for (const [l,w] of [['de','Palimpsest'],['nl','Palimpsest'],['en','Palimpsest']]){
  await js(`setLang('${l}')`); await sleep(500);
  ok(`${l}: Beschriftung`, await js("document.getElementById('eb-palimpsest').textContent"), w);
  ok(`${l}: Name fuer Hilfsmittel`, await js("document.getElementById('eb-palimpsest').getAttribute('aria-label')"),
     t=>typeof t==='string' && t.length>10);
}
await js("setLang('de')"); await sleep(400);
await js("document.getElementById('eb-palimpsest').click()"); await sleep(900);
ok('Knoepfe bleiben an ihrem Platz', await js(`(function(){
  return ['eb-historie','eb-kapitel','eb-zeit','eb-palimpsest'].map(function(i){
    var r=document.getElementById(i).getBoundingClientRect();
    return [Math.round(r.left), Math.round(r.top)];});})()`),
  v=>Array.isArray(v) && v.length===4);
await knipse('P2_palimpsest_de.png');

ok('keine Konsolenfehler', errs, a=>a.length===0);
console.log(P.join('\n'));
if (errs.length) console.log('Fehler:', errs.slice(0,4));
ws.close(); chrome.kill(); process.exit(P.some(z=>z.startsWith('FEHL'))?1:0);
