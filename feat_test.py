from playwright.sync_api import sync_playwright
import requests, json, glob, os, time

BASE="http://127.0.0.1:5000"; U="feat"
CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
d=json.load(open(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/data/questions.json",encoding="utf-8"))
topic_ids=[t["id"] for t in d["topics"]]

def log(m): print(m)

with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1280,"height":900})
    results=[]

    for tid in topic_ids:
        # mo bai 1 cua chu de
        pg.goto(f"{BASE}/exam/{tid}/0?name={U}")
        pg.wait_for_timeout(500)
        tname=next(t["name"] for t in d["topics"] if t["id"]==tid)
        # --- TEST SPAM: click option dau 5 lan ---
        opts=pg.query_selector_all("#optionsBox .opt-card")
        if opts:
            for _ in range(5): opts[0].click()
            sel=pg.query_selector_all("#optionsBox .opt-card.sel")
            spam_ok = (len(sel)==1)  # chi 1 duoc chon du lam spam
            # verify state.answers[0] la 1 so (khong phai array)
            st=pg.evaluate("JSON.stringify(state.answers[0])")
            spam_val = st
        else:
            spam_ok=False; spam_val="NA"
        # --- TEST CHON NHIEU (neu bai nay co multi) ---
        multi_ok=None
        is_multi=pg.evaluate("QUESTIONS[state.current].multi")
        if is_multi:
            cbs=pg.query_selector_all("#optionsBox input[type=checkbox]")
            cbs[0].click(); cbs[1].click(); cbs[2].click()
            starr=pg.evaluate("JSON.stringify(state.answers[0])")
            multi_ok = (starr.startswith("[") and len(json.loads(starr))==3)
        # --- submit bai nay (chon tat ca dung) ---
        qd=next(t for t in d["topics"] if t["id"]==tid)["exams"][0]["questions"]
        ans={i:(q["answer"] if isinstance(q["answer"],list) else q["answer"]) for i,q in enumerate(qd)}
        requests.post(BASE+"/submit",json={"topic_id":tid,"exam_idx":0,"user_name":U,"answers":ans})
        results.append((tid, tname, spam_ok, spam_val, is_multi, multi_ok))
        log(f"  {tid:12} | spam(1 chon):{spam_ok} val={spam_val} | multi:{is_multi} multi_ok:{multi_ok}")

    # verify topic page shows 10 passed
    pg.goto(f"{BASE}/topic/goi?name={U}"); pg.wait_for_timeout(600)
    em=len(pg.query_selector_all("section#exams article.bg-emerald-500\\/10"))
    log(f"\nTopic goi pass xanh: {em}/10")
    b.close()
    for f in glob.glob(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/results/feat_*"): os.remove(f)
    log("DONE")
