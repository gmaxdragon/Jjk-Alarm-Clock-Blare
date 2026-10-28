import os,sys,subprocess,time,json,random
py=sys.executable
root=os.path.dirname(__file__)
P='PIEZO 3V3 DISP_CS DISP_DC DISP_MOSI DISP_SCK K1 K2 K3 K4 K5 K6 ROW_LEFT ROW_RIGHT COL_TOP COL_MIDDLE COL_BOTTOM'.split()
orders=[
 'K6 K5 K4 K3 K2 K1 PIEZO DISP_DC DISP_CS DISP_SCK DISP_MOSI 3V3 ROW_LEFT ROW_RIGHT COL_BOTTOM COL_MIDDLE COL_TOP',
 'K1 K2 K3 K4 K5 K6 COL_BOTTOM COL_MIDDLE COL_TOP ROW_LEFT ROW_RIGHT PIEZO DISP_DC DISP_CS DISP_MOSI DISP_SCK 3V3',
 'DISP_DC DISP_MOSI DISP_SCK DISP_CS PIEZO 3V3 K6 K5 K4 K3 K2 K1 COL_BOTTOM COL_MIDDLE COL_TOP ROW_LEFT ROW_RIGHT',
 'K6 K5 K4 K3 K2 K1 COL_BOTTOM COL_MIDDLE COL_TOP ROW_LEFT ROW_RIGHT DISP_DC DISP_SCK DISP_MOSI DISP_CS PIEZO 3V3',
 'K6 K4 K3 K5 K2 K1 DISP_DC DISP_SCK DISP_CS DISP_MOSI PIEZO 3V3 COL_BOTTOM COL_TOP COL_MIDDLE ROW_LEFT ROW_RIGHT',
 'DISP_DC DISP_SCK DISP_MOSI DISP_CS K1 K2 K3 K4 K5 K6 3V3 PIEZO COL_TOP COL_BOTTOM COL_MIDDLE ROW_LEFT ROW_RIGHT',
]
assert all(set(o.split())==set(P) for o in orders)
for j,order in enumerate(orders):
 ts=time.time(); env=os.environ.copy();env['GGK_ROUTE_PRIORITY']=','.join(order.split())
 try:r=subprocess.run([py,root+'/build_board.py'],env=env,capture_output=True,text=True,timeout=38)
 except subprocess.TimeoutExpired:print('RUN',j,'TIMEOUT', flush=True); continue
 if r.returncode: print('RUN',j,'ERROR',r.stderr[-500:],flush=True);continue
 report=json.load(open(root+'/Docs/generator_report.json'))
 issues=[x['net'] for x in report['routing'] if x['status']=='UNROUTED']
 print('RUN',j,'unrouted',len(issues),issues,'elapsed',round(time.time()-ts,1),'vias',report['vias'],flush=True)
 # Preserve best version files, so we can revisit the proper order after.
 import shutil
 if len(issues)<=2:
  target=root+'/Routes_'+str(j);os.makedirs(target,exist_ok=True)
  for f in ['jjkspeakerpcb.kicad_pcb','jjkspeakerpcb.kicad_sch']:
   shutil.copy(root+'/PCB/'+f,target+'/'+f)
  shutil.copy(root+'/Docs/generator_report.json',target+'/route_report.json')
 if len(issues)==0:break
