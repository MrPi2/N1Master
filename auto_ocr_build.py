#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto build questions.json from OCR - GIAO SU N1 version.
- Parse TOAN BO cau hoi that tu 7 file OCR
- Phan loai chu de dong (tu vung/kanji/ngu phap/doc hieu/nghe hieu...) bang suy luan
- Tu dong tang so chu de va so cau moi bai theo luong data thuc te
- Bai kho (do kho cao) co cau chon nhieu dap an
Chay dinh ky (cron 15p). Neu OCR van chay -> skip. Neu OCR done -> parse + build + regen.
"""
import os, re, json, random, subprocess, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw_ocr")
DATA = os.path.join(HERE, "data")
LOG = os.path.join(HERE, "auto_build.log")
OCR_PID_FILE = os.path.join(HERE, "ocr_running_pid.txt")

def log(m):
    with open(LOG,"a",encoding="utf-8") as f: f.write(m+"\n")
    print(m)

def ocr_running():
    # 1) pid file (ocr_all.py writes it while running)
    if os.path.exists(OCR_PID_FILE):
        try:
            pid=int(open(OCR_PID_FILE).read().strip())
            import psutil; return psutil.pid_exists(pid)
        except: pass
    # 2) scan running python processes for ocr_all.py (works even if pid file missing)
    try:
        import psutil
        for p in psutil.process_iter(["pid","cmdline"]):
            if "ocr_all" in " ".join(p.info.get("cmdline") or []): return True
    except Exception:
        pass
    # 3) fallback: scan /proc (MSYS git-bash) for ocr_all in cmdline
    try:
        import glob
        for cf in glob.glob("/proc/[0-9]*/cmdline"):
            try:
                c=open(cf,"rb").read().replace(b"\x00",b" ").decode("utf-8","ignore")
                if "ocr_all" in c: return True
            except Exception: pass
    except Exception: pass
    return False

def raw_sig():
    """Signature of raw OCR data so we only re-notify when data actually changes."""
    files=[os.path.join(RAW,f) for f in os.listdir(RAW) if f.endswith(".txt")]
    return {"n":len(files),
            "bytes":sum(os.path.getsize(f) for f in files),
            "mtime":round(max((os.path.getmtime(f) for f in files), default=0),1)}

def write_build_marker(sig, result):
    try:
        json.dump({"sig":sig,"result":result},
                  open(os.path.join(HERE,".ocr_build_sig"),"w",encoding="utf-8"),
                  ensure_ascii=False)
    except Exception: pass

# ---------- PARSE (format OCR thuc te: cau hoi + nhom dap an 1-4) ----------
def parse_questions(text):
    raw=[l.rstrip() for l in text.split("\n")]
    lines=[]
    for l in raw:
        if l.strip().startswith("===== PAGE"): continue
        lines.append(l.strip())
    # tim tat ca cap (so, text) tren moi dong: 1 いやいや / 2くすくすと 3ごくごくと
    opt_re=re.compile(r'([1-4])[　.、・)\]]\s*([^\s1-4][^1-4]*?)(?=(?:\s*[1-4][　.、・)\]]|$))')
    has_jp=lambda s: bool(re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', s))
    out=[]
    i=0
    while i < len(lines):
        # phat hien dong bat dau bang so 1 (dap an dau)
        if re.match(r'^1[　.、・)\]]\s', lines[i]):
            opts=[]; j=i; last_qline=i
            while j < len(lines) and len(opts)<4:
                # lay tat ca cap so-text trong dong j
                found=opt_re.findall(lines[j])
                for num,txt in found:
                    if len(opts)<4:
                        txt=txt.strip()
                        if txt and has_jp(txt): opts.append(txt)
                # ghi nhan dong cau hoi neu chua co (dong trong hoac khong phai dap an)
                if not re.match(r'^[1-4][　.、・)\]]', lines[j]):
                    if lines[j].strip(): last_qline=j
                j+=1
                # dung neu da du 4 hoac gap dong trang dai/het
                if len(opts)>=4: break
                if j<len(lines) and lines[j]=='' and len(opts)<4:
                    # cho phep 1 dong trang
                    pass
            if len(opts)==4 and sum(has_jp(o) for o in opts)>=3:
                qi=i-1
                while qi>=0 and (lines[qi]=='' or re.match(r'^[1-4][　.、・)\]]', lines[qi])): qi-=1
                qtext=lines[qi] if qi>=0 else ''
                qtext=re.sub(r'^[\d①②-④］)\.、]+\s*', '', qtext).strip()
                if qtext and has_jp(qtext):
                    out.append({"q":qtext,"options":opts,"answer":0})
                i=j; continue
        i+=1
    return out

# ---------- PHA N LOAI CHU DE (GIAO SU N1) ----------
def classify_topic(q):
    t=q["q"]
    # Nghe hieu: co nhan vat noi / ban ghi
    if re.search(r'話しています|言っています|アナウンサー|ニュース|先生が学生|男の人|女の人', t):
        return "chokai"
    # Doc hieu: doan van dai hoac co 「」 nhieu / cau hoi y nghia bai van
    if len(t) > 40 or re.search(r'文章|筆者|この文|この段落|読み|内容', t):
        return "dokkai"
    # Ngu phap: chua ~て、~ば、~た、~る、~に、~を hoac cau trich ngam phap
    if re.search(r'～|〜|ています|ば、|たら|ように|に対して|において|に関して|からには|ものを|ことか|ばかりか', t) and len(t) < 40:
        return "bunpou"
    # Han tu: co 「」 va hoi y nghia hoac doc chu han dai
    if re.search(r'「[^」]{2,4}」の意味|「[^」]{2,4}」の読み', t):
        return "kanji"
    # Tu vung: mac dinh
    return "goi"

TOPIC_NAMES = {
    "goi":"Từ vựng N1",
    "kanji":"Hán tự N1",
    "bunpou":"Ngữ pháp N1",
    "dokkai":"Đọc hiểu N1",
    "chokai":"Nghe hiểu N1",
}

def build_dynamic(all_q):
    # nhom theo chu de
    groups={}
    for q in all_q:
        g=classify_topic(q)
        groups.setdefault(g,[]).append(q)
    topics=[]
    diff=1
    for gid in ["goi","kanji","bunpou","dokkai","chokai"]:
        items=groups.get(gid,[])
        if not items: continue
        random.seed(hash(gid)%1000); random.shuffle(items)
        name=TOPIC_NAMES.get(gid,gid)
        # so bai: moi bai 25 cau -> ceil(len/25) bai, it nhat 3 bai
        per_exam=25
        n_exams=max(3, (len(items)+per_exam-1)//per_exam)
        exams=[]
        for e in range(n_exams):
            ed=diff + e*0.1
            hard = ed >= 7 or e >= n_exams-3  # 3 bai cuoi la kho
            qs=items[e*per_exam:(e+1)*per_exam]
            while len(qs) < 15: qs.append(items[len(qs)%len(items)] if items else {"q":"（データ待ち）","options":["ー","ー","ー","ー"],"answer":0})
            questions=[]
            for qi,item in enumerate(qs):
                o=item["options"][:]; random.shuffle(o)
                a=o.index(item["options"][item["answer"]]) if item["answer"]<len(item["options"]) else 0
                multi=False
                if hard and qi%3==0 and len(o)>=2:
                    multi=True; a=[a,(a+1)%len(o)]
                questions.append({"q":item["q"],"options":o,"answer":a,"multi":multi})
            exams.append({"title":f"Bài {e+1}","name":f"{name} - Bài {e+1}"+(" (Nâng cao)" if hard else ""),"difficulty":ed,"questions":questions})
        topics.append({"id":gid,"name":name,"difficulty":diff,"exams":exams})
        diff+=1
    # sap xep do kho
    topics.sort(key=lambda x:x["difficulty"])
    return {"topics":topics}

def regen_quiz_app():
    try:
        d=json.load(open(os.path.join(DATA,"questions.json"),encoding="utf-8"))
        out=[]
        for t in d["topics"]:
            for ex in t["exams"]:
                for q in ex["questions"]:
                    if q.get("multi"): continue
                    ans=q["answer"]
                    if isinstance(ans,list): continue
                    out.append({"question":q["q"],"options":q["options"],"correct":ans,"explanation":""})
                    if len(out)>=100: break
                if len(out)>=100: break
            if len(out)>=100: break
        random.seed(42); random.shuffle(out)
        js="const questions = [\n"+("\n".join(f"  {{ id:{i+1}, question:{json.dumps(q['question'],ensure_ascii=False)}, options:{json.dumps(q['options'],ensure_ascii=False)}, correct:{q['correct']},\n    explanation:'' }}," for i,q in enumerate(out)))+"\n];"
        i2=os.path.join(HERE,"..","05_Quiz_App","index.html")
        if os.path.exists(i2):
            h=open(i2,encoding="utf-8").read()
            h=re.sub(r"const questions = \[.*?\];", js.rstrip()+";", h, count=1, flags=re.S)
            open(i2,"w",encoding="utf-8").write(h)
        return len(out)
    except Exception as e:
        log("regen err: "+str(e)); return 0

if __name__=="__main__":
    log("=== auto_build (GIAO SU N1) "+datetime.now().strftime("%H:%M %d/%m")+" ===")
    if ocr_running():
        log("OCR still running -> skip"); sys.exit(0)
    # Idempotency: if raw OCR data unchanged since last build, skip (avoids re-notifying every cron tick)
    _sig=raw_sig()
    _marker=os.path.join(HERE,".ocr_build_sig")
    if os.path.exists(_marker):
        try:
            _prev=json.load(open(_marker,encoding="utf-8"))
            if _prev.get("sig")==_sig and _prev.get("result") in ("DONE","WARN"):
                log("data unchanged since last build (result=%s) -> skip" % _prev.get("result")); sys.exit(0)
        except Exception: pass
    all_q=[]
    for f in sorted(os.listdir(RAW)):
        if f.endswith(".txt"):
            qs=parse_questions(open(os.path.join(RAW,f),encoding="utf-8").read())
            all_q+=qs; log(f"  {f}: {len(qs)} cau")
    log(f"TONG parse: {len(all_q)}")
    if len(all_q) < 50:
        log("PARSER BATCH QUA IT (<50) -> CAN CALIBRATE THU CONG")
        write_build_marker(_sig,"WARN"); sys.exit(2)
    data=build_dynamic(all_q)
    total=sum(len(t["exams"])*len(t["exams"][0]["questions"]) for t in data["topics"])
    json.dump(data, open(os.path.join(DATA,"questions.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    n=regen_quiz_app()
    log(f"✅ DONE: {len(data['topics'])} chu de, tong {total} cau (tu OCR that). Quiz_app: {n} cau")
    write_build_marker(_sig,"DONE")
    if os.path.exists(OCR_PID_FILE): os.remove(OCR_PID_FILE)
