from pathlib import Path, PurePosixPath
import hashlib,json,re,zipfile,sys
root=Path(__file__).resolve().parent.parent
errors=[]
required=['README.md','CAD/README.md','CAD/Original_STEP_Exports.zip','PCB/jjkspeakerpcb.kicad_pcb','PCB/jjkspeakerpcb.kicad_sch','PCB/jjkspeakerpcb.kicad_pro','Firmware/JJK_Alarm/JJK_Alarm.ino','Firmware/JJK_Alarm/JJK_Hands_76x76.h','Production/gerbers.zip','Docs/ATTRIBUTION.md','Docs/SUBMISSION_CHECK.md']
for n in required:
 if not (root/n).is_file():errors.append('Missing '+n)
text=(root/'README.md').read_text()
for url in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
 if '://' in url or url.startswith('#'):continue
 target=root/url.split('#')[0]
 if not target.exists():errors.append('Broken README link: '+url)
manifest=json.loads((root/'Docs/Images/manifest.json').read_text())
for entry in manifest:
 p=root/entry['path']
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:errors.append('Original image changed: '+entry['path'])
if (root/'Production/gerbers.zip').exists():
 with zipfile.ZipFile(root/'Production/gerbers.zip') as z:
  if z.testzip():errors.append('Gerber CRC failed')
  expected={f'jjkspeakerpcb-{n}.gbr' for n in ['F_Cu','B_Cu','F_Mask','B_Mask','F_Silkscreen','B_Silkscreen','Edge_Cuts']} | {'jjkspeakerpcb-PTH.drl','jjkspeakerpcb-NPTH.drl'}
  if set(z.namelist())!=expected:errors.append('Gerber layer/drill inventory mismatch')
for p in (root/'Firmware').rglob('*'):
 if p.name=='secrets.h':errors.append('Private secrets file committed')
# Check product wording without banning honest AI assistance disclosure.
for p in [root/'README.md',*list((root/'Docs').rglob('*.md'))]:
 if re.search('ChatGPT'+r'[ _-]*image',p.read_text(),re.I):errors.append('Unwanted image label: '+str(p.relative_to(root)))
assert 'JJK Alarm' in text
if errors:
 print('\n'.join(errors));sys.exit(1)
print(f'PASS: source presence, README local links, {len(manifest)} original images, complete Gerber ZIP, and credential exclusion.')
print('Documentary check only. Outstanding CAD/attribution/size/acceptance items remain in Docs/SUBMISSION_CHECK.md.')
