from pathlib import Path
import shutil, hashlib, json, zipfile, re
root=Path('.'); legacy=root/'Archive/Legacy_T_Shaped_RevD'
def archive(path, dest=None):
 p=root/path
 if not p.exists(): return
 q=(root/dest) if dest else legacy/path
 q.parent.mkdir(parents=True,exist_ok=True)
 if q.exists(): raise RuntimeError('Archive collision: '+str(q))
 shutil.move(str(p),str(q))
# Archive only known superseded generation/configuration artifacts.
for n in ['build_board.py','make_libraries.py','render_kicad_geometry.py','render_preview.py','test_routing.py','verify_board_geometry.py',
          'Docs/BOM_Kit_Only.csv','Docs/GGK_ALARM_ONE_MASTER_BUILD_AND_TIMELAPSE_GUIDE.md',
          'Docs/PCB_Outline_for_Tinkercad.svg','Docs/POWER_OPTIONS.md','Docs/RELEASE_GATES.json',
          'Docs/REV_D_ENGINEERING_AUDIT_20261025.md','Docs/SAFETY_FIRST_POWER.md','Docs/Tinkercad_fit_guide.md',
          'Docs/generator_report.json','Docs/geometry_check.json','Docs/independent_connectivity.json','Docs/physical_pad_map.json',
          'PCB/GGK.kicad_sym','PCB/GGK.pretty','PCB/fp-lib-table','PCB/sym-lib-table',
          '.github/workflows/ggk-engineering-gate.yml','.github/workflows/ggk-esp32-real-compile.yml']:
 archive(n)
archive('Docs/RECTANGULAR_WIP_STATUS_2026-10-26.md','Archive/Rectangular_Development/RECTANGULAR_WIP_STATUS_2026-10-26.md')
archive('Firmware/RECTANGULAR_FLASH_AND_TEST.md','Archive/Rectangular_Development/RECTANGULAR_FLASH_AND_TEST.md')
archive('Production/Incomplete_Gerbers','Archive/Incomplete_Gerbers')
archive('Production/GENERATE_GERBERS.sh','Archive/Rectangular_Development/GENERATE_GERBERS.sh')
archive('.github/workflows/blare-preview-gerbers.yml','Archive/Rectangular_Development/blare-preview-gerbers.yml')
archive('.github/workflows/blare-rectangular-firmware.yml','Archive/Rectangular_Development/blare-rectangular-firmware.yml')
# The native project filenames remain aligned; preserve all three source files verbatim.
for ext,sha in [('kicad_pcb','3351412a618d503bc12ae340c8929a538e5a25b4'),('kicad_sch','62d6689fb959df01a41eee5e92389d74f2917390'),('kicad_pro','ecab10fddb41fcffac219a8a5fd1fab3df81be36')]:
 data=(root/'PCB'/('jjkspeakerpcb.'+ext)).read_bytes()
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==sha, 'PCB source changed unexpectedly: '+ext
old=root/'Firmware/GGK_Alarm';new=root/'Firmware/JJK_Alarm'
if old.exists():
 assert not new.exists();old.rename(new);(new/'GGK_Alarm.ino').rename(new/'JJK_Alarm.ino')
# Do not alter the actual firmware functionality or first-power audio settings.
keep={'alarm_logic_tests.cpp','time_tools_tests.cpp'}
for p in list((root/'Tests').iterdir()):
 if p.name not in keep: archive(str(p))
for p in (root/'Tests').glob('*.cpp'):
 p.write_text(p.read_text().replace('Firmware/GGK_Alarm','Firmware/JJK_Alarm'))
review=root/'Production/ReviewOnly'; reports=root/'Production/Reports';reports.mkdir(parents=True,exist_ok=True)
if review.exists():
 z=review/'gerbers.zip'
 assert z.exists()
 shutil.copyfile(z,root/'Production/gerbers.zip')
 for n in ['native_erc.rpt','native_drc.rpt','drill_report.rpt']:
  shutil.copyfile(review/n,reports/n)
 archive('Production/ReviewOnly','Archive/Rectangular_Development/ReviewOnly')
archive('CAD/CASE_PENDING.txt','Archive/Rectangular_Development/CASE_PENDING.txt')
(root/'Archive/README.md').write_text('# Historical files\n\nThese are superseded T-shaped-design sources and earlier rectangular working exports. They are retained for history, not for fabrication or current dimensions. Use the root PCB, Firmware, CAD and Production folders.\n')
# No credentials or lock files enter the active project.
assert not list((root/'Firmware').rglob('secrets.h'))
for p in root.rglob('*.lck'):
 if '.git' not in p.parts: raise RuntimeError('Lock file in package: '+str(p))
print('Organized the rectangular submission; PCB source hashes unchanged.')
