"""Call the three copied fixed-workbench task/status tools after evidence repair.
No model generation, compiler lowering or historical CPU-test rerun.
"""
import asyncio, json, os, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
PACKAGE=Path(__file__).resolve().parents[2]
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
async def main():
    out=PACKAGE/'test-results'/('secondary-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True)
    config=json.loads((PACKAGE/'lmstudio-home/mcp.json').read_text());rows=[]
    for name,tool in [('biwn-instruction-workbench','get_biwn_instruction_task'),('biwn-string-workbench','get_biwn_string_task'),('biwn-compiler-workbench','get_biwn_string_optimization_status')]:
        entry=config['mcpServers'][name]
        with (out/(name+'-stderr.log')).open('w')as errors:
            async with stdio_client(StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(Path(entry['args'][0]).parent)),errlog=errors)as(r,w):
                async with ClientSession(r,w,read_timeout_seconds=timedelta(seconds=180))as client:
                    await client.initialize();listed=await client.list_tools();save(out/(name+'-inventory.json'),[x.model_dump(mode='json')for x in listed.tools])
                    result=await client.call_tool(tool,{});save(out/(tool+'.json'),result.model_dump(mode='json'));assert not result.isError,str(result)
                    rows.append(dict(server=name,tool=tool,isError=False,tools=len(listed.tools)));save(out/'calls.json',rows);print(name,tool,'passed',flush=True)
    state=dict(status='terminal_moved_three_secondary_workbench_read_calls_pass',directory=str(out),package=str(PACKAGE),python=sys.executable,calls=rows,new_predictions=0,new_training=False,fresh_CPU_tests=False,scope=__doc__)
    save(out/'protocol.json',state);save(PACKAGE/'portable-secondary-test-current.json',state);print(json.dumps(state))
if __name__=='__main__':asyncio.run(main())
