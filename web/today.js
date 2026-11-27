"use strict";
// Build19 intentionally has no fetch, localStorage, IndexedDB, or clinical write path.
const copy = {
 en: {language:"Language",welcome:"One small step today.",subtitle:"A gentle preview of a daily care journal, without diagnoses or clinical targets.",heading:"What would you like to note?",note:"Record only measurements recommended in your care plan. Nothing here is a clinical instruction.",insightHeading:"Your next step",insightEmpty:"Select a sample item to see a gentle reflection. No information is saved.",insightDone:"This sample check-in is selected. A real journal would require a verified observation, source, date, and your explicit confirmation.",safety:"AI Missy cannot set medicines, fluid limits, or clinical targets. Seek professional care when you need medical help.",reset:"Reset this preview",footer:"Synthetic demonstration · Memory only · No real patient data · No AI medical advice",back:"Back to offline water demo",counter:n=>n+" of 4 sample items selected (not medical records)",items:[["Blood pressure","Measure only if your individual plan calls for it."],["Blood glucose","The timing of a reading matters; no number is entered here."],["Daily movement","Reflect on activity appropriate to your health situation."],["Food habits","Notice a habit; no renal diet is prescribed."]]},
 zh: {language:"语言",welcome:"今天，照顾自己一点点。",subtitle:"温和的日常健康日记预览，不诊断疾病，也不设定医疗目标。",heading:"今天想记录什么？",note:"仅按照个人照护计划测量所需指标。此页面不提供医疗指示。",insightHeading:"你的下一步",insightEmpty:"选择一个示例项目，查看温和提示。不会保存任何资料。",insightDone:"已选择示例记录。真实日记仍需核实数值、来源、时间与用户明确确认。",safety:"AI Missy 不会设定药物、饮水限制或临床目标。如需医疗协助，请联系适当的专业人员。",reset:"重置演示",footer:"合成演示 · 仅暂存于页面内存 · 无真实患者资料 · 非 AI 医疗建议",back:"返回离线饮水演示",counter:n=>"已选择 "+n+" / 4 个示例项目（非医疗记录）",items:[["血压","仅在个人监测计划要求时测量。"],["血糖","测量时点很重要，此页面不输入读数。"],["日常活动","根据个人状况回顾合适的活动。"],["饮食习惯","观察习惯，不自动制定肾病食谱。"]]},
 ms: {language:"Bahasa",welcome:"Satu langkah kecil hari ini.",subtitle:"Pratonton jurnal harian yang ringkas, tanpa diagnosis atau sasaran klinikal.",heading:"Apa yang ingin anda catat?",note:"Ukur hanya jika disarankan dalam pelan penjagaan individu. Ini bukan arahan perubatan.",insightHeading:"Langkah seterusnya",insightEmpty:"Pilih satu item contoh untuk melihat maklum balas. Tiada data disimpan.",insightDone:"Item contoh dipilih. Jurnal sebenar memerlukan bacaan, sumber, masa dan pengesahan yang jelas.",safety:"AI Missy tidak menetapkan ubat, had cecair atau sasaran klinikal. Dapatkan bantuan profesional apabila perlu.",reset:"Set semula pratonton",footer:"Demonstrasi sintetik · Memori halaman sahaja · Tiada data pesakit sebenar · Bukan nasihat perubatan AI",back:"Kembali ke demo air luar talian",counter:n=>n+" daripada 4 item contoh dipilih (bukan rekod perubatan)",items:[["Tekanan darah","Ukur hanya jika pelan individu memerlukannya."],["Glukosa darah","Masa bacaan penting; tiada bacaan dimasukkan di sini."],["Aktiviti harian","Renung aktiviti yang sesuai dengan keadaan kesihatan anda."],["Tabiat pemakanan","Perhatikan satu tabiat; tiada diet buah pinggang ditetapkan."]]}
};
const node=id=>document.getElementById(id);
const checked=new Set();
const history=[];
let lastMessage="";
let largeText=false;

