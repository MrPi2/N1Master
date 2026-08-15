import json, re
d=json.load(open(r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/data/questions.json",encoding="utf-8"))
vn=re.compile(r"[àáảãạăâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]")
bad=0; total=0
for t in d["topics"]:
    for ex in t["exams"]:
        for blk in ex["questions"]:
            qs=blk["questions"] if blk.get("type") else [blk]
            for q in qs:
                total+=1
                for f in [q["q"],q.get("explain","")]+q["options"]:
                    if vn.search(str(f)): bad+=1
print("Viet leak:",bad,"| Tong cau flat:",total,"| Chu de:",len(d["topics"]))
