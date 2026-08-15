from playwright.sync_api import sync_playwright
import requests, json, glob, os

BASE="http://127.0.0.1:5000"; U="full120"
CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
d=json.load(open(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/data/questions.json",encoding="utf-8"))

def flatten(ex):
    flat=[]
    for blk in ex["questions"]:
        if blk.get("type") in ("reading","listening"):
            for q in blk["questions"]: flat.append(q)
        else: flat.append(blk)
    return flat

errors=[]; done=0
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1280,"height":900})
    for t in d["topics"]:
        tid=t["id"]
        for ei in range(len(t["exams"])):
            ex=t["exams"][ei]; flat=flatten(ex)
            ans={i:(q["answer"] if isinstance(q["answer"],list) else q["answer"]) for i,q in enumerate(flat)}
            try:
                r=requests.post(BASE+"/submit",json={"topic_id":tid,"exam_idx":ei,"user_name":U,"answers":ans},timeout=10)
                j=r.json()
                if r.status_code!=200: errors.append(f"{tid}/{ei}: HTTP{r.status_code}")
                if abs(j.get("score",0)-100)>0.01: errors.append(f"{tid}/{ei}: score{j.get('score')}")
            except Exception as e: errors.append(f"{tid}/{ei}: {str(e)[:30]}"); continue
            try:
                pg.goto(f"{BASE}/result/{tid}/{ei}?name={U}",wait_until="domcontentloaded"); pg.wait_for_timeout(80)
                if "renderReview" not in pg.content(): errors.append(f"{tid}/{ei}: thieu review")
            except Exception as e: errors.append(f"{tid}/{ei}: res {str(e)[:30]}")
            done+=1
    # topic pass check
    for t in d["topics"]:
        pg.goto(f"{BASE}/topic/{t['id']}?name={U}",wait_until="domcontentloaded"); pg.wait_for_timeout(80)
        em=len(pg.query_selector_all("section#exams article.bg-emerald-500\\/10"))
        if em!=len(t["exams"]): errors.append(f"topic {t['id']}: {em}/{len(t['exams'])} xanh")
    b.close()
    for f in glob.glob(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/results/full120_*"): os.remove(f)
    print(f"=== HOAN THANH {done} bai ===")
    print("LOI:", errors[:25] if errors else "KHONG CO LOI - TAT CA 120 BAI OK!")
    if len(errors)>25: print(f"...+{len(errors)-25} loi khac")