// Build26: optional synthetic modules, in-memory only, no clinical measurements.
const featureKeys=["glucose","pressure","renal","lipids"];
const enabledFeatures=new Set(["glucose","pressure"]);
const featureMeta={
 en:{heading:"Manage Functions",description:"Choose which sample care areas appear today. Nothing is stored.",session:"SESSION ONLY",note:"These switches only change this demonstration view. They do not configure clinical monitoring.",names:["Blood glucose","Blood pressure","Kidney care","Blood lipids"],details:["Sample glucose task only; no readings or insulin advice.","Sample pressure task only; no targets.","Follow-up reminder preview; no kidney risk prediction.","Lab follow-up preview; no lipid treatment advice."],renalTask:["Kidney follow-up","Follow the plan provided by your care professional; no readings entered."],lipidTask:["Blood lipid review","Note a future lab discussion; no levels or medicines entered."]},
 zh:{heading:"管理功能",description:"选择今天展示哪些照护领域。关闭后不会保存资料。",session:"仅本次会话",note:"开关只改变演示界面，不会设置临床监测或治疗。",names:["血糖管理","血压管理","肾脏健康","血脂管理"],details:["仅展示血糖示例任务；无读数或胰岛素建议。","仅展示血压示例任务；不设定目标。","复诊提醒预览；不预测肾病风险。","化验复查预览；不提供降脂治疗建议。"],renalTask:["肾脏复查任务","以医护计划为准；此处不输入检验数值。"],lipidTask:["血脂化验复查","仅供安排复查讨论；不填写结果或药物。"]},
 ms:{heading:"Urus Fungsi",description:"Pilih bidang penjagaan contoh untuk hari ini. Tiada data disimpan.",session:"SESI INI SAHAJA",note:"Suis ini hanya mengubah pratonton; bukan pelan pemantauan atau rawatan klinikal.",names:["Glukosa darah","Tekanan darah","Penjagaan buah pinggang","Lipid darah"],details:["Tugas contoh sahaja; tiada bacaan atau nasihat insulin.","Tugas contoh sahaja; tiada sasaran klinikal.","Pratonton susulan; bukan ramalan risiko buah pinggang.","Pratonton ujian makmal; bukan nasihat rawatan lipid."],renalTask:["Susulan buah pinggang","Ikut pelan penjagaan; tiada bacaan dimasukkan."],lipidTask:["Semakan lipid darah","Nota ujian makmal akan datang; tiada nilai atau ubat dimasukkan."]}
};


const dashboardCopy={
 en:{eyebrow:"MY CARE · SYNTHETIC",heading:"Today at a glance",description:"Only your selected care areas appear below.",status:"NOT A MEDICAL RECORD",completed:"Example tasks selected",remaining:"Example tasks remaining",empty:"No care modules selected. Use Manage Functions below.",boundary:"All tasks are fictional examples. Nothing is sent to PAIR or ACE.",done:"Selected",todo:"Not selected",open:"View task"},
 zh:{eyebrow:"我的照护 · 合成演示",heading:"今天的照护一览",description:"这里仅显示您在功能管理中启用的健康模块。",status:"非医疗记录",completed:"已选择的示例任务",remaining:"未选择的示例任务",empty:"尚未启用健康模块。请在下方的管理功能中选择。",boundary:"所有任务均为虚构示例，不向 PAIR 或 ACE 发送资料。",done:"已选择",todo:"未选择",open:"查看任务"},
 ms:{eyebrow:"PENJAGAAN SAYA · SINTETIK",heading:"Ringkasan penjagaan hari ini",description:"Hanya bidang penjagaan yang dipilih dipaparkan.",status:"BUKAN REKOD PERUBATAN",completed:"Tugas contoh dipilih",remaining:"Tugas contoh belum dipilih",empty:"Tiada modul dipilih. Gunakan Urus Fungsi di bawah.",boundary:"Semua tugas adalah contoh rekaan. Tiada data dihantar ke PAIR atau ACE.",done:"Dipilih",todo:"Belum dipilih",open:"Lihat tugas"}
};
const featureTaskIds={glucose:1,pressure:0,renal:4,lipids:5};
function paintDashboard(locale,fm){
 const d=dashboardCopy[locale];
 for(const [id,val] of [["care-eyebrow",d.eyebrow],["care-heading",d.heading],["care-description",d.description],["care-status",d.status],["care-completed-label",d.completed],["care-remaining-label",d.remaining],["care-empty",d.empty],["care-boundary",d.boundary]])node(id).textContent=val;
 const selected=featureKeys.filter(key=>enabledFeatures.has(key));
 const complete=selected.filter(key=>checked.has(featureTaskIds[key])).length;
 node("care-completed").textContent=String(complete);
 node("care-remaining").textContent=String(selected.length-complete);
 node("care-empty").hidden=selected.length!==0;
 const cards=node("care-cards");cards.replaceChildren();
 selected.forEach(key=>{
  const idx=featureKeys.indexOf(key);
  const done=checked.has(featureTaskIds[key]);
  const card=document.createElement("article");card.className="care-card";card.dataset.care=key;
  const top=document.createElement("div");top.className="care-card-head";
  const heading=document.createElement("strong");heading.textContent=fm.names[idx];
  const state=document.createElement("span");state.className=done?"care-state care-state-done":"care-state";state.textContent=done?d.done:d.todo;
  const detail=document.createElement("p");detail.textContent=fm.details[idx];
  const link=document.createElement("button");link.type="button";link.className="secondary care-task-link";link.textContent=d.open;
  link.addEventListener("click",()=>{
    const target=node("tasks").querySelector('input[data-index="'+featureTaskIds[key]+'"]');
    if(target){target.scrollIntoView({block:"center",behavior:"instant"});target.focus();}
  });
  top.append(heading,state);card.append(top,detail,link);cards.append(card);
 });
}


