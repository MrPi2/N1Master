from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe', args=['--no-sandbox'])
    pg=b.new_page()
    pg.goto('http://127.0.0.1:5000/exam/goi/0?name=dbg2')
    pg.wait_for_timeout(700)
    opts=pg.query_selector_all('#optionsBox .opt-card')
    radios=pg.query_selector_all('#optionsBox input[type=radio]')
    print('so option:', len(opts), '| so radio:', len(radios))

    letters=['A','B','C','D']
    for click_idx in range(4):
        opts[click_idx].click()
        pg.wait_for_timeout(150)
        # doc mau cua tung label (sel?) va tung radio bg
        status=[]
        for i,el in enumerate(opts):
            cls=el.get_attribute('class') or ''
            sel = 'sel' in cls
            bg = radios[i].evaluate('e=>getComputedStyle(e).backgroundColor')
            status.append(f'{letters[i]}:sel={sel},radioBG={bg}')
        ans = pg.evaluate('JSON.stringify(state.answers[0])')
        print(f'Sau click {letters[click_idx]}: ' + ' | '.join(status) + f' || answers[0]={ans}')
    b.close()
