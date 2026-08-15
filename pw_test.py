import time, json, requests
from playwright.sync_api import sync_playwright

BASE="http://127.0.0.1:5000"
U="pwtest"
CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
d=json.load(open(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/data/questions.json",encoding="utf-8"))
topic=next(t for t in d["topics"] if t["id"]=="goi")

def log(m): print(m)

with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1280,"height":900})
    # 1. Topic page - submit all 10 via API first, then check UI render
    for ei,ex in enumerate(topic["exams"]):
        ans={i:(q["answer"] if isinstance(q["answer"],list) else q["answer"]) for i,q in enumerate(ex["questions"])}
        requests.post(BASE+"/submit",json={"topic_id":"goi","exam_idx":ei,"user_name":U,"answers":ans})
    time.sleep(0.5)
    pg.goto(f"{BASE}/topic/goi?name={U}")
    pg.wait_for_timeout(800)
    cards=pg.query_selector_all("section#exams article")
    emerald=pg.query_selector_all("section#exams article.bg-emerald-500\\/10")
    log(f"Topic: {len(cards)} cards, {len(emerald)} emerald(pass)")
    # 2. Open a MULTI exam (grammar_mix/0 diff=10 >=7 -> multi from bai 1)
    pg.goto(f"{BASE}/exam/grammar_mix/0?name={U}")
    pg.wait_for_timeout(800)
    inputs=pg.query_selector_all("#optionsBox input")
    types=[i.get_attribute("type") for i in inputs]
    cb=[i for i in inputs if i.get_attribute("type")=="checkbox"]
    log(f"Exam grammar_mix/0: {len(inputs)} inputs, checkbox={len(cb)}, radio={types.count('radio')}")
    # verify square shape via computed style of first checkbox
    if cb:
        sty=cb[0].evaluate("el=>getComputedStyle(el).borderRadius")
        log(f"Checkbox border-radius (square=0px): {sty}")
    # select 2 options in multi
    if cb:
        cb[0].click(); cb[1].click()
        sel=pg.query_selector_all("#optionsBox .opt-card.sel")
        log(f"After click 2: {len(sel)} cards selected")
    # 3. Submit -> result page (grammar_mix/0 dang o cau 1, goi requestSubmit())
    pg.evaluate("requestSubmit()")
    pg.wait_for_timeout(400)
    # confirm modal
    pg.wait_for_selector("#confirmModal:not(.hidden)", timeout=5000)
    pg.click("#confirmModal button:has-text('Nộp bài')")
    pg.wait_for_timeout(1200)
    log(f"After submit URL: {pg.url}")
    has_review = pg.query_selector("button:has-text('Xem lại bài thi')") is not None
    log(f"Result has 'Xem lại' button: {has_review}")
    # click xem lai
    if has_review:
        pg.click("button:has-text('Xem lại bài thi')")
        pg.wait_for_timeout(600)
        rev=pg.query_selector_all("#reviewBox article")
        log(f"Review articles rendered: {len(rev)}")
    b.close()
log("DONE")
