import json, requests, os, glob
BASE="http://127.0.0.1:5000"
UNAME="selftest"
d=json.load(open(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/data/questions.json",encoding="utf-8"))
topic=next(t for t in d["topics"] if t["id"]=="goi")
print("Chu de:", topic["name"], "| so bai:", len(topic["exams"]))
errors=[]
for ei,ex in enumerate(topic["exams"]):
    qs=ex["questions"]
    ans={}
    for i,q in enumerate(qs):
        a=q["answer"]
        ans[i]=a if isinstance(a,list) else a
    r=requests.post(BASE+"/submit",json={"topic_id":"goi","exam_idx":ei,"user_name":UNAME,"answers":ans})
    j=r.json()
    if r.status_code!=200: errors.append(f"Bai {ei+1}: HTTP {r.status_code}")
    if abs(j.get("score",0)-100)>0.01: errors.append(f"Bai {ei+1}: score={j.get('score')}")
    rr=requests.get(f"{BASE}/result/goi/{ei}?name={UNAME}")
    if rr.status_code!=200: errors.append(f"Bai {ei+1}: result HTTP {rr.status_code}")
    if "renderReview" not in rr.text: errors.append(f"Bai {ei+1}: thieu review")
    print(f"  Bai {ei+1}: score={j['score']}% | result {rr.status_code}")
tt=requests.get(f"{BASE}/topic/goi?name={UNAME}").text
emerald=tt.count("emerald")
print(f"Topic: o emerald (pass) = {emerald}/10")
if emerald<10: errors.append(f"Chi {emerald}/10 pass xanh")
for f in glob.glob(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/results/selftest_*"):
    os.remove(f)
print("\n=== KET QUA ===")
print("LOI:", errors if errors else "KHONG CO LOI - tat ca tinh nang hoat dong!")
