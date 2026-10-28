#!/usr/bin/env python3
"""Attempt to isolate native pcbnew parser failures without hiding them."""
import re,sys,tempfile,pathlib
sys.path.insert(0,"/usr/lib/python3/dist-packages")
import pcbnew

original=pathlib.Path("PCB/jjkspeakerpcb.kicad_pcb").read_text()
start=original.index("(kicad_pcb")+len("(kicad_pcb")
s=original[start:]
groups=[]
begin=None;d=0;quoted=False;escaped=False
for i,c in enumerate(s):
    if quoted:
        if escaped:escaped=False
        elif c=="\\":escaped=True
        elif c=='"':quoted=False
        continue
    if c=='"':quoted=True;continue
    if c=='(':
        if d==0:begin=i
        d+=1
    elif c==')':
        if d>0:
            d-=1
            if d==0 and begin is not None:
                raw=s[begin:i+1]
                kind=re.match(r"\(\s*([^\s()]+)",raw).group(1)
                groups.append((kind,raw))
                begin=None
        else:
            break
print("Native diagnostic top-level groups",len(groups),flush=True)
header=[g for n,g in groups if n not in ("footprint","segment","via","gr_line","gr_text","zone")]
content=[(n,g) for n,g in groups if n in ("footprint","segment","via","gr_line","gr_text","zone")]
print("Groups:",{k:sum(n==k for n,g in groups) for k in sorted({n for n,g in groups})},flush=True)
directory=pathlib.Path(tempfile.mkdtemp(prefix="ggk_parser_"))
index=0
def check(items,label):
    global index
    index+=1
    path=directory/("debug_"+str(index)+".kicad_pcb")
    path.write_text("(kicad_pcb\n"+"\n".join(header+items)+"\n)")
    try:
        b=pcbnew.LoadBoard(str(path))
        ok=b is not None
        if b is not None:
            del b
    except Exception as e:
        ok=False
        print("EXCEPTION:",repr(e),flush=True)
    print("TEST:",label,"OK" if ok else "FAIL",flush=True)
    return ok
base=check([],"header-nets-only")
allbody=[x for _,x in content]
check(allbody,"fullbody")
for kind in ("footprint","segment","via","gr_line","gr_text","zone"):
    subset=[g for n,g in content if n==kind]
    check(subset,"kind-only:"+kind)
    if subset and not check([g for n,g in content if n!=kind],"all-except:"+kind):
        print("Not eliminated by excluding",kind,flush=True)
if base:
    cumul=[]
    for kind in ("footprint","segment","via","gr_line","gr_text","zone"):
        seq=[g for n,g in content if n==kind]
        if not check(cumul+seq,"cumulative-kind:"+kind):
            for j,g in enumerate(seq):
                if not check(cumul+[g],"single:"+kind+":"+str(j)):
                    print("FIRST LIKELY INVALID TOP-LEVEL GROUP:",kind,j,"TEXT:",g[:450],flush=True)
                    break
        else:
            cumul+=seq