// Build29: immutable synthetic-only temporal observations, independent from task checkboxes.
// Contract: provenance + two timestamps + explicit status; no medical values or clinical scoring.
const timelineObservations=Object.freeze([
 Object.freeze({id:"SYN-BP-001",module:"pressure",event:"review",observedAt:"2026-10-03T09:30:00+08:00",recordedAt:"2026-10-03T09:35:00+08:00",source:"synthetic_patient_demo",confirmation:"unverified",evidenceId:"SYN-EV-101",synthetic:true,scope:"demo_only"}),
 Object.freeze({id:"SYN-GL-001",module:"glucose",event:"check_in",observedAt:"2026-10-10T08:15:00+08:00",recordedAt:"2026-10-10T08:20:00+08:00",source:"synthetic_patient_demo",confirmation:"unverified",evidenceId:"SYN-EV-102",synthetic:true,scope:"demo_only"}),
 Object.freeze({id:"SYN-RN-001",module:"renal",event:"follow_up",observedAt:"2026-10-17T14:00:00+08:00",recordedAt:"2026-10-17T14:05:00+08:00",source:"synthetic_care_plan",confirmation:"unverified",evidenceId:"SYN-EV-103",synthetic:true,scope:"demo_only"}),
 Object.freeze({id:"SYN-LP-001",module:"lipids",event:"lab_review",observedAt:"2026-10-24T11:00:00+08:00",recordedAt:"2026-10-24T11:07:00+08:00",source:"synthetic_care_plan",confirmation:"unverified",evidenceId:"SYN-EV-104",synthetic:true,scope:"demo_only"})
]);
function isValidTimelineObservation(e){
 const allowed=new Set(["glucose","pressure","renal","lipids"]);
 const iso=s=>typeof s==="string"&&/^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\+08:00$/.test(s)&&Number.isFinite(Date.parse(s));
 return e&&e.synthetic===true&&e.scope==="demo_only"&&allowed.has(e.module)&&
 ["id","source","evidenceId"].every(k=>typeof e[k]==="string"&&e[k].startsWith("SYN-")||k==="source"&&["synthetic_patient_demo","synthetic_care_plan"].includes(e[k]))&&
 e.confirmation==="unverified"&&iso(e.observedAt)&&iso(e.recordedAt)&&Date.parse(e.observedAt)<=Date.parse(e.recordedAt);
}
if(!timelineObservations.every(isValidTimelineObservation))throw new Error("SYNTHETIC_TIMELINE_CONTRACT_INVALID");
const timelineCopy={
 en:{eyebrow:"CONTEXT · SYNTHETIC",heading:"Care timeline",intro:"Dated fictional events with traceable source and confirmation status.",status:"READ ONLY",empty:"No dated examples for selected modules.",boundary:"Not a medical record, adherence measure or risk prediction. Nothing is saved.",events:{review:"Sample check-in",check_in:"Sample glucose check-in",follow_up:"Sample follow-up",lab_review:"Sample laboratory review"},source:"Source",recorded:"Recorded",confirmation:"Confirmation",evidence:"Evidence ID",scope:"Scope",inspect:"Show provenance",hide:"Hide provenance",unverified:"Not verified"},
 zh:{eyebrow:"长期上下文 · 合成演示",heading:"照护时间线",intro:"按日期展示虚构事件、来源与确认状态。",status:"仅供查看",empty:"所选模块暂无示例时间线。",boundary:"并非医疗记录、依从性指标或风险预测。不会保存资料。",events:{review:"模拟日常回顾",check_in:"模拟血糖记录事项",follow_up:"模拟肾脏复查",lab_review:"模拟血脂检验复查"},source:"来源",recorded:"登记时间",confirmation:"确认状态",evidence:"证据编号",scope:"使用范围",inspect:"查看来源证据",hide:"收起来源证据",unverified:"尚未验证"},
 ms:{eyebrow:"KONTEKS · SINTETIK",heading:"Garis masa penjagaan",intro:"Peristiwa rekaan mengikut tarikh, sumber dan status pengesahan.",status:"BACA SAHAJA",empty:"Tiada contoh bagi modul yang dipilih.",boundary:"Bukan rekod perubatan, ukuran pematuhan atau ramalan risiko. Tiada data disimpan.",events:{review:"Semakan contoh",check_in:"Semakan glukosa contoh",follow_up:"Susulan contoh",lab_review:"Semakan makmal contoh"},source:"Sumber",recorded:"Direkodkan",confirmation:"Pengesahan",evidence:"ID bukti",scope:"Skop",inspect:"Lihat asal-usul",hide:"Tutup asal-usul",unverified:"Belum disahkan"}
};
function paintTimeline(locale){
 const t=timelineCopy[locale],fm=featureMeta[locale];
 for(const [id,value] of [["timeline-eyebrow",t.eyebrow],["timeline-heading",t.heading],["timeline-intro",t.intro],["timeline-status",t.status],["timeline-empty",t.empty],["timeline-boundary",t.boundary]])node(id).textContent=value;
 const events=timelineObservations.filter(e=>enabledFeatures.has(e.module)).slice().sort((a,b)=>Date.parse(b.observedAt)-Date.parse(a.observedAt));
 const container=node("timeline-events");container.replaceChildren();node("timeline-empty").hidden=events.length!==0;
 events.forEach(e=>{
  const article=document.createElement("article");article.className="timeline-event";article.dataset.eventId=e.id;
  const heading=document.createElement("strong");heading.textContent=fm.names[featureKeys.indexOf(e.module)]+" · "+t.events[e.event];
  const day=document.createElement("time");day.dateTime=e.observedAt;day.textContent=e.observedAt.slice(0,10);
  const header=document.createElement("div");header.className="timeline-event-head";header.append(heading,day);
  const badge=document.createElement("p");badge.className="timeline-unverified";badge.textContent=t.unverified+" · "+e.id;
  const details=document.createElement("dl");details.className="timeline-provenance";details.hidden=true;
  for(const [label,value] of [[t.source,e.source],[t.recorded,e.recordedAt],[t.confirmation,e.confirmation],[t.evidence,e.evidenceId],[t.scope,e.scope]]){
   const term=document.createElement("dt");term.textContent=label;
   const data=document.createElement("dd");data.textContent=value;
   details.append(term,data);
  }
  const btn=document.createElement("button");btn.type="button";btn.className="secondary timeline-inspect";btn.textContent=t.inspect;btn.setAttribute("aria-expanded","false");
  btn.addEventListener("click",()=>{details.hidden=!details.hidden;btn.setAttribute("aria-expanded",String(!details.hidden));btn.textContent=details.hidden?t.inspect:t.hide;});
  article.append(header,badge,btn,details);container.append(article);
 });
}

