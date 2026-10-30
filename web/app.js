let token='', pending=null;
const $=id=>document.getElementById(id);
async function api(path,data){const opts=data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Missy-Token':token},body:JSON.stringify(data)};const r=await fetch(path,opts);const j=await r.json();if(!r.ok)throw Error(j.error||r.status);return j;}
function showError(id,e){$(id).textContent='Not completed: '+e.message;$(id).className='error';}
async function refresh(){try{const r=await api('/api/status');const s=r.summary;$('recorded').textContent=s.recorded_ml;$('remaining').textContent=s.above_record_target_ml?`Above synthetic record target by ${s.above_record_target_ml} mL (not a diagnosis).`:`Remaining to synthetic recording target: ${s.remaining_record_target_ml} mL (demo only).`;$('bar').style.width=Math.min(100,100*s.recorded_ml/s.target_ml)+'%';renderReminders(r.reminders);}catch(e){showError('remaining',e);}}
function renderReminders(items){const box=$('reminder-list');box.replaceChildren();for(const item of items){const p=document.createElement('p');const due=new Date(item.due_at);p.textContent=(item.acknowledged?'✓ ':'⏰ ')+item.title+' · '+due.toLocaleTimeString();if(!item.acknowledged&&due<=new Date()){p.className='good';p.textContent='🔔 Reminder: '+item.title+' (local browser notification)';const btn=document.createElement('button');btn.className='secondary';btn.textContent='Acknowledge';btn.onclick=async()=>{try{await api('/api/ack',{id:item.id});await refresh();}catch(e){showError('reminder-list',e);}};p.append(' ',btn);}box.appendChild(p);}}
$('network').textContent=navigator.onLine?'Device reports online':'Device reports offline';window.addEventListener('offline',()=>{$('network').textContent='Device reports offline';});window.addEventListener('online',()=>{$('network').textContent='Device reports online';});
$('parse').onclick=async()=>{pending=null;$('pending').hidden=true;$('parse-result').textContent='Loading local QVAC model and interpreting…';$('parse-result').className='';try{const r=await api('/api/parse',{text:$('phrase').value});pending=r.pending;$('parse-result').textContent=`Local QVAC ${r.proof.model} · ${r.proof.latency_ms} ms · confirmation required`;$('parse-result').className='good';$('pending-text').textContent=`Confirm recording ${pending.volume_ml} mL? Original: ${pending.source}`;$('pending').hidden=false;}catch(e){showError('parse-result',e);}};
$('confirm').onclick=async()=>{if(!pending)return;try{await api('/api/confirm',pending);pending=null;$('pending').hidden=true;$('parse-result').textContent='Saved locally after your confirmation.';await refresh();}catch(e){showError('parse-result',e);}};
$('cancel').onclick=()=>{pending=null;$('pending').hidden=true;};
$('food-btn').onclick=async()=>{try{const r=await api('/api/food',{name:$('food').value});$('food-result').textContent=(r.food?r.food+' — ':'')+r.message+' Source: '+(r.source||'No verified entry');}catch(e){showError('food-result',e);}};
$('remind').onclick=async()=>{try{await api('/api/reminder',{title:'Review your saved care checklist',due_at:new Date(Date.now()+120000).toISOString()});await refresh();}catch(e){showError('reminder-list',e);}};
let timelineOffset=0, timelineBusy=false;
async function loadTimeline(reset=false){
  if(timelineBusy)return;
  timelineBusy=true;
  $('timeline-load').disabled=true;
  $('timeline-more').disabled=true;
  try{
    const offset=reset?0:timelineOffset;
    const r=await api('/api/timeline',{limit:10,offset});
    if(r.synthetic!==true||r.schema_version!=='ai-missy.synthetic-timeline.v1')throw Error('Timeline schema not verified');
    if(reset)$('timeline-list').replaceChildren();
    for(const event of r.events){
      const p=document.createElement('p');
      p.textContent=new Date(event.confirmed_at).toLocaleString()+' · '+event.volume_ml+' mL confirmed (synthetic)';
      $('timeline-list').appendChild(p);
    }
    timelineOffset=offset+r.events.length;
    $('timeline-more').hidden=!r.page.has_more;
    $('timeline-result').textContent=r.page.total===0?'No confirmed synthetic events yet.':'Showing '+timelineOffset+' of '+r.page.total+' confirmed synthetic records.';
  }catch(e){showError('timeline-result',e);}
  finally{timelineBusy=false;$('timeline-load').disabled=false;$('timeline-more').disabled=false;}
}
$('timeline-load').onclick=()=>loadTimeline(true);
$('timeline-more').onclick=()=>loadTimeline(false);
$('export').onclick=async()=>{try{const record=await api('/api/export',{});if(record.synthetic!==true||record.schema_version!=='ai-missy.synthetic-care.v1')throw Error('Export schema not verified');const blob=new Blob([JSON.stringify(record,null,2)+'\n'],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='ai-missy-synthetic-care.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);$('export-result').textContent='Synthetic care record downloaded locally. No server upload.';}catch(e){showError('export-result',e);}};
(async()=>{try{token=(await api('/api/session')).token;await refresh();setInterval(refresh,4000);}catch(e){showError('remaining',e);}})();
