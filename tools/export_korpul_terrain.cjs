// Build complete PNGs from painted masters and record exact provenance.
// Browser review is static, never a game launch. Run from addon root:
// node tools/export_korpul_terrain.cjs [--review]
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..'),art=path.join(root,'art/terrain-korpul-v1'),out=path.join(root,'data/gfx/refined/korpul'),rev=path.join(art,'review/runtime');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const materials=['floor-a','floor-b','wall','hardwall','door-closed-horizontal','door-closed-vertical','door-open-horizontal','door-open-vertical'];
fs.mkdirSync(out,{recursive:true});fs.mkdirSync(rev,{recursive:true});
const binary=path.join('/tmp',`export-korpul-${process.pid}`);
try{cp.execFileSync('cc',['-O2',path.join(__dirname,'export_korpul_terrain.c'),'-o',binary,'-lpng','-lm']);cp.execFileSync(binary,[path.join(art,'masters'),out,rev],{stdio:'inherit'});}finally{if(fs.existsSync(binary))fs.unlinkSync(binary);}
const sources=['floor-a-v2','floor-b-v2','wall-top-v1','hardwall-top-v1','wall-v1','hardwall-v1','door-leaf-horizontal-v1','door-leaf-vertical-v2'].map(id=>({id,path:`masters/${id}.png`,sha256:hash(path.join(art,'masters',id+'.png')),prompt:`prompts/${id}.json`}));
const files=[];
for(const material of materials)for(let mask=0;mask<(material.startsWith('floor')?1:16);mask++)for(let parity=0;parity<2;parity++){
 const name=`${material}-${mask}-${parity}.png`,p=path.join(out,name),buf=fs.readFileSync(p);
 if(buf.readUInt32BE(16)!==128||buf.readUInt32BE(20)!==128||buf[25]!==6)throw Error('PNG format mismatch '+name);
 files.push({material,mask,parity,path:`checker-revised+refined/korpul/${name}`,file:`data/gfx/refined/korpul/${name}`,sha256:hash(p),bytes:buf.length,width:128,height:128});
}
const actual=fs.readdirSync(out).filter(n=>n.endsWith('.png')).sort(),expected=files.map(x=>path.basename(x.file)).sort();
if(JSON.stringify(actual)!==JSON.stringify(expected)||files.length!==196)throw Error('Contract output set mismatch');
const manifest={version:1,generator:'tools/export_korpul_terrain.c',generator_sha256:hash(path.join(__dirname,'export_korpul_terrain.c')),source_mode:'built-in ImageGen; deterministic C masks, crops, alpha-over, area downsampling, parity; no rotation',runtime_ready_requires_parent_live_validation:true,static_review:'review/runtime',count:files.length,geometry:{canvas:128,wall_footprint:[0,0,128,128],outer_edge_widths:{N:2,E:5,S:9,W:2},connected_edges:'no outer side strip; continuous painted top reaches boundary',door_horizontal_jambs:[[0,84,20,124],[108,84,128,124]],door_vertical_jambs:[[4,0,44,20],[4,108,44,128]],door_closed_horizontal_leaf:[19,96,109,116],door_open_horizontal_leaf:[16,16,34,104],door_closed_vertical_leaf:[16,19,34,109],door_open_vertical_leaf:[24,100,112,120],parity_multipliers:[1,0.90],door_axis_only_connections:'horizontal E/W; vertical N/S; perpendicular bits do not add a barrier'},sources,files};
manifest.orchestrator='tools/export_korpul_terrain.cjs';
manifest.orchestrator_sha256=hash(__filename);
fs.writeFileSync(path.join(art,'runtime-manifest.json'),JSON.stringify(manifest,null,2)+'\n');

