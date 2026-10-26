#!/usr/bin/env python3
"""Fail-closed design invariants tied to *source*, not an AI drawing.

These assertions catch accidental restoring of the unsafe GPIO9 display
assignment, reversed diodes or declaring battery/audio safely enabled.
"""
from __future__ import annotations
import json,re,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=runpy.run_path(str(root/'build_board.py'))
parts={p['ref']:p for p in d['parts']}
pin={q['number']:q['net'] for q in parts['U1']['pads']}
assert pin=={
    '1':'','2':'DISP_DC','3':'DISP_CS','4':'COL_TOP',
    '5':'COL_MIDDLE','6':'COL_BOTTOM','7':'DISP_SCK',
    '8':'DISP_MOSI','9':'ROW_LEFT','10':'ROW_RIGHT',
    '11':'PIEZO','12':'3V3','13':'GND','14':'',
    **{str(i):None for i in range(15,23)}
}, pin
assert not any(v=='VBUS' for v in pin.values())
assert not any(v=='BAT' for v in pin.values())
expected={
    'D1':('K1','ROW_LEFT'),
    'D2':('K2','ROW_RIGHT'),
    'D3':('K3','ROW_LEFT'),
    'D4':('K4','ROW_RIGHT'),
    'D5':('K5','ROW_LEFT'),
    'D6':('K6','ROW_RIGHT'),
}
for ref,nets in expected.items():
    q={x['number']:x['net'] for x in parts[ref]['pads']}
    assert (q['1'],q['2'])==nets,(ref,q)
h={q['number']:q['net'] for q in parts['J1']['pads']}
assert h=={'1':'GND','2':'3V3','3':'DISP_SCK','4':'DISP_MOSI',
          '5':'3V3','6':'DISP_DC','7':'DISP_CS','8':'GND'}
board=(root/'Firmware/GGK_Alarm/BoardConfig.h').read_text()
assert 'ROW0 = 8, ROW1 = 9' in board
assert 'COL0 = 5, COL1 = 6, COL2 = 7' in board
assert 'TFT_SCK = 21, TFT_MOSI = 20, TFT_DC = 3, TFT_CS = 4' in board
assert 'BUZZER = 10' in board
ino=(root/'Firmware/GGK_Alarm/GGK_Alarm.ino').read_text()
assert 'pinMode(ROW[i],INPUT_PULLUP)' in ino
assert 'pinMode(COL[c],INPUT)' in ino
assert 'pinMode(COL[c],OUTPUT)' in ino
assert 'digitalWrite(COL[c],LOW)' in ino
assert 'if(!soundAllowed())return;' in ino
assert 'GGK_BUZZER_VERIFIED==1 && GGK_HARDWARE_INSPECTED==1' in ino
assert 'uint32_t elapsed=currentMs()-alertAtMs;' in ino
assert 'ggk::MAX_RING_SECONDS*1000UL' in ino
sample=(root/'Firmware/GGK_Alarm/secrets.example.h').read_text()
assert '#define GGK_BUZZER_VERIFIED 0' in sample
assert '#define GGK_HARDWARE_INSPECTED 0' in sample
assert '#define GGK_PORTAL_PIN ""' in sample
report=json.loads((root/'Docs/RELEASE_GATES.json').read_text())
assert report['status']=='DESIGN_HOLD_NOT_FOR_OVERNIGHT_USE'
assert report['power']['internal_battery_installed'] is False
assert report['power']['fully_unplugged_supported'] is False
assert report['release_approved'] is False
print('GGK pin map, diode direction, 3V3 TFT, USB-only, safe-audio defaults: PASS')
