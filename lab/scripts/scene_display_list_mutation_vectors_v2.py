"""Additional distinct declared-reread fixtures, separate from the original1217host run."""
import json
import check_scene_display_list_structured_host_v1 as parent

def cases(snapshot):
    old=parent.base.cases(snapshot);rows=[]
    for i in range(64):
        x=json.loads(json.dumps(old[1+i%2]));sup=bool(i//32)
        x.update(id=1200+i,kind='distinct_declared_reread_CCR_bank',SR=(0x2000 if sup else 0)|((i%8)<<8)|(i%32),body=bool(i%2),usp=0x170000 if sup else parent.base.SP,ssp=parent.base.SP if sup else 0x1d0000)
        x['registers'][0]=(x['registers'][0]+i*0x9e3779b9)&0xffffffff
        x['registers'][3]^=(i*0x1234567)&0xffffffff
        x['read_queues']=[dict(address=0x120006,width=4,values=[1,2]),dict(address=0x120012,width=2,values=[[0xffff,0x8000,0x0001,0x7fff][i%4],(i*1777+1)&65535])]
        rows.append(x)
    assert len({json.dumps({k:v for k,v in x.items()if k!='id'},sort_keys=True)for x in rows})==64
    return rows
