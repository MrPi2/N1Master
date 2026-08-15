from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':420,'height':900})
    pg.goto('http://127.0.0.1:8080/topic/goi', wait_until='networkidle'); pg.wait_for_timeout(700)
    cards=pg.query_selector_all('#exams article')
    print('so bai:', len(cards))
    c0=cards[0].inner_text()
    print('--- Bai 1 ---')
    print(c0)
    print('Co "Da thi":', 'Da thi' in c0)
    pg.screenshot(path='topic_list.png')
    b.close()
print('DONE')
