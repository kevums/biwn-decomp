"""Reproduce invalid dictionary schema and verify the supported typed form."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import chat_tools,lmstudio
from lmstudio.json_api import ChatResponseEndpoint
import lmstudio._kv_config as kv
functions=[chat_tools.verify_68000_fixture,chat_tools.project_evidence,chat_tools.render_inventory_preview,chat_tools.render_animation_preview,chat_tools.inspect_boot,chat_tools.search_references];tools,_=ChatResponseEndpoint.parse_tools(functions)
def converted(config):
 _,stack=kv.prediction_config_to_kv_config_stack(None,config)
 return next(f['value']for layer in stack.to_dict()['layers']for f in layer['config']['fields']if f['key']=='llm.prediction.tools')
old=converted({'temperature':0.2,'rawTools':tools.to_dict()});typed=lmstudio.LlmPredictionConfig(temperature=0.2,raw_tools=tools);new=converted(typed);expected=tools.to_dict();assert new==expected
before=old['tools'][0]['function']['parameters'];assert 'bytesHex'in before['properties']and 'bytes_hex'in before['required'];after=new['tools'][0]['function']['parameters'];assert set(after['required'])<=set(after['properties'])and'initial_ccr'in after['properties']
for row in new['tools']:
 parameters=row['function']['parameters'];assert set(parameters.get('required',[]))<=set(parameters.get('properties',{}))
report=dict(status='typed_prediction_config_tool_schemas_preserved',tools=len(functions),dictionary_bug_reproduced=True,typed_schema_matches_callable_schema=True,SDK_global_files_changed=False,old_fixture_schema=before,new_fixture_schema=after)
(ROOT/'verification/SDK-tool-schema-roundtrip.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
