"""Independent directed-connectivity test of PCB diodes versus firmware scanning.

Enumerates all 64 physical switch combinations. This is a circuit/topology
model, not an ESP32 electrical, timing, debounce or hardware test.
"""
from pathlib import Path
import itertools,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools/compact'))
from sexpr import loads,children,child
board=loads((ROOT/'PCB/jjkspeakerpcb.kicad_pcb').read_text())
parts={str(next(p[2] for p in children(f,'property') if p[1]=='Reference')):f for f in children(board,'footprint')}
def net(ref,pad):
 return str(child(next(p for p in children(parts[ref],'pad') if str(p[1])==str(pad)),'net')[-1])
config=(ROOT/'Firmware/JJK_Alarm/BoardConfig.h').read_text()
sketch=(ROOT/'Firmware/JJK_Alarm/JJK_Alarm.ino').read_text()
logic=(ROOT/'Firmware/JJK_Alarm/AlarmLogic.h').read_text()
pins={k:int(v) for k,v in re.findall(r'\b(ROW[01]|COL[012])\s*=\s*(\d+)',config)}
assert pins==dict(ROW0=8,ROW1=9,COL0=5,COL1=6,COL2=7)
# Physical XIAO header mapping, independent of switch numbering.
rows=[net('J2',6),net('J2',5)]
cols=[net('J1',4),net('J1',5),net('J1',6)]
assert rows==['/LEFT','/RIGHT'] and cols==['/TOP','/MID','/BOT']
assert re.search(r'col\s*\*\s*2\s*\+\s*row',logic)
assert 'digitalWrite(COL[c],LOW)' in sketch and 'pinMode(COL[c],INPUT)' in sketch
assert 'pinMode(ROW[i],INPUT_PULLUP)' in sketch
assert 'delayMicroseconds(80)' in sketch
assert re.search(r'enum Key[^\n]+UP=0, DOWN=1, TIME_SET=2, CLOCK_SET=3, SNOOZE=4, ALARM_ON=5',sketch)
assert 'JJK_BUZZER_VERIFIED==1 && JJK_HARDWARE_INSPECTED==1' in sketch
defaults=(ROOT/'Firmware/JJK_Alarm/secrets.example.h').read_text()
for flag in ['JJK_BUZZER_VERIFIED','JJK_HARDWARE_INSPECTED']:
 assert re.search(r'#define\s+'+flag+r'\s+0\b',defaults)
def reaches(graph,start,target):
 seen=set(); pending=[start]
 while pending:
  node=pending.pop()
  if node==target:return True
  if node not in seen:
   seen.add(node);pending.extend(graph.get(node,()))
 return False
for mask in range(64):
 graph={}
 def link(a,b):graph.setdefault(a,[]).append(b)
 for i in range(1,7):
  # KiCad D_DO-35 pad 1 is cathode, pad 2 is anode.
  assert net('D'+str(i),1)==net('SW'+str(i),2)
  link(net('D'+str(i),2),net('D'+str(i),1))
  if mask & (1<<(i-1)):
   a,b=net('SW'+str(i),1),net('SW'+str(i),2)
   link(a,b);link(b,a)
 observed=0
 for c,col in enumerate(cols):
  for r,row in enumerate(rows):
   if reaches(graph,row,col):observed|=1<<(2*c+r)
 assert observed==mask,(mask,observed)
print('PASS: 64 physical switch combinations; no topology-model ghost keys or key-order mismatch.')
print('PASS: GPIO/header map, scan direction and disabled first-power sound settings.')
print('Not tested: ESP32 thresholds, leakage, debounce timing, held-key reset/boot, real switches or buzzer.')

