"use strict";
// Build19 intentionally has no fetch, localStorage, IndexedDB, or clinical write path.
const copy = {
 en: {language:"Language",welcome:"One small step today.",subtitle:"A gentle preview of a daily care journal, without diagnoses or clinical targets.",heading:"What would you like to note?",note:"Record only measurements recommended in your care plan. Nothing here is a clinical instruction.",insightHeading:"Your next step",insightEmpty:"Select a sample item to see a gentle reflection. No information is saved.",insightDone:"This sample check-in is selected. A real journal would require a verified observation, source, date, and your explicit confirmation.",safety:"AI Missy cannot set medicines, fluid limits, or clinical targets. Seek professional care when you need medical help.",reset:"Reset this preview",footer:"Synthetic demonstration · Memory only · No real patient data · No AI medical advice",back:"Back to offline water demo",counter:n=>n+" of 4 sample items selected (not medical records)",items:[["Blood pressure","Measure only if your individual plan calls for it."],["Blood glucose","The timing of a reading matters; no number is entered here."],["Daily movement","Reflect on activity appropriate to your health situation."],["Food habits","Notice a habit; no renal diet is prescribed."]]},
 zh: {language:"语言",welcome:"今天，照顾自己一点点。",subtitle:"温和的日常健康日记预览，不诊断疾病，也不设定医疗目标。",heading:"今天想记录什么？",note:"仅按照个人照护计划测量所需指标。此页面不提供医疗指示。",insightHeading:"你的下一步",insightEmpty:"选择一个示例项目，查看温和提示。不会保存任何资料。",insightDone:"已选择示例记录。真实日记仍需核实数值、来源、时间与用户明确确认。",safety:"AI Missy 不会设定药物、饮水限制或临床目标。如需医疗协助，请联系适当的专业人员。",reset:"重置演示",footer:"合成演示 · 仅暂存于页面内存 · 无真实患者资料 · 非 AI 医疗建议",back:"返回离线饮水演示",counter:n=>"已选择 "+n+" / 4 个示例项目（非医疗记录）",items:[["血压","仅在个人监测计划要求时测量。"],["血糖","测量时点很重要，此页面不输入读数。"],["日常活动","根据个人状况回顾合适的活动。"],["饮食习惯","观察习惯，不自动制定肾病食谱。"]]},
 ms: {language:"Bahasa",welcome:"Satu langkah kecil hari ini.",subtitle:"Pratonton jurnal harian yang ringkas, tanpa diagnosis atau sasaran klinikal.",heading:"Apa yang ingin anda catat?",note:"Ukur hanya jika disarankan dalam pelan penjagaan individu. Ini bukan arahan perubatan.",insightHeading:"Langkah seterusnya",insightEmpty:"Pilih satu item contoh untuk melihat maklum balas. Tiada data disimpan.",insightDone:"Item contoh dipilih. Jurnal sebenar memerlukan bacaan, sumber, masa dan pengesahan yang jelas.",safety:"AI Missy tidak menetapkan ubat, had cecair atau sasaran klinikal. Dapatkan bantuan profesional apabila perlu.",reset:"Set semula pratonton",footer:"Demonstrasi sintetik · Memori halaman sahaja · Tiada data pesakit sebenar · Bukan nasihat perubatan AI",back:"Kembali ke demo air luar talian",counter:n=>n+" daripada 4 item contoh dipilih (bukan rekod perubatan)",items:[["Tekanan darah","Ukur hanya jika pelan individu memerlukannya."],["Glukosa darah","Masa bacaan penting; tiada bacaan dimasukkan di sini."],["Aktiviti harian","Renung aktiviti yang sesuai dengan keadaan kesihatan anda."],["Tabiat pemakanan","Perhatikan satu tabiat; tiada diet buah pinggang ditetapkan."]]}
};
const node=id=>document.getElementById(id);
const checked=new Set();
function paint(){
 const locale=node("language").value;
 const t=copy[locale];
 document.documentElement.lang=locale==="zh"?"zh-Hans":locale;
 for(const [id,value] of [["language-label",t.language],["welcome",t.welcome],["subtitle",t.subtitle],["tasks-heading",t.heading],["measurement-note",t.note],["insight-heading",t.insightHeading],["safety-note",t.safety],["reset",t.reset],["footer-text",t.footer],["back-link",t.back]])node(id).textContent=value;
 const tasks=node("tasks");tasks.replaceChildren();
 t.items.forEach(([name,detail],i)=>{
  const label=document.createElement("label");label.className="task";
  const input=document.createElement("input");input.type="checkbox";input.checked=checked.has(i);input.setAttribute("aria-label",name);
  input.addEventListener("change",()=>{if(input.checked)checked.add(i);else checked.delete(i);paint();});
  const box=document.createElement("span");box.className="task-copy";
  const strong=document.createElement("strong");strong.textContent=name;
  const small=document.createElement("small");small.textContent=detail;
  box.append(strong,small);label.append(input,box);tasks.append(label);
 });
 node("summary").textContent=t.counter(checked.size);
 node("insight").textContent=checked.size?t.insightDone:t.insightEmpty;
}
node("language").addEventListener("change",paint);
node("reset").addEventListener("click",()=>{checked.clear();paint();});
paint();
