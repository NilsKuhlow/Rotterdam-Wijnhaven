/* Die Zitate wurden am 2026-10-26 sprachlich neu gefasst (ganze Saetze
   statt Notizfragmente, keine woertlich uebersetzten Wendungen mehr).
   Die Pruefungen hier haengen an einer Wendung des jeweiligen Zitats und
   sind deshalb mitgezogen worden; die Aussagen selbst sind dieselben. */
/* Stimmen: Abschnitt, Sprechblasen im Modell, Zitatfeld, Sprachwechsel. */
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';
const CHROME='C:/Program Files/Google/Chrome/Application/chrome.exe', PORT=9177;
const chrome=spawn(CHROME,['--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run','--user-data-dir=C:/Temp/wij3d/chrome-stimmen',`--remote-debugging-port=${PORT}`,'about:blank'],{stdio:'ignore'});
let u; for(let i=0;i<60;i++){try{const l=await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();const p=l.find(t=>t.type==='page');if(p){u=p.webSocketDebuggerUrl;break}}catch{} await sleep(500);}
const ws=new WebSocket(u); await new Promise(r=>ws.addEventListener('open',r,{once:true}));
let id=0; const off=new Map(); const errs=[];
ws.addEventListener('message',e=>{const m=JSON.parse(e.data); if(m.id&&off.has(m.id)){off.get(m.id)(m);off.delete(m.id)} if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errs.push(m.params.entry.text); if(m.method==='Runtime.exceptionThrown')errs.push(m.params.exceptionDetails.text);});
const cmd=(m,p={})=>new Promise(r=>{const i=++id;off.set(i,r);ws.send(JSON.stringify({id:i,method:m,params:p}))});
const js=async e=>(await cmd('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true})).result?.result?.value;
const bild=async n=>{const s=await cmd('Page.captureScreenshot',{format:'png'});writeFileSync('C:/Temp/wij3d/pres/'+n,Buffer.from(s.result.data,'base64'));};
await cmd('Page.enable'); await cmd('Runtime.enable'); await cmd('Log.enable');
await cmd('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:2,mobile:true});
await cmd('Page.navigate',{url:'http://127.0.0.1:8099/index.html'}); await sleep(6000);
const P=[];const ok=(n,v,e)=>P.push(`${(typeof e==='function'?e(v):v===e)?'ok   ':'FEHL '} ${n}: ${JSON.stringify(v)}`);

ok('Abschnitt da', await js("!!document.getElementById('stimmen')"), true);
ok('fuenf Stimmen', await js("document.querySelectorAll('#stimmen .st-item').length"), 5);
ok('Ueberschrift DE', await js("document.querySelector('.st-title').textContent"), 'Stimmen aus dem Viertel');
ok('Lead gefuellt', await js("document.querySelector('.st-lead').textContent.length"), n=>n>80);
ok('Hinweis gefuellt', await js("document.querySelector('.st-note').textContent.length"), n=>n>150);
ok('Anker je Stimme', await js("[...document.querySelectorAll('#stimmen .st-item')].every(function(f){return /^stimme-/.test(f.id)})"), true);
ok('erstes Zitat DE', await js("document.querySelector('#stimme-shyvanna blockquote').textContent"), s=>/weniger gewohnt als gearbeitet/.test(String(s)));

await js("setLang('en')"); await sleep(400);
ok('Ueberschrift EN', await js("document.querySelector('.st-title').textContent"), 'Voices from the quarter');
ok('erstes Zitat EN', await js("document.querySelector('#stimme-shyvanna blockquote').textContent"), s=>/less living than working/.test(String(s)));
await js("setLang('nl')"); await sleep(400);
ok('Ueberschrift NL', await js("document.querySelector('.st-title').textContent"), 'Stemmen uit de wijk');
await js("setLang('de')"); await sleep(400);

/* 3D: Blasen und Zitat */
await js('openTour3D()');
for(let i=0;i<150;i++){ if(await js("document.querySelectorAll('.t3d-pin').length")) break; await sleep(1000); }
ok('Bauwerksmarker', await js("document.querySelectorAll('.t3d-pin').length"), 7);
ok('Sprechblasen', await js("document.querySelectorAll('.t3d-blase').length"), 5);
ok('Blase kleiner als Marker', await js("(function(){var b=document.querySelector('.t3d-blase').getBoundingClientRect(),p=document.querySelector('.t3d-pin').getBoundingClientRect();return Math.round(b.width)+'<'+Math.round(p.width)})()"), s=>{const[a,c]=String(s).split('<').map(Number);return a<c;});
ok('Zitat zuerst verborgen', await js("document.getElementById('t3d-zitat').hidden"), true);
await js("document.querySelector('.t3d-blase[data-stimme=\"sirano\"]').click()"); await sleep(500);
ok('Zitat offen', await js("!document.getElementById('t3d-zitat').hidden"), true);
ok('Zitattext', await js("document.querySelector('.t3z-text').textContent"), s=>/nehmen einem die Identität/.test(String(s)));
ok('Name', await js("document.querySelector('.t3z-who').textContent"), 'Sirano');
ok('Kontext', await js("document.querySelector('.t3z-ctx').textContent"), 'erstes Studienjahr');
ok('Blase markiert', await js("document.querySelectorAll('.t3d-blase.offen').length"), 1);
await bild('30_blasen.png');
/* Sprachwechsel bei offenem Zitat */
await js("setLang('en')"); await sleep(450);
ok('Zitat wechselt mit', await js("document.querySelector('.t3z-text').textContent"), s=>/take your identity away/.test(String(s)));
await js("setLang('de')"); await sleep(400);
await js('schliesseStimme()'); await sleep(300);
ok('Zitat schliesst', await js("document.getElementById('t3d-zitat').hidden"), true);
ok('Markierung weg', await js("document.querySelectorAll('.t3d-blase.offen').length"), 0);
console.log(P.join('\n'));
console.log('Konsolenfehler:', errs.length?errs.slice(0,5):'keine');
ws.close(); chrome.kill(); process.exit(0);
