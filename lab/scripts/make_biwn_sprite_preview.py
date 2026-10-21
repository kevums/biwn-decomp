"""Diagnostic nonzero-word silhouettes, without assuming display colors."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
report = json.loads((root/'verification/biwn-sprite-decode-checks.json').read_text())
assets = json.loads((Path(report['directory'])/'fixtures.json').read_text())[:61]
assert all(x['C_result']['declared_pixels'] == x['C_result']['emitted_pixels'] for x in assets)
out = root/'artifacts/decoded-sprites'
out.mkdir(parents=True, exist_ok=True)
canvas = Image.new('RGB', (1000,600), '#111923')
draw = ImageDraw.Draw(canvas)
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22)
small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 17)
draw.text((28,20), 'Black Ice White Noise — reconstructed sprite decoder', fill='white', font=font)
draw.text((28,55), 'Nonzero-word silhouettes; diagnostic preview, not verified colors or a rebuilt frame.', fill='#b5c8d9', font=small)
preview = []
for j,index in enumerate([0,4,38,44,1,60]):
    row = assets[index]
    result = row['C_result']
    width,height = result['width'], result['height']
    raw = (Path(row['directory'])/'decoded-pixels.bin').read_bytes()
    assert len(raw) == width*height*2
    mask = Image.new('L', (width,height))
    mask.putdata([255 if int.from_bytes(raw[i:i+2], 'big') else 0 for i in range(0,len(raw),2)])
    scale = min(6,270//width,180//height)
    scaled = mask.resize((width*scale,height*scale), Image.Resampling.NEAREST)
    x,y = 28+(j%3)*325, 100+(j//3)*245
    tile = Image.new('RGB', (290,195), '#253446')
    tile.paste('#dbe9f2', (int((290-scaled.width)/2),int((195-scaled.height)/2)), scaled)
    canvas.paste(tile, (x,y))
    draw.text((x,y+202), f'Frame {index} • {width} × {height}', fill='white', font=small)
    mask.save(out/f'frame-{index:02d}-silhouette.png')
    preview.append({'frame':index,'width':width,'height':height,'raw16bit_pixels':str(Path(row['directory'])/'decoded-pixels.bin'),'mask_rule':'White iff raw16bitword !=0, black otherwise; displaycolor not interpreted.'})
canvas.save(out/'sprite-silhouettes.png')
(out/'provenance.json').write_text(json.dumps({'GPU_check_report':str(root/'verification/biwn-sprite-decode-checks.json'),'preview_scope':'Nonzero rawword silhouettes from checked C decoder, not original colors, game viewport or reconstructed inventoryframe.','frames':preview,'generator_initial_errors':['Initial one-off script had else0 syntax typo; no execution.','Corrected script used labvenv withoutPillow; no output. Used bundled document/image runtime without modifying modelvenv.']},indent=2)+'\n')
print(out/'sprite-silhouettes.png')
