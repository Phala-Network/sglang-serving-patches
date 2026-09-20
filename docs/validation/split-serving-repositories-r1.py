"""Repartition frozen serving source without changing runtime bytes; CPU only."""
import ast, difflib, hashlib, json, re, subprocess, tarfile
from pathlib import Path
ROOT=Path("/var/volatile/dstack/persistent/pig-sglang-native-qos-20260915")
INPUT=ROOT/"split-serving-input-r1"
OUT=ROOT/"split-serving-output-r1"
OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((INPUT/"release-manifest.json").read_text())
assert manifest["upstream"]=="94602c9c2b7cbdb8efd5c52802dac6a1c180089e"
assert sha((INPUT/"upstream-preimages.tar").read_bytes())=="769548241d9a4046b840c7b6a49672ad3064a0c512d02313dd3f1c8d6f6eb1d6"
original={}
with tarfile.open(INPUT/"upstream-preimages.tar") as tar:
    for m in tar:
        assert m.isfile() and m.name in manifest["reproduced_files"]
        original[m.name]=tar.extractfile(m).read().decode().replace("\r\n","\n")
def materialize(name, tree):
    path=OUT/name;path.mkdir()
    for rel,data in tree.items():
        dst=path/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(data)
    return path
fullpath=materialize("historical",original)
for entry in manifest["patches"]:
    patch=INPUT/entry["name"]
    assert sha(patch.read_bytes())==entry["sha256"]
    for args in (["--check"],[]):
        subprocess.run(["git","apply",*args,str(patch)],cwd=fullpath,check=True,capture_output=True)
full={p.relative_to(fullpath).as_posix():p.read_text() for p in fullpath.rglob("*") if p.is_file()}
assert {k:sha(v.encode()) for k,v in full.items()}==manifest["reproduced_files"]
def hunks(name):
    file=None;entries=[];cur=None
    for line in (INPUT/name).read_text().splitlines(True):
        if line.startswith("+++ "): file=line[6:].strip()
        elif line.startswith("@@ "):
            cur={"file":file,"old_start":int(re.match(r"@@ -(\d+)",line)[1]),"lines":[]};entries.append(cur)
        elif cur is not None and line[:1] in (" ","+","-") and not line.startswith(("--- ","+++ ")):
            cur["lines"].append(line)
        elif line.startswith(("diff --git ","--- ")):cur=None
    return entries
def replace(tree,file,before,after):
    assert tree[file].count(before)==1,(file,"anchor matches",tree[file].count(before),before[:150])
    tree[file]=tree[file].replace(before,after,1)
def reverse(tree,h):
    before="".join(l[1:] for l in h["lines"] if l[0] in " -")
    after="".join(l[1:] for l in h["lines"] if l[0] in " +")
    replace(tree,h["file"],after,before)
    if h["old_start"]==0:
        assert not tree[h["file"]]
        del tree[h["file"]]
P="python/sglang/srt/"
no_governor=dict(full)
h1=hunks("0001-governor-hooks.patch")
for h in reversed(h1):
    if h["file"]==P+"entrypoints/http_server.py" or (h["file"]==P+"managers/scheduler.py" and h["old_start"] in (466,1340,3649,4622,5013,5883)):
        reverse(no_governor,h)
replace(no_governor,P+"managers/io_struct.py",
'    # Numeric knobs or a namespaced extension payload; scheduler validates keys.\n    server_args: Dict[str, Union[int, float, Dict[str, Any]]]\n',
'    # Only numeric scheduler knobs are accepted (see Scheduler.set_internal_state).\n    server_args: Dict[str, Union[int, float]]\n')
branch='''        if set(server_args_dict) == {"pig_governor"} and self.governor is not None:
            from pig_governor.admin import execute

            try:
                execute(self.governor.core, "patch", time.monotonic(), server_args_dict["pig_governor"])
                return SetInternalStateReqOutput(updated=True, control_nonce=recv_req.control_nonce)
            except ValueError:
                return SetInternalStateReqOutput(updated=False, control_nonce=recv_req.control_nonce)
'''
replace(no_governor,P+"managers/scheduler.py",branch,"")
assert not any("pig_governor" in v or "PIG_GOVERNOR_ENABLE" in v for v in no_governor.values())
h7=hunks("0007-qwen-serving-compatibility.patch")
coder_files={P+"function_call/qwen3_coder_detector.py",
"test/registered/unit/function_call/test_qwen_xml_empty_required_schema.py",
"test/registered/unit/function_call/test_qwen3_coder_parallel_structural_tag.py",
"test/registered/unit/function_call/test_qwen3_coder_schema_coercion.py"}
qwen35=dict(no_governor)
for h in reversed(h7):
    if h["file"] in coder_files: reverse(qwen35,h)
