"""Factual routing handles length preambles without converting actions to lookup."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat
positive=[
 'What does the native copy replace?',
 'In under120words, what does the native copy replace?',
 'In at most 80 words: explain the native heap tests.',
 'Briefly, what does the native blitter work prove?',
 'Concisely, in fewer than 100 words, how is the native copy tested?']
negative=[
 'In under120words, run the native copy tests.',
 'In at most 80 words: can you build the native copy disc?',
 'Briefly, write a native copy routine.',
 'What does the native copy replace, and then rebuild the disc?',
 'In under120words, what does the native copy replace, and build a new disc?',
 'In under120words, what does the native copy replace? Do not fetch evidence.',
 'Correct grammar only: what does the native copy replace?',
 'What is the weather today?']
rows=[]
for task in positive+negative:
 actual=assistant_chat.game_evidence_topic(task);expected='input_dispatch'if task in positive else None
 assert actual==expected,(task,actual,expected);rows.append(dict(task=task,actual=actual))
print(json.dumps(dict(status='passed',cases=rows,scope='Host source-topic selector only; no model inference, semantic or UI validation.'),indent=2))
