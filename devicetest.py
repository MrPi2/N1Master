from playwright.sync_api import sync_playwright

def test_device(pg, label, block_cdn=False):
    if block_cdn:
        pg.route('**://cdn.tailwindcss.com/**', lambda r: r.abort())
    # SINGLE goi/0
    pg.goto('http://127.0.0.1:5000/exam/goi/0?name=t_'+label, wait_until='domcontentloaded')
    pg.wait_for_timeout(900)
    errs=pg.evaluate('window.__err||[]')
    opts=pg.query_selector_all('#optionsBox .opt-card')
    cb=pg.query_selector_all('#optionsBox input[type=checkbox]')
    rb=pg.query_selector_all('#optionsBox input[type=radio]')
    print(f'[{label}] SINGLE goi/0: opts={len(opts)} checkbox={len(cb)} radio={len(rb)}')
    if opts:
        for i in range(4):
            opts[i].click(); pg.wait_for_timeout(100)
            s=['sel' in o.get_attribute('class') for o in opts]
            if sum(s)!=1: print(f'  [{label}] LOI: click {chr(65+i)} co {sum(s)} sel: {s}')
        print(f'  [{label}] SINGLE chon lan luot OK (chi 1 vang)')
    # MULTI grammar_mix/0
    pg.goto('http://127.0.0.1:5000/exam/grammar_mix/0?name=t_'+label, wait_until='domcontentloaded')
    pg.wait_for_timeout(900)
    opts=pg.query_selector_all('#optionsBox .opt-card')
    cb=pg.query_selector_all('#optionsBox input[type=checkbox]')
    rb=pg.query_selector_all('#optionsBox input[type=radio]')
    print(f'[{label}] MULTI grammar_mix/0: opts={len(opts)} checkbox={len(cb)} radio={len(rb)}')
    if cb:
        cb[0].click(); cb[1].click()
        a=pg.evaluate('JSON.stringify(state.answers[0])')
        print(f'  [{label}] MULTI chon 2 -> answers[0]={a}')

with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe', args=['--no-sandbox'])
    # PC
    pg=b.new_page(viewport={'width':1280,'height':900})
    pg.on('pageerror', lambda e: print('  [PC] PAGEERROR:', str(e)[:60]))
    test_device(pg,'PC')
    # MOBILE
    mp=b.new_page(**p.devices['iPhone 12'])
    mp.on('pageerror', lambda e: print('  [MOBILE] PAGEERROR:', str(e)[:60]))
    test_device(mp,'MOBILE')
    b.close()
print('=== DONE ===')
