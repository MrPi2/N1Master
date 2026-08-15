from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1000,'height':900})
    errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:8080/admin?pin=n1admin', wait_until='networkidle'); pg.wait_for_timeout(800)
    print('JS errors:', errs)
    rows=pg.query_selector_all('#rows tr')
    print('So dong bang:', len(rows))
    if rows:
        print('Dong dau:', rows[0].inner_text().replace(chr(10),' | '))
    # mo chi tiet lan 1
    pg.click('text=Xem chi tiết'); pg.wait_for_timeout(500)
    modal=pg.inner_text('#modalBody')
    print('Modal co cau 1:', '1.' in modal)
    print('Modal co Chon/Dap an:', 'Chọn' in modal and 'Đáp án' in modal)
    pg.screenshot(path='admin_view.png')
    b.close()
print('DONE')
