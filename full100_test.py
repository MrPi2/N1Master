from playwright.sync_api import sync_playwright
import requests, json, glob, os, time

BASE="http://127.0.0.1:5000"; U="full100"
CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
d=json.load(open(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/data/questions.json",encoding="utf-8"))

errors=[]
done_count=0
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1280,"height":900})
    for t in d["topics"]:
        tid=t["id"]
        for ei in range(len(t["exams"])):
            # submit qua API (chon dung)
            ex=t["exams"][ei]
            ans={i:(q["answer"] if isinstance(q["answer"],list) else q["answer"]) for i,q in enumerate(ex["questions"])}
            try:
                r=requests.post(BASE+"/submit",json={"topic_id":tid,"exam_idx":ei,"user_name":U,"answers":ans},timeout=10)
                j=r.json()
                if r.status_code!=200: errors.append(f"{tid}/{ei}: HTTP {r.status_code}")
                if abs(j.get("score",0)-100)>0.01: errors.append(f"{tid}/{ei}: score {j.get('score')}")
            except Exception as e:
                errors.append(f"{tid}/{ei}: submit err {str(e)[:40]}")
                continue
            # verify result page render qua browser
            try:
                pg.goto(f"{BASE}/result/{tid}/{ei}?name={U}", wait_until="domcontentloaded")
                pg.wait_for_timeout(150)
                if "renderReview" not in pg.content(): errors.append(f"{tid}/{ei}: result thieu review")
            except Exception as e:
                errors.append(f"{tid}/{ei}: result err {str(e)[:40]}")
            done_count+=1
    # verify topic pages all passed
    for t in d["topics"]:
        pg.goto(f"{BASE}/topic/{t['id']}?name={U}", wait_until="domcontentloaded")
        pg.wait_for_timeout(150)
        em=len(pg.query_selector_all("section#exams article.bg-emerald-500\\/10"))
        if em != len(t["exams"]): errors.append(f"topic {t['id']}: chi {em}/{len(t['exams'])} pass xanh")
    b.close()
    for f in glob.glob(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/results/full100_*"): os.remove(f)
    print(f"=== HOAN THANH {done_count} bai ===")
    print("LOI:", errors[:20] if errors else "KHONG CO LOI - TAT CA 100 BAI OK!")
    if len(errors)>20: print(f"...va {len(errors)-20} loi khac")
