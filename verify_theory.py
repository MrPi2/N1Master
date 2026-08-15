import json, re
d=json.load(open(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/data/questions.json",encoding="utf-8"))
vn=re.compile(r"[àáảãạăâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]")
bad=0; sample=[]
for t in d["topics"]:
    for ex in t["exams"]:
        for q in ex["questions"]:
            for field in [q["q"],q["explain"]]+q["options"]:
                if vn.search(str(field)):
                    bad+=1
                    if len(sample)<5: sample.append(str(field)[:40])
print("Tieng Viet leak:", bad, sample)
err=0
for t in d["topics"]:
    for ex in t["exams"]:
        for q in ex["questions"]:
            a=q["answer"]
            if isinstance(a,list):
                if any(x>=len(q["options"]) or x<0 for x in a): err+=1
            else:
                if a>=len(q["options"]) or a<0: err+=1
print("Answer index errors:", err)
q=d["topics"][0]["exams"][0]["questions"][0]
print("\nSample Q:", q["q"][:90])
print("Opts:", q["options"])
print("Answer idx:", q["answer"], "| Explain:", q["explain"][:80])
