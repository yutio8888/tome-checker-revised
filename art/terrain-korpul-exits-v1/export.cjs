// Mechanical export only: generated artwork/native alpha remain unchanged.
const fs=require('node:fs'), path=require('node:path'), cp=require('node:child_process'), crypto=require('node:crypto');
const root=__dirname, addon=path.resolve(root,'../..');
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const bin='/tmp/korpul-stairs-export';
cp.execFileSync('cc',['-O2',path.join(addon,'tools/export_token.c'),'-o',bin,'-lpng','-lm']);
const ids=['stairs-up','stairs-down','stairs-world'],sizes=[48,64,96,128,256];
const report={method:'Built-in ImageGen native alpha; existing tools/export_token.c premultiplied-alpha area filter and centered 86% visible-bounds fit; no painting or recoloring',assets:[]};
for(const id of ids){
 const master=path.join(root,'masters',id+'-v1.png');
 const asset={id,master:path.relative(root,master),sha256:sha(master),exports:[]};
 for(const size of sizes){const dir=path.join(root,'sprites',String(size));fs.mkdirSync(dir,{recursive:true});const file=path.join(dir,id+'.png');const meta=JSON.parse(cp.execFileSync(bin,[master,file,String(size)],{encoding:'utf8'}));asset.exports.push({path:path.relative(root,file),...meta,sha256:sha(file)});}
 const runtime=path.join(addon,'data/gfx/refined/korpul',id+'.png');fs.copyFileSync(path.join(root,'sprites/256',id+'.png'),runtime);asset.runtime={path:path.relative(addon,runtime),engine_path:'checker-revised+refined/korpul/'+id+'.png',sha256:sha(runtime)};
 report.assets.push(asset);
}
fs.writeFileSync(path.join(root,'export-report.json'),JSON.stringify(report,null,2)+'\n');
const revision='korpul-exits-v1-'+crypto.createHash('sha256').update(report.assets.map(a=>a.runtime.sha256).join('\n')).digest('hex').slice(0,12);
fs.writeFileSync(path.join(root,'runtime-manifest.json'),JSON.stringify({ready:true,revision,files:report.assets.map(a=>a.runtime)},null,2)+'\n');
fs.writeFileSync(path.join(addon,'data/terrain-korpul-stairs-manifest.lua'),"-- Generated from art/terrain-korpul-exits-v1/runtime-manifest.json.\n-- Three transparent foreground sprites; existing Kor'Pul floors provide the base.\nreturn {\n ready=true,\n revision='"+revision+"',\n files={\n"+report.assets.map(a=>"  ['"+a.runtime.engine_path+"']=true,").join('\n')+"\n },\n}\n");
const refs=['art/terrain-korpul-v1/masters/floor-a-v2.png','art/terrain-korpul-v1/review/runtime/production-sheet.png'];fs.writeFileSync(path.join(root,'references/inspected.json'),JSON.stringify(refs.map(p=>({path:p,sha256:sha(path.join(addon,p)),role:'style/material reference; visually inspected before first generation'})),null,2)+'\n');
const floor='../../../data/gfx/refined/korpul/floor-a-0-0.png';
let html='<!doctype html><meta charset="utf-8"><title>Kor’Pul stairs — foreground review</title><style>body{background:#252a26;color:#ddd;font:16px system-ui;margin:24px}main{display:flex;gap:20px}article{border:1px solid #667;padding:16px;width:410px}h2{font-size:20px}.samples{display:flex;gap:14px;align-items:end;margin:16px 0}.cell{background-image:url('+floor+');background-size:100% 100%;display:block}.gray{filter:grayscale(1)}.label{font-size:12px;margin-bottom:5px}.transparent{background:#ddd;background-image:conic-gradient(#aaa 25%,transparent 0 50%,#aaa 0 75%,transparent 0);background-size:16px 16px}img{display:block}</style><h1>Kor’Pul — UP / DOWN / WORLD</h1><p>Actual 48 / 64 / 96 / 128px PNGs over existing floor; second row CSS grayscale. Browser composition only, not a game capture.</p><main>';
for(const id of ids){html+='<article><h2>'+id+'</h2>';for(const gray of [false,true])html+='<div class="samples '+(gray?'gray':'')+'">'+sizes.slice(0,4).map(s=>'<div><div class="label">'+s+'px</div><span class="cell"><img src="../sprites/'+s+'/'+id+'.png" width="'+s+'" height="'+s+'"></span></div>').join('')+'</div>';html+='<p>128px native alpha over checkerboard</p><span class="transparent" style="display:inline-block"><img src="../sprites/128/'+id+'.png" width="128" height="128"></span></article>';}
html+='</main>';fs.writeFileSync(path.join(root,'review/index.html'),html);
const previous=JSON.parse(fs.readFileSync(path.join(addon,'art/terrain-korpul-v1/review/runtime/capture-config.json')));const config={browser:previous.browser,playwright:previous.playwright,jobs:[{file:path.join(root,'review/production-sheet.png'),url:'file://'+path.join(root,'review/index.html'),count:3}],report:path.join(root,'review/capture-report.json')};fs.writeFileSync(path.join(root,'review/capture-config.json'),JSON.stringify(config,null,2)+'\n');
console.log(JSON.stringify({revision,assets:report.assets.length,exports:report.assets.reduce((n,a)=>n+a.exports.length,0)}));
