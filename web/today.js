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
 if(focusIndex!==null){const next=tasks.querySelector(`input[data-index="${focusIndex}"]`);if(next)next.focus();}
}
node("language").addEventListener("change",paint);
node("undo").addEventListener("click",()=>{if(!history.length){lastMessage="nothing";paint();return;}const prior=history.pop();checked.clear();for(const id of prior)checked.add(id);lastMessage="undone";paint();node("undo").focus();});
node("reset").addEventListener("click",()=>{checked.clear();history.length=0;lastMessage="";paint();});
node("large-text").addEventListener("click",()=>{largeText=!largeText;document.body.classList.toggle("large-type",largeText);paint();node("large-text").focus();});
paint();
