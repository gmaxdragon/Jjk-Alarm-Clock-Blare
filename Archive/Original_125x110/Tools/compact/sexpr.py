import re,json
class Q(str): pass
def loads(s):
 toks=re.finditer(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+)',s)
 stack=[];out=None
 for m in toks:
  t=m[1]
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   else:out=a
   stack.append(a)
  elif t==')':stack.pop()
  elif t.startswith('"'):stack[-1].append(Q(json.loads(t)))
  else:stack[-1].append(t)
 assert not stack
 return out
def dumps(a,level=0):
 if not isinstance(a,list):return json.dumps(str(a),ensure_ascii=False) if isinstance(a,Q) else str(a)
 if not any(isinstance(x,list) for x in a):return '('+' '.join(map(dumps,a))+')'
 return '('+str(a[0])+''.join(('\n'+'  '*(level+1)+dumps(x,level+1)) if isinstance(x,list) else (' '+dumps(x)) for x in a[1:])+'\n'+'  '*level+')'
def child(a,k):return next((v for v in a if isinstance(v,list) and v and v[0]==k),None)
def children(a,k):return [v for v in a if isinstance(v,list) and v and v[0]==k]
def get(a,k,default=None):
 v=child(a,k)
 return v[1] if v and len(v)>1 else default
