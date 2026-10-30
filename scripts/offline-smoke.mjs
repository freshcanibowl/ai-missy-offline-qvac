// This script MUST be run with all network connections physically disconnected.
// A successful result is evidence of an SDK completion, not proof of total network isolation.
import {loadModel,completion,unloadModel,close,LLAMA_3_2_1B_INST_Q4_0} from '@qvac/sdk';
let id;
try {
  const start=Date.now();
  id=await loadModel({modelSrc:LLAMA_3_2_1B_INST_Q4_0,modelType:'llm',modelConfig:{ctx_size:2048}});
  const result=await completion({modelId:id,history:[{role:'user',content:'Reply with only the word LOCAL.'}],stream:true,generationParams:{temp:0,predict:32}}).final;
  const out=result.contentText?.trim()||'';
  if (!out || ['length','error','cancelled'].includes(result.stopReason)) throw Error('EMPTY_OR_INCOMPLETE_OUTPUT');
  if (!/\bLOCAL\b/i.test(out)) throw Error('MODEL_DID_NOT_FOLLOW_SIMPLE_PROMPT');
  console.log(JSON.stringify({engine:'QVAC_LOCAL',model:'LLAMA_3_2_1B_INST_Q4_0',model_loaded:true,generated_text:out.slice(0,160),stop_reason:result.stopReason||'unknown',latency_ms:Date.now()-start,offline_inference_completed:true}));
}catch(e){console.error('OFFLINE_INFERENCE_COMPLETED=false '+(e?.message||String(e)));process.exitCode=1;}
finally{if(id)await unloadModel({modelId:id,clearStorage:false}).catch(()=>{});await close().catch(()=>{});}
