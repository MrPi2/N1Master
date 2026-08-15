import re, glob, os, json
RAW=r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/raw_ocr"
OUT=r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/ocr_bank.json"
files=glob.glob(os.path.join(RAW,"*.txt"))
entries=set()
for f in files:
    txt=open(f,encoding='utf-8').read()
    txt=re.sub(r'===== PAGE \d+ =====','',txt)
    for m in re.finditer(r'([一-鿿]{2,4})[（\(]([ぁ-ヿ]{2,8})[）)]', txt):
        entries.add((m.group(1), m.group(2)))
    for m in re.finditer(r'\n([一-鿿]{2,4})[：:]\s*([A-Za-z][A-Za-z\s]{3,40})', txt):
        entries.add((m.group(1), m.group(2).strip()))
clean=[list(e) for e in entries if 2<=len(e[0])<=4 and 2<=len(e[1])<=10]
print("Tong cap trich:", len(entries), "| sau loc:", len(clean))
json.dump(clean, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
for e in clean[:30]: print(" ", e[0], e[1])
