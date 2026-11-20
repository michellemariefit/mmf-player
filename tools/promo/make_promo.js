// Renders promo images of the diet plan app into promo/.
// Serve the repo first:  python3 -m http.server 8787 --bind 127.0.0.1   then:  node tools/promo/make_promo.js
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const BASE='http://127.0.0.1:8787';const OUT=path.join(__dirname,'..','..','promo');fs.mkdirSync(OUT,{recursive:true});
const SIZES={hero:[1600,1000],before:[1600,1000]};
const CARDS=['hero','today','cook','shop','aversion','week','before','included'];
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1600,height:1200},deviceScaleFactor:2});
  // every frame of the app starts in the same, good-looking state: week 1 Friday is today, breakfast eaten, water half done
  await ctx.addInitScript(()=>{try{
    if(!location.pathname.includes('/diet/'))return;
    const d=new Date();d.setHours(0,0,0,0);const iso=x=>x.getFullYear()+'-'+String(x.getMonth()+1).padStart(2,'0')+'-'+String(x.getDate()).padStart(2,'0');
    const todayKey=iso(d);const s=new Date(d);s.setDate(s.getDate()-5);// week 1, Fri
    const tab={today:'today',week:'week',recipe:'today',recipes:'recipes',shop:'shopping'}[new URLSearchParams(location.search).get('tab')||window.name]||'today';
    localStorage.clear();localStorage.setItem('pdp:start',JSON.stringify(iso(s)));localStorage.setItem('pdp:tab',JSON.stringify(tab));
    localStorage.setItem('pdp:done:'+todayKey,JSON.stringify({b:true,s1:true}));localStorage.setItem('pdp:water:'+todayKey,'4');
    localStorage.setItem('pdp:snack:'+todayKey+':1',JSON.stringify('Blueberry Chip Cookies'));
    const ate=new Date();ate.setMinutes(ate.getMinutes()-70);localStorage.setItem('pdp:ate',String(ate.getTime()));
    localStorage.setItem('pdp:av',JSON.stringify({fish:true}));localStorage.setItem('pdp:shopweek','1');
    localStorage.setItem('pdp:have:week1',JSON.stringify({'Eggs':true,'Goat Cheese':true,'Paprika':true}));
    localStorage.setItem('pdp:fav',JSON.stringify({5:true,'s:Blueberry Chip Cookies':true}));
  }catch(e){}});
  for(const card of CARDS){
    const [w,h]=SIZES[card]||[1200,1200];
    const p=await ctx.newPage();await p.setViewportSize({width:w,height:h});
    await p.goto(`${BASE}/tools/promo/card.html?card=${card}`,{waitUntil:'networkidle'});
    await p.waitForTimeout(600);
    for(const f of p.frames()){
      if(f===p.mainFrame())continue;
      try{await f.waitForSelector('.tabs button',{timeout:8000})}catch(e){continue}
      if(f.name()==='recipe'){await f.click('[data-open="5"]');await f.waitForSelector('.comp');await f.click('[data-scale="2"]');await f.waitForTimeout(150)}
      if(f.name()==='recipes'){await f.click('[data-filter="fish"]');await f.waitForTimeout(150)}
      if(f.name()==='today'){await f.evaluate(()=>window.scrollTo(0,0))}
    }
    await p.evaluate(()=>{window.scrollTo(0,0);document.querySelectorAll('*').forEach(e=>{e.scrollLeft=0;e.scrollTop=0})});await p.waitForTimeout(500);
    await p.screenshot({path:path.join(OUT,`${card}.png`),clip:{x:0,y:0,width:w,height:h}});
    console.log('wrote',card);await p.close();
  }
  // plain phone screenshots too, for Canva
  const m=await ctx.newPage();await m.setViewportSize({width:390,height:844});
  for(const [name,act] of [['today',null],['week',null],['recipes',null],['shop',null],['recipe',async f=>{await f.click('[data-open="5"]');await f.waitForSelector('.comp');await f.click('[data-scale="2"]')}]]){
    await m.goto(`${BASE}/diet/index.html?tab=${name}`,{waitUntil:'networkidle'});await m.waitForSelector('.tabs button');
    if(act)await act(m);await m.waitForTimeout(300);
    await m.screenshot({path:path.join(OUT,`screen-${name}.png`)});
  }
  await b.close();console.log('done');
})();
