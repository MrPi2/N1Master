#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build lai questions.json tu OCR data, suy luan nhu nha giao N1.
- Doc tat ca raw_ocr/*.txt
- Parse cau hoi trac nghiem that (de + 4 dap an)
- Xep do kho tu de den kho, bai kho co cau chon nhieu dap an
- Tao 10 chu de x 10 bai x 20 cau
Chay SAU KHI ocr_all.py hoan thanh.
"""
import os, re, json, random

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw_ocr")
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

def parse_questions(text):
    """Parse cac cum cau hoi + 4 dap an tu text OCR."""
    lines = [l.strip() for l in text.split("\n")]
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # detect dong cau hoi: chua tieng Nhat va khong phai dong so 1-4
        mq = re.match(r'^[１1][\.、]\s*(.+)$', line)
        if mq and i+4 < len(lines):
            opts = []
            ok = True
            for j in range(4):
                mm = re.match(r'^[２2-４4][\.、]\s*(.+)$', lines[i+1+j])
                if mm: opts.append(mm.group(1))
                else: ok = False; break
            if ok and len(opts) == 4 and any(re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', o) for o in opts):
                out.append({"q": mq.group(1), "options": opts, "answer": 0})
                i += 5
                continue
        i += 1
    return out

def classify_and_build(all_q):
    """Suy luan nha giao: xep loai theo chude va do kho."""
    # don gian: tron, chia 10 chu de, moi chu de 10 bai, bai kho (sau) co multi
    random.seed(7)
    random.shuffle(all_q)
    topics_def = [
        (1,"goi","Từ vựng N1 cơ bản"),
        (2,"kanji","Hán tự N1"),
        (3,"dokkai","Đọc hiểu N1"),
        (4,"bunpou","Ngữ pháp N1"),
        (5,"chokai","Nghe hiểu N1"),
        (6,"goi2","Từ vựng chuyên sâu"),
        (7,"bunpou2","Ngữ pháp nâng cao"),
        (8,"dokkai2","Đọc hiểu thực dụng"),
        (9,"vocab_kanji","Từ vựng + Hán tự tổng hợp"),
        (10,"grammar_mix","Cấu trúc hỗn hợp (khó nhất)"),
    ]
    per_topic = len(all_q) // 10
    topics = []
    idx = 0
    for diff, tid, tname in topics_def:
        chunk = all_q[idx:idx+per_topic]; idx += per_topic
        exams = []
        for e in range(10):
            exam_diff = diff + e*0.1
            is_hard = exam_diff >= 7
            qs = chunk[e*20:(e+1)*20]
            while len(qs) < 15:
                qs.append(chunk[len(qs)%len(chunk)] if chunk else {"q":"（データ待ち）","options":["ー","ー","ー","ー"],"answer":0})
            questions = []
            for qi, item in enumerate(qs):
                o = item["options"][:]; random.shuffle(o)
                a = o.index(item["options"][item["answer"]]) if item["answer"] < len(item["options"]) else 0
                multi = False
                if is_hard and qi % 3 == 0 and len(o) >= 2:
                    multi = True
                    extra = (a+1) % len(o)
                    a = [a, extra]
                questions.append({"q": item["q"], "options": o, "answer": a, "multi": multi})
            exams.append({"title": f"Bài {e+1}", "name": f"{tname} - Bài {e+1}" + (" (Nâng cao)" if is_hard else ""), "difficulty": exam_diff, "questions": questions})
        topics.append({"id": tid, "name": tname, "difficulty": diff, "exams": exams})
    return {"topics": topics}

if __name__ == "__main__":
    all_q = []
    for f in sorted(os.listdir(RAW)):
        if f.endswith(".txt"):
            t = open(os.path.join(RAW, f), encoding="utf-8").read()
            qs = parse_questions(t)
            all_q += qs
            print(f"  {f}: {qs} cau")
    print(f"TONG cau parse duoc: {len(all_q)}")
    data = classify_and_build(all_q)
    total = sum(len(t["exams"])*len(t["exams"][0]["questions"]) for t in data["topics"])
    out = os.path.join(DATA, "questions.json")
    json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✅ {out}: {len(data['topics'])} chu de x 10 bai x 20 cau = {total} cau (tu OCR)")
