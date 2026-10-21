"""Fresh optimized formatter runs, same observers and controller policies."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 out=ROOT/'verification/native-fast-core-gameplay-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);records=[]
 def emit(name,target_name,transform):
  source=ROOT/'scripts'/name;text=transform(source.read_text());target=ROOT/'scripts'/target_name;compile(text,str(target),'exec');target.write_text(text);(out/('parent-'+name)).write_bytes(source.read_bytes());(out/target_name).write_bytes(target.read_bytes());records.append(dict(parent=str(source),parent_sha256=sha(source),derived=str(target),derived_sha256=sha(target)))
 emit('run_biwn_native_core_entry_deck_pair.py','run_biwn_native_fast_core_entry_deck_pair.py',lambda t:t.replace('native-core-format','native-fast-core-format').replace('native-core-entry','native-fast-core-entry'))
 emit('run_format_core_long_routes.py','run_format_fast_core_long_routes.py',lambda t:t.replace("[('parent','native-number-format'),('core','native-core-format')]","[('parent','native-number-format'),('fast','native-fast-core-format')]").replace("builds['core']","builds['fast']").replace('native-core-format-long-route','native-fast-core-format-long-route'))
 emit('run_native_core_raw_layout_control.py','run_native_fast_core_raw_layout_control.py',lambda t:t.replace('native-core-format','native-fast-core-format').replace('native-core-raw-layout','native-fast-core-raw-layout').replace("row['lane']=='core'","row['lane']=='fast'").replace('15408payload','14664payload'))
 state=dict(status='inline_formatter_gameplay_drivers_prepared',directory=str(out),drivers=records,default_promoted=False,new_training=False)
 save(out/'preparation.json',state);save(ROOT/'verification/native-fast-core-gameplay-preparation-current.json',state);print(out)
if __name__=='__main__':main()
