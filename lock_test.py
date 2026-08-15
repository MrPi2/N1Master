import requests
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8080'
# 1) topic page: bai 1 co 5% (chua pass) -> bai 2..10 locked
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':420,'height':900})
    pg.goto(f'{BASE}/topic/goi', wait_until='networkidle'); pg.wait_for_timeout(700)
    cards=pg.query_selector_all('#exams article')
    txt=[c.inner_text() for c in cards]
    locked=[ 'Da kho' in t or 'khoá' in t.lower() or '🔒' in t for t in txt]
    print('SO BAI:', len(cards))
    print('Bai1:', txt[0].split(chr(10))[0], '| khoa?', locked[0])
    print('Bai2:', '🔒' in txt[1], '| khoa?', locked[1])
    print('Bai3 khoa?', locked[2])
    print('So bai bi khoa (2-10):', sum(locked[1:]))
    # 2) truy cap truc tiep exam goi/3 -> bi redirect ve topic
    resp=pg.goto(f'{BASE}/exam/goi/3?name=anonymous', wait_until='networkidle')
    print('Truy cap /exam/goi/3 truc tiep -> url:', pg.url, '| co khoa?', '🔒' in pg.inner_text('#exams'))
    pg.screenshot(path='lock_list.png')
    b.close()
print('DONE')