const style=`<style>body{margin:20px;background:#252a26;color:#e6e3d9;font:14px system-ui}h1{font-size:23px}h2{font-size:16px;margin:5px 0 9px}main{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}article{padding:10px;border:1px solid #646a61}.samples{display:flex;gap:7px;align-items:flex-start}.map{display:grid;gap:0;flex:none}.map img{display:block;margin:0}.grey{filter:grayscale(1)}.row{display:flex;gap:15px;align-items:center;margin:10px 0}p{line-height:1.4}</style>`;
const img=(name,size)=>`<img src="${size}/${name}.png" width="${size}" height="${size}">`;
function mapHtml(grid,size,shift=0,centerKind=null,centerMask=0){
 const h=grid.length,w=grid[0].length;let s=`<div class="map" style="grid-template-columns:repeat(${w},${size}px)">`;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const k=grid[y][x];let mask=0;
  for(const [dx,dy,bit] of [[0,-1,1],[1,0,2],[0,1,4],[-1,0,8]])if(['wall','hardwall'].includes(grid[y+dy]?.[x+dx]))mask|=bit;
  const material=k||((x+y)%3?'floor-a':'floor-b');if(material.startsWith('floor'))mask=0;
  if(centerKind&&x===1&&y===1)mask=centerMask;
  s+=img(`${material}-${mask}-${(x+y+shift)%2}`,size);
 }return s+'</div>';
}
const jobs=[];
for(const kind of materials.slice(2)){
 let h=`<!doctype html><meta charset="utf-8">${style}<h1>${kind} — all 16 masks / both parity phases</h1><p>Actual 48px exports. Each card: parity phase 0 then 1. Mixed ordinary/hard wall neighbours. Centre is the named material; no diagonal geometry is inferred. Static browser review, not runtime.</p><main>`;
 for(let m=0;m<16;m++){
  const g=Array.from({length:3},()=>Array(3).fill(null));g[1][1]=kind;
  if(m&1)g[0][1]='wall';if(m&2)g[1][2]='hardwall';if(m&4)g[2][1]='wall';if(m&8)g[1][0]='hardwall';
  h+=`<article><h2>mask ${m}</h2><div class="samples">${mapHtml(g,48,0,kind,m)}${mapHtml(g,48,1,kind,m)}</div></article>`;
 }h+='</main>';const name=kind+'-masks';fs.writeFileSync(path.join(rev,name+'.html'),h);jobs.push({file:path.join(rev,name+'.png'),url:'file://'+path.join(rev,name+'.html'),count:16});
}
let s=`<!doctype html><meta charset="utf-8">${style}<h1>Kor’Pul — full-cell production review</h1><p>Actual 48 / 64 / 96px. Complete floor-under-object exports, fixed door anchors and world light. Grayscale is CSS only. No game render or actor-state test claimed.</p><main>`;
for(const kind of materials){s+=`<article><h2>${kind}</h2><div class="samples">`;for(const n of [48,64,96])s+=img(`${kind}-0-0`,n);s+='</div><div class="samples grey">';for(const n of [48,64,96])s+=img(`${kind}-0-1`,n);s+='</div></article>';}s+='</main>';
const W='wall',H='hardwall',F=null;
const scenarios=[
 ['4 x 4 solid ordinary wall — no interior floor gutters',Array.from({length:4},()=>Array(4).fill(W))],
 ['Straight / corner / T / cross / mixed',[[W,W,W,H,H],[W,F,W,F,H],[W,W,W,H,H],[F,F,W,F,H],[H,H,H,H,H]]],
 ['East-west one-cell corridor / vertical door axis',[[W,W,W,H,H],[F,'door-closed-vertical',F,'door-open-vertical',F],[W,W,W,H,H]]],
 ['North-south one-cell corridors / horizontal door axis',[[W,F,W,F,H],[W,'door-closed-horizontal',W,'door-open-horizontal',H],[W,F,W,F,H]]],
 ['Diagonal contact remains square / no inferred corner cutout',[[W,F,H,F],[F,W,F,H],[H,F,W,F],[F,H,F,W]]]
];
for(const [title,g] of scenarios){s+=`<h2>${title}</h2><div class="row">${mapHtml(g,48)}${mapHtml(g,64)}${mapHtml(g,96)}</div>`;}
fs.writeFileSync(path.join(rev,'production-sheet.html'),s);jobs.push({file:path.join(rev,'production-sheet.png'),url:'file://'+path.join(rev,'production-sheet.html'),count:8});
const config={browser:'~/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell',playwright:'~/.npm/_npx/e41f203b7505f1fb/node_modules/playwright-core',jobs,report:path.join(rev,'capture-report.json')};
fs.writeFileSync(path.join(rev,'capture-config.json'),JSON.stringify(config,null,2)+'\n');
if(process.argv.includes('--review'))cp.execFileSync('node',[path.join(__dirname,'capture_monster_review.cjs')],{input:JSON.stringify(config),stdio:['pipe','inherit','inherit'],env:{...process.env,LD_LIBRARY_PATH:'~/.cache/sgstory-chrome-deps/usr/lib/x86_64-linux-gnu'+(process.env.LD_LIBRARY_PATH?':'+process.env.LD_LIBRARY_PATH:'')}});
console.log('Manifest:',path.join(art,'runtime-manifest.json'));