common=dict(qwen35)
chat=P+"entrypoints/openai/serving_chat.py"
for h in reversed(h7):
    if (h["file"]==chat and h["old_start"] in (112,1128,1179,1510)) or (h["file"]=="test/registered/unit/entrypoints/openai/test_serving_chat.py" and h["old_start"]==562):
        reverse(common,h)
# Mixed hunk: retain generic allowed-tool helpers; move only Qwen methods.
a=common[chat].index("    def _uses_qwen35_chat_template(")
b=common[chat].index("    def _prepare_kimi_k3_messages(",a)
common[chat]=common[chat][:a]+common[chat][b:]
calls='''        messages = self._fold_qwen35_system_messages(messages)
        messages = self._apply_qwen35_reasoning_effort_guidance(
            messages, request.reasoning_effort
        )
        self._expose_qwen35_reasoning_tool_history(messages)
'''
replace(common,chat,calls,"")
assert "_QWEN35_" not in common[chat] and "_qwen35_" not in common[chat]
stages=[("common",common),("qwen3_5",qwen35),("qwen3_coder",no_governor),("governor",full)]
paths={
"common":"serving/patches/sglang/v0.5.20/common/0001-serving.patch",
"qwen3_5":"serving/patches/sglang/v0.5.20/models/qwen3_5/0001-template-compatibility.patch",
"qwen3_coder":"serving/patches/sglang/v0.5.20/models/qwen3_coder/0001-parser-compatibility.patch",
"governor":"governor/patches/sglang/v0.5.20/0001-governor-hooks.patch"}
previous=original;records=[]
for name,tree in stages:
    delta=[]
    for rel in sorted(set(previous)|set(tree)):
        if previous.get(rel)==tree.get(rel):continue
        delta+=difflib.unified_diff(previous.get(rel,"").splitlines(True),tree.get(rel,"").splitlines(True),
             fromfile="a/"+rel if rel in previous else "/dev/null",tofile="b/"+rel if rel in tree else "/dev/null")
    patch=OUT/paths[name];patch.parent.mkdir(parents=True,exist_ok=True);patch.write_text("".join(delta))
    records.append({"group":name,"path":paths[name],"sha256":sha(patch.read_bytes()),
                    "changed_files":[k for k in sorted(set(previous)|set(tree)) if previous.get(k)!=tree.get(k)]})
    materialize("stage-"+name,tree)
    for rel,text in tree.items():
        if rel.endswith(".py"):ast.parse(text,filename=name+"/"+rel)
    previous=tree
# Independently apply emitted patches; model selections and absence of Governor explicit.
combinations={"common":["common"],"qwen3_5":["common","qwen3_5"],
"qwen3_coder":["common","qwen3_coder"],"qwen38_without_governor":["common","qwen3_5","qwen3_coder"],
"qwen38_with_governor":["common","qwen3_5","qwen3_coder","governor"],
"common_with_governor":["common","governor"]}
checks=[]
for name,series in combinations.items():
    dest=materialize("verify-"+name,original)
    for group in series:
        for args in (["--check"],[]):
            result=subprocess.run(["git","apply",*args,str(OUT/paths[group])],cwd=dest,capture_output=True)
            assert result.returncode==0,(name,group,result.stderr.decode())
    actual={p.relative_to(dest).as_posix():p.read_text() for p in dest.rglob("*") if p.is_file()}
    for rel,data in actual.items():
        if rel.endswith(".py"):ast.parse(data,filename=name+"/"+rel)
    if name=="qwen38_with_governor":assert actual==full
    if name=="common":assert actual==common
    if name=="qwen38_without_governor":assert actual==no_governor
    checks.append({"selection":name,"series":series,"files":len(actual),"patch_apply":True,"ast":True,
                   "file_hashes":{k:sha(v.encode()) for k,v in actual.items()}})
record={"schema":"phala.split-serving-reproduction.v1","passed":True,
"upstream":manifest["upstream"],"historical_governor_commit":"b24dbadb3a8a9a1c701bb8cac12bd7648a0bb157",
"historical_manifest_sha256":sha((INPUT/"release-manifest.json").read_bytes()),
"patches":records,"checks":checks,"reproduced_final_files":len(full),
"scope":"Patch reapplication, exact historical final bytes and Python AST only; execution/regression/image gates pending"}
(OUT/"reproduction.json").write_text(json.dumps(record,indent=2)+"\n")
archive=ROOT/"split-serving-output-r1.tgz"
with tarfile.open(archive,"x:gz") as tar:
    for group,path in paths.items():tar.add(OUT/path,arcname=path)
    tar.add(OUT/"reproduction.json",arcname="reproduction.json")
print(json.dumps({"passed":True,"archive":str(archive),"sha256":sha(archive.read_bytes()),"files":len(full)}))
