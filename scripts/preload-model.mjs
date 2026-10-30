import {downloadAsset, LLAMA_3_2_1B_INST_Q4_0, close} from '@qvac/sdk';
try {const r=await downloadAsset({assetSrc:LLAMA_3_2_1B_INST_Q4_0});console.log('MODEL_PRELOAD_COMPLETED=true',JSON.stringify(r));}
catch(e){console.error('MODEL_PRELOAD_FAILED',e);process.exitCode=1;}
finally{await close().catch(()=>{});}
