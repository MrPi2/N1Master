from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',args=['--no-sandbox'])
    # TEST A: reload giu vi tri
    pg=b.new_page(viewport={'width':420,'height':900})
    pg.goto('http://127.0.0.1:8080/exam/goi/0?name=qaA', wait_until='networkidle'); pg.wait_for_timeout(400)
    pg.evaluate('next();next();'); pg.wait_for_timeout(200)
    print('[A] truoc reload cau:', pg.evaluate('state.current+1'))
    pg.reload(wait_until='networkidle'); pg.wait_for_timeout(500)
    print('[A] sau reload cau:', pg.evaluate('state.current+1'), '(mong 3)')
    # TEST B: het gio ep nop + khoa
    pg2=b.new_page(viewport={'width':420,'height':900})
    pg2.goto('http://127.0.0.1:8080/exam/goi/0?name=qaB', wait_until='networkidle'); pg2.wait_for_timeout(400)
    pg2.evaluate('state.timeLeft=1;')
    pg2.wait_for_timeout(2600)
    print('[B] sau het gio url:', pg2.url.split('8080')[-1], '(mong /result/...)')
    # quay lai trang thi de check finished/locked
    pg3=b.new_page(viewport={'width':420,'height':900})
    pg3.goto('http://127.0.0.1:8080/exam/goi/0?name=qaB', wait_until='networkidle'); pg3.wait_for_timeout(400)
    # ghi nhan finished tu localStorage time bi xoa -> finished true nghia la da nop
    print('[B] TIME_KEY con ton tai?', pg3.evaluate('localStorage.getItem("n1_time_qaB_goi_0")') is None)
    b.close()
print('DONE')
