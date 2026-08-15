import re, glob, os, json

RAW=r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/raw_ocr"
OUT=r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/ocr_extracted.json"

files=glob.glob(os.path.join(RAW,"*.txt"))
entries=[]  # (kanji, kana, type, context)
for f in files:
    txt=open(f,encoding='utf-8').read()
    txt=re.sub(r'===== PAGE \d+ =====','\n',txt)
    lines=[l.strip() for l in txt.split("\n") if l.strip()]
    for i,l in enumerate(lines):
        # 1. (kanji)（kana） hoac (kanji)（かな）
        for m in re.finditer(r'([一-鿿]{2,5})[（\(]([ぁ-ヿ]{2,10})[）)]', l):
            entries.append({"k":m.group(1),"r":m.group(2),"t":"word","ctx":l[:60]})
        # 2. tu tieng Nhat + nghia tieng Anh: 期：a once-in-a-lifetime chance
        for m in re.finditer(r'([一-鿿]{2,5})[：:]\s*([A-Za-z][A-Za-z\s]{4,50})', l):
            entries.append({"k":m.group(1),"r":m.group(2).strip(),"t":"en","ctx":l[:60]})
        # 3. dinh dang 「言葉」の使い方 / 〜を引く［意味］
        for m in re.finditer(r'[(［]((?:[ぁ-ヿ一-鿿]{1,6}))[)］]\s*([一-鿿]{2,8})', l):
            entries.append({"k":m.group(2),"r":m.group(1),"t":"def","ctx":l[:60]})
        # 4. cau co （ ） va 4 dap an lien ke
        if '（' in l and '）' in l and re.search(r'[ぁ-ヿ一-鿿]', l):
            entries.append({"k":"","r":"","t":"sentence","ctx":l[:80]})

# loc trung + bo nhieu
seen=set(); clean=[]
for e in entries:
    key=(e["k"],e["r"],e["t"])
    if key in seen: continue
    seen.add(key)
    # bo entry quai (r la tieng Anh dai qua hoac ki tu special)
    if e["t"]=="en" and (len(e["r"].split())>6 or 'xxx' in e["r"].lower() or 'X'*3 in e["r"]): continue
    if e["t"]=="word" and not re.search(r'[ぁ-ヿ]', e["r"]): continue
    clean.append(e)

json.dump(clean, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("Tong entry trich:", len(entries), "| sau loc:", len(clean))
# thong ke
from collections import Counter
c=Counter(e["t"] for e in clean)
print("Phan loai:", dict(c))
# in 50 dau
for e in clean[:50]: print(" ", e["t"], "|", e["k"], e["r"], "|", e["ctx"][:30])
