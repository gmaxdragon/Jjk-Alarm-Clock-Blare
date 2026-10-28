"""Prepare exact checked source/reference geometry for a local rebuild."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];w=root/'Build/Compact'
(w/'validated/CAD').mkdir(parents=True,exist_ok=True)
shutil.copyfile(root/'CAD/Reference/Ornament_Topology_Source.npz',w/'shrine_topology_preserved.npz')
shutil.copyfile(root/'CAD/Reference/PCB_Substrate.step',w/'validated/CAD/PCB_Substrate.step')
shutil.copyfile(root/'CAD/Checks/Compact_Routing.json',w/'validated/layout_and_routing.json')
print('Prepared Build/Compact. Original inputs and canonical release files unchanged.')
