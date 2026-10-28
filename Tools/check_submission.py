"""Check the current compact package without mistaking digital checks for hardware tests."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools/compact'))
from sexpr import loads,child,children,get
errors=[]
def need(p):
 if not (ROOT/p).is_file():errors.append('Missing '+p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
required=['README.md','CAD/README.md','CAD/JJK_Alarm_Assembly.step','PCB/jjkspeakerpcb.kicad_pcb','PCB/jjkspeakerpcb.kicad_sch','PCB/jjkspeakerpcb.kicad_pro','Firmware/JJK_Alarm/JJK_Alarm.ino','Firmware/JJK_Alarm/JJK_Hands_76x76.h','Production/gerbers.zip','Docs/ATTRIBUTION.md','Docs/SUBMISSION_CHECK.md','Archive/Original_125x110/README.md','CAD/Owner_Originals/JJK_Alarm_Clock_Enclosure.stl']
for p in required:need(p)
text=(ROOT/'README.md').read_text()
for url in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
 if '://' in url or url.startswith('#'):continue
 if not (ROOT/url.split('#')[0]).exists():errors.append('Broken README link: '+url)
for row in json.loads((ROOT/'Docs/Images/manifest.json').read_text()):
 p=ROOT/row['path']
 if not p.exists() or sha(p)!=row['sha256']:errors.append('Original image changed: '+row['path'])
# Original is preserved byte-for-byte, including project, schematic and Gerbers.
archive=ROOT/'Archive/Original_125x110'
for row in json.loads((archive/'PRESERVATION_SHA256.json').read_text()):
 p=archive/row['path']
 if not p.exists() or sha(p)!=row['sha256']:errors.append('Preserved file mismatch: '+row['path'])
def netmap(board):
 r={}
 for fp in children(board,'footprint'):
  ref=str(next(p[2] for p in children(fp,'property') if p[1]=='Reference'))
  r[ref]={str(p[1]):str(get(p,'net','')) for p in children(fp,'pad') if p[1]}
 return r
b=loads((ROOT/'PCB/jjkspeakerpcb.kicad_pcb').read_text())
old=loads((archive/'PCB/jjkspeakerpcb.kicad_pcb').read_text())
if netmap(b)!=netmap(old):errors.append('Electrical pad/net map changed')
outline=[e for e in children(b,'gr_rect') if get(e,'layer')=='Edge.Cuts']
if len(outline)!=1:errors.append('Expected one rectangular board outline')
else:
 a=list(map(float,child(outline[0],'start')[1:3]));z=list(map(float,child(outline[0],'end')[1:3]));dims=[abs(z[i]-a[i]) for i in range(2)]
 if any(abs(v-95)>1e-6 for v in dims):errors.append('PCB outline is not 95 x 95 mm')
with zipfile.ZipFile(ROOT/'Production/gerbers.zip') as z:
 expected={f'jjkspeakerpcb-{n}.gbr' for n in ['F_Cu','B_Cu','F_Mask','B_Mask','F_Silkscreen','B_Silkscreen','Edge_Cuts']} | {'jjkspeakerpcb-PTH.drl','jjkspeakerpcb-NPTH.drl'}
 if set(z.namelist())!=expected or z.testzip():errors.append('Gerber inventory or CRC failed')
 edge=z.read('jjkspeakerpcb-Edge_Cuts.gbr').decode()
 xy=[tuple(map(int,m)) for m in re.findall(r'X(-?\d+)Y(-?\d+)D0[12]\*',edge)]
 if not xy or any(abs((max(t[i] for t in xy)-min(t[i] for t in xy))/1e6-95)>1e-6 for i in (0,1)):errors.append('Gerber outline does not match 95 mm board')
for p in (ROOT/'Firmware').rglob('secrets.h'):errors.append('Private/local configuration file present: '+str(p.relative_to(ROOT)))
for p in [ROOT/'README.md',*(ROOT/'Docs').rglob('*.md')]:
 if re.search('ChatGPT'+r'[ _-]*image',p.read_text(),re.I):errors.append('Unwanted image caption: '+str(p.relative_to(ROOT)))
report=json.loads((ROOT/'CAD/Checks/Assembly_STEP_Validation.json').read_text())
if not report['all_solids_valid'] or report['STEP_reimport_solids']!=50:errors.append('STEP validation did not recover 50 valid solids')
if sha(ROOT/'CAD/JJK_Alarm_Assembly.step')!=report['STEP_sha256']:errors.append('STEP bytes differ from validated assembly')
for row in json.loads((ROOT/'CAD/Checks/Print_Mesh_Validation.json').read_text()):
 p=ROOT/'Production/Case_Parts'/(row['part']+'.stl')
 if not p.exists() or sha(p)!=row['sha256'] or not row['watertight_after_STL_reload'] or row['nonmanifold_edges']!=0:errors.append('Print part differs from validated mesh: '+row['part'])
mech=json.loads((ROOT/'CAD/Checks/Mechanical_Report.json').read_text())
if mech['component_carrier_collision_checks']:errors.append('Reference component collision checks not clear')
if sha(ROOT/'CAD/Owner_Originals/JJK_Alarm_Clock_Enclosure.stl')!=mech['original_enclosure_sha256']:errors.append('Owner enclosure source changed')
if errors:print('\n'.join(errors));sys.exit(1)
print('PASS: 95mm source/Gerber geometry, original pad nets, archive hashes, README links, original images, 50-solid STEP hash and three checked print meshes.')
print('Digital package checks only. Component measurements, physical commissioning, source attribution and organizer acceptance are separate.')
