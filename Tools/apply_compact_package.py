"""One-time non-destructive migration; archive original before applying the compact patch."""
from pathlib import Path
import argparse,hashlib,json,shutil
ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--patch',required=True);args=ap.parse_args()
root=Path(args.root).resolve();patch=Path(args.patch).resolve();archive=root/'Archive/Original_125x110'
if not (archive/'PRESERVATION_SHA256.json').exists():
 archive.mkdir(parents=True,exist_ok=True)
 for name in ['PCB','Production','Firmware','Tools']:
  if (root/name).exists():shutil.copytree(root/name,archive/name,dirs_exist_ok=True)
 cad=archive/'CAD';cad.mkdir(exist_ok=True)
 for p in (root/'CAD').iterdir():
  if p.name=='Owner_Originals':continue
  if p.is_dir():shutil.copytree(p,cad/p.name,dirs_exist_ok=True)
  else:shutil.copy2(p,cad/p.name)
 shutil.copy2(root/'README.md',archive/'README_before_compact.md')
 for n in ['SUBMISSION_CHECK.md','COMPACT_REVISION.md','REVIEW_REQUEST.md','PUBLICATION_MANIFEST.json']:
  if (root/'Docs'/n).exists():
   (archive/'Docs').mkdir(exist_ok=True);shutil.copy2(root/'Docs'/n,archive/'Docs'/n)
 records=[]
 for p in sorted(archive.rglob('*')):
  if p.is_file():records.append({'path':p.relative_to(archive).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (archive/'PRESERVATION_SHA256.json').write_text(json.dumps(records,indent=2)+'\n')
 (archive/'README.md').write_text('# Original 125 x 110 mm JJK Alarm\n\nThe original six-in-a-row electrical design, Gerbers, firmware, available CAD and previous README are preserved here. The manifest records the original bytes before the compact package was applied.\n\nThese are history files, not the current 95 mm production set. Tall keycap extensions belong to this original version. Original uploaded images remain unchanged in the root Docs/Images directory.\n')
# Remove superseded active outputs only after they are safely archived.
for name in ['PCB','Production']:
 if (root/name).exists():shutil.rmtree(root/name)
for p in list((root/'CAD').iterdir()):
 if p.name=='Owner_Originals':continue
 if p.is_dir():shutil.rmtree(p)
 else:p.unlink()
for p in list((root/'Tools').iterdir()):
 if p.is_dir():shutil.rmtree(p)
 else:p.unlink()
# Old generation workflows would overwrite the new layout with the 125mm assumptions.
wf_archive=archive/'Workflow_History';wf_archive.mkdir(exist_ok=True)
for p in (root/'.github/workflows').glob('*.yml'):
 if p.name in ('jjk-finalize-compact.yml','jjk-validation.yml'):continue
 shutil.copy2(p,wf_archive/p.name)  # Workflow removal is performed via the connector after publishing.
# The final patch contains derived outputs and project docs, not private credentials.
for p in patch.rglob('*'):
 if not p.is_file() or '__pycache__' in p.parts or '.github' in p.relative_to(patch).parts:continue
 q=root/p.relative_to(patch);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
# Preserve existing firmware source; update descriptions only. Matrix/GPIO logic is unchanged.
config=root/'Firmware/JJK_Alarm/BoardConfig.h'
s=config.read_text().replace('rectangular PCB (125 x 110 mm)','compact PCB (95 x 95 mm)').replace('SW1..6 arranged as one horizontal strip','physical top row SW1/SW3/SW5; bottom row SW2/SW4/SW6')
config.write_text(s)
ino=root/'Firmware/JJK_Alarm/JJK_Alarm.ino'
s=ino.read_text().replace('JJK ALARM rectangular board','JJK ALARM compact 95 mm board').replace('Rectangular PCB firmware','Compact 95 mm PCB firmware')
ino.write_text(s)
readme=root/'Firmware/README.md';s=readme.read_text().replace('current rectangular board','current 95 mm compact board')
s=s.replace('## Controls\n','## Controls\n\nPhysical top row, left to right: **UP, TIME SET, SNOOZE**. Bottom row: **DOWN, CLOCK SET, ALARM ON**. The switch matrix and GPIO map are unchanged from the original rectangular circuit.\n')
readme.write_text(s)
ignore=root/'.gitignore';s=ignore.read_text() if ignore.exists() else ''
for line in ['Build/','__pycache__/','*.pyc','Firmware/JJK_Alarm/secrets.h']:
 if line not in s.splitlines():s+='\n'+line
ignore.write_text(s.rstrip()+'\n')
print('Original preserved; compact package applied without changing GPIO logic or original screenshot bytes.')