function paint(focusIndex=null){
 const locale=node("language").value;
 const t=copy[locale];
 document.documentElement.lang=locale==="zh"?"zh-Hans":locale;
 for(const [id,value] of [["language-label",t.language],["welcome",t.welcome],["subtitle",t.subtitle],["tasks-heading",t.heading],["measurement-note",t.note],["insight-heading",t.insightHeading],["safety-note",t.safety],["reset",t.reset],["footer-text",t.footer],["back-link",t.back]])node(id).textContent=value;
 const guide=locale==="zh"?["体验操作说明","选择一个示例项目。","改变主意？可以撤销。","随时重置。不会保存任何资料。","撤销上一步","已撤销上一步。","没有可撤销的操作。"]:locale==="ms"?["Cara mencuba","Pilih satu item contoh.","Berubah fikiran? Gunakan buat asal.","Set semula bila-bila masa. Tiada data disimpan.","Buat asal tindakan","Tindakan terakhir dibatalkan.","Tiada tindakan untuk dibatalkan."]:["Try this preview","Choose one sample item.","Changed your mind? Use undo.","Reset at any time. Nothing is saved.","Undo last change","Last change undone.","No change to undo."];
 for(const [id,value] of [["guide-heading",guide[0]],["guide-one",guide[1]],["guide-two",guide[2]],["guide-three",guide[3]],["undo",guide[4]]])node(id).textContent=value;
 node("undo").disabled=history.length===0;
 node("action-message").textContent=lastMessage==="undone"?guide[5]:lastMessage==="nothing"?guide[6]:"";
 node("large-text").textContent=locale==="zh"?"放大文字":locale==="ms"?"Teks lebih besar":"Larger text";
 node("large-text").setAttribute("aria-pressed",String(largeText));
 node("skip-note").textContent=locale==="zh"?"任何项目都可以跳过。本演示不会为健康状况评分。":locale==="ms"?"Anda boleh langkau mana-mana item. Pratonton ini tidak memberi skor kesihatan.":"You may skip any item. This preview does not grade your health.";
 const fm=featureMeta[locale];
 for(const [id,value] of [["functions-heading",fm.heading],["functions-description",fm.description],["functions-session",fm.session],["functions-note",fm.note]])node(id).textContent=value;
 const options=node("function-options");options.replaceChildren();
 featureKeys.forEach((key,i)=>{
  const label=document.createElement("label");label.className="feature-option";
  const input=document.createElement("input");input.type="checkbox";input.dataset.feature=key;input.checked=enabledFeatures.has(key);input.setAttribute("aria-label",fm.names[i]);
  input.addEventListener("change",()=>{
   if(input.checked)enabledFeatures.add(key);else enabledFeatures.delete(key);
   if(!input.checked)checked.delete(key==="glucose"?1:key==="pressure"?0:key==="renal"?4:5);
   history.length=0;lastMessage="";paint();
   const next=options.querySelector(`input[data-feature="${key}"]`);if(next)next.focus();
  });
  const desc=document.createElement("span");desc.className="feature-copy";
  const title=document.createElement("strong");title.textContent=fm.names[i];
  const detail=document.createElement("small");detail.textContent=fm.details[i];
  desc.append(title,detail);label.append(input,desc);options.append(label);
 });
 const tasks=node("tasks");tasks.replaceChildren();
 const entries=t.items.map((entry,i)=>({entry,i}));
 entries.push({entry:fm.renalTask,i:4},{entry:fm.lipidTask,i:5});
 const visibleEntries=entries.filter(({i})=>i===0?enabledFeatures.has("pressure"):i===1?enabledFeatures.has("glucose"):i===4?enabledFeatures.has("renal"):i===5?enabledFeatures.has("lipids"):true);
 visibleEntries.forEach(({entry:[name,detail],i})=>{
  const label=document.createElement("label");label.className="task";
  const input=document.createElement("input");input.type="checkbox";input.checked=checked.has(i);input.setAttribute("aria-label",name);input.dataset.index=String(i);
  input.addEventListener("change",()=>{history.push(new Set(checked));if(input.checked)checked.add(i);else checked.delete(i);lastMessage="";paint(i);});
  const box=document.createElement("span");box.className="task-copy";
  const strong=document.createElement("strong");strong.textContent=name;
  const small=document.createElement("small");small.textContent=detail;
  box.append(strong,small);label.append(input,box);tasks.append(label);
 });
 node("summary").textContent=t.counter(checked.size).replace(/4(?= sample| 个| item)/,String(visibleEntries.length));
 node("insight").textContent=checked.size?t.insightDone:t.insightEmpty;
 paintDashboard(locale,fm);
 paintTimeline(locale);
 if(focusIndex!==null){const next=tasks.querySelector(`input[data-index="${focusIndex}"]`);if(next)next.focus();}
}
node("language").addEventListener("change",paint);
node("undo").addEventListener("click",()=>{if(!history.length){lastMessage="nothing";paint();return;}const prior=history.pop();checked.clear();for(const id of prior)checked.add(id);lastMessage="undone";paint();node("undo").focus();});
node("reset").addEventListener("click",()=>{checked.clear();history.length=0;lastMessage="";paint();});
node("large-text").addEventListener("click",()=>{largeText=!largeText;document.body.classList.toggle("large-type",largeText);paint();node("large-text").focus();});
paint();
