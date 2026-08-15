from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':420,'height':900})
    # 1) / chua nhap -> bam Vao hoc -> bao loi
    pg.goto('http://127.0.0.1:8080/', wait_until='networkidle'); pg.wait_for_timeout(500)
    pg.click('#enterBtn'); pg.wait_for_timeout(200)
    print('[1] khong nhap ma bam -> url van /:', pg.url.split('8080')[-1], '| err hien:', 'hidden' not in pg.eval_on_selector('#err','e=>e.className'))
    # 2) nhap ten -> vao home
    pg.fill('#uname','Hoa'); pg.click('#enterBtn'); pg.wait_for_timeout(700)
    print('[2] sau nhap Hoa -> url:', pg.url.split('8080')[-1])
    print('[2] home co danh sach chu de:', len(pg.query_selector_all('#topics article')), 'bai')
    print('[2] loi chao:', pg.inner_text('#hello'))
    # 3) click chu de dau -> topic co name
    pg.query_selector_all('#topics article')[0].click(); pg.wait_for_timeout(700)
    print('[3] vao topic url:', pg.url.split('8080')[-1], '(phai co ?name=Hoa)')
    # 4) submit 1 bai voi user Hoa -> kiem tra file results/Hoa_...
    import requests, json
    d=json.load(open('data/questions.json',encoding='utf-8'))
    ex=d['topics'][0]['exams'][0]; flat=[(b['questions'] if b.get('type') else [b]) for b in ex['questions']]
    flat=[q for sub in flat for q in sub]
    ans={str(i):(q['answer'][0] if q.get('multi') else q['answer']) for i,q in enumerate(flat)}
    r=requests.post('http://127.0.0.1:8080/submit',json={'topic_id':'goi','exam_idx':0,'user_name':'Hoa','answers':ans})
    print('[4] submit Hoa score:', r.json()['score'])
    import os
    files=[f for f in os.listdir('results') if f.startswith('Hoa_')]
    print('[4] file results/Hoa_*.json:', files)
    b.close()
print('DONE')
