import {validate, frameAt, project} from './material-viewer-model.mjs';
const $ = id => document.getElementById(id);
const canvas = $('scene'), ctx = canvas.getContext('2d');
let data, extent = 1, index = 0, selected = 0, yaw = .65, pitch = -.45, zoom = 1, playing = false, start = 0, origin = 0;
function stop(){playing=false;$('play').textContent='Play';}
function install(raw, label){
  const next = validate(raw); stop(); data=next; index=0; selected=0;
  extent=0;for(const f of data.frames)for(const m of f.modules)for(const b of m.bodies)for(const v of b.vertices_m)extent=Math.max(extent,Math.hypot(...v));
  $('module').replaceChildren(...data.frames[0].modules.map((m,i)=>new Option(m.id,String(i))));
  for(const id of ['play','module','frame']) $(id).disabled=false;
  $('frame').max=String(data.frames.length-1);$('frame').value='0';$('error').textContent='';
  $('provenance').textContent=`Loaded: ${label}\nCase: ${data.case}\nFrames: ${data.frame_count}\nLength: metres\nTime: seconds\nAngles: radians\nEnergy: joules\nExport display scale: ${data.units.display_m_per_unit} m/unit\n\nSource: ${data.source_report?.path ?? 'not supplied'}\nSHA-256 (reported, not independently verified):\n${data.source_report?.sha256_normalized_text ?? 'not supplied'}\n\n${data.coordinate_policy ?? 'Module local frames'}`;
  render();
}
function error(e){stop();$('error').textContent=e.message;}
$('example').onclick=async()=>{try{const r=await fetch('./material-viewer-example.json');if(!r.ok)throw Error('Example could not be loaded.');install(await r.json(),'computed example');}catch(e){error(e);}};
$('file').onchange=async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>25e6)throw Error('Please use an export smaller than 25 MB.');install(JSON.parse(await f.text()),f.name);}catch(e){error(e);}};
$('module').onchange=()=>{selected=Number($('module').value);render();};
$('frame').oninput=()=>{stop();index=Number($('frame').value);render();};
$('speed').onchange=stop;
$('play').onclick=()=>{if(playing){stop();return;}if(index===data.frames.length-1)index=0;origin=data.frames[index].time_s;start=performance.now();playing=true;$('play').textContent='Pause';};
$('reset').onclick=()=>{yaw=.65;pitch=-.45;zoom=1;render();};
let drag;
canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);};
canvas.onpointermove=e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.01;pitch+=(e.clientY-drag[1])*.01;drag=[e.clientX,e.clientY];render();};
canvas.onpointerup=canvas.onpointercancel=()=>{drag=null;};
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.3,Math.min(5,zoom*Math.exp(-e.deltaY*.001)));render();},{passive:false});
function render(){
  const w=canvas.clientWidth,h=canvas.clientHeight,dpr=devicePixelRatio||1;
  canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.scale(dpr,dpr);ctx.clearRect(0,0,w,h);
  if(!data){ctx.fillStyle='#aabbd0';ctx.font='16px system-ui';ctx.fillText('Load a computed export to inspect the geometry.',24,45);return;}
  const frame=data.frames[index],m=frame.modules[selected];
  // One fixed scale across all modules and frames preserves relative physical size.
  const scale=.38*Math.min(w,h)/Math.max(extent,1e-12)*zoom;
  const shapes=m.bodies.map(b=>({b,pts:b.vertices_m.map(v=>project(v,yaw,pitch))}));
  shapes.sort((a,b)=>a.pts.reduce((s,p)=>s+p[2],0)/a.pts.length-b.pts.reduce((s,p)=>s+p[2],0)/b.pts.length);
  for(const {pts} of shapes){ctx.beginPath();pts.forEach((p,i)=>{const x=w/2+p[0]*scale,y=h/2-p[1]*scale;i?ctx.lineTo(x,y):ctx.moveTo(x,y);});
    if(pts.length>2){ctx.closePath();ctx.fillStyle='#167a8c88';ctx.fill();ctx.strokeStyle='#72deec';ctx.lineWidth=1.5;ctx.stroke();}
    else if(pts.length===2){ctx.strokeStyle='#ffcc70';ctx.lineWidth=3;ctx.stroke();}
    else{ctx.arc(w/2+pts[0][0]*scale,h/2-pts[0][1]*scale,5,0,Math.PI*2);ctx.fillStyle='#ff8fb1';ctx.fill();}}
  ctx.fillStyle='#bdd0e4';ctx.font='13px system-ui';ctx.fillText(`${m.id} · 22 bodies · local frame`,16,25);
  $('frame').value=String(index);$('time').textContent=`t = ${frame.time_s.toFixed(4)} s · sample ${index+1}/${data.frame_count} · scale ${m.q[0].toFixed(5)} · angle ${m.q[1].toFixed(5)} rad`;
  const rows=[['Reserve',m.reserve_j],['Delivered work (transfer)',m.delivered_work_j],['External input',m.input_j],['Damping loss',m.losses_j.damping],['Conversion loss',m.losses_j.conversion],['Leakage loss',m.losses_j.leakage]];
  $('ledger').replaceChildren(...rows.map(([name,value])=>{const tr=document.createElement('tr');for(const t of [name,value.toExponential(6)+' J']){const td=document.createElement('td');td.textContent=t;tr.append(td);}return tr;}));
  $('edges').textContent=`All network edges (not selected-module totals)\nStored potential (J): ${JSON.stringify(frame.edge_potential_j)}\nEndpoint work (J): ${JSON.stringify(frame.edge_work_j)}`;
}
new ResizeObserver(render).observe(canvas);
function tick(now){if(playing){const t=origin+(now-start)/1000*Number($('speed').value);index=frameAt(data.frames,t);if(t>=data.frames.at(-1).time_s)stop();render();}requestAnimationFrame(tick);}requestAnimationFrame(tick);render();
