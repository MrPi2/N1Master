import json, os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))

def norm(s):
    return (s or "").strip()

# ============ 1. QUESTIONS.JSON (phần thi) ============
print("="*60)
print("PHẦN THI — questions.json")
print("="*60)
q = json.load(open(os.path.join(BASE,"data/questions.json"), encoding="utf-8"))

# flatten all questions with location
all_q = []  # (topic_id, exam_idx, q_idx, q_text, options, answer)
for t in q["topics"]:
    for ei, ex in enumerate(t["exams"]):
        for blk in ex["questions"]:
            items = blk["questions"] if isinstance(blk,dict) and "questions" in blk else [blk]
            for qi, ques in enumerate(items):
                if not isinstance(ques, dict) or "q" not in ques: continue
                all_q.append((t["id"], ei, qi, norm(ques.get("q")), ques.get("options",[]), ques.get("answer")))

print("Tổng câu hỏi (flat):", len(all_q))

# duplicate by q text
by_text = defaultdict(list)
for r in all_q:
    by_text[r[3]].append(r)
dups = {k:v for k,v in by_text.items() if len(v) > 1}
print("Số câu hỏi BỊ TRÙNG (cùng text q):", len(dups))
for k,v in list(dups.items())[:10]:
    locs = [f"{r[0]}/B{r[1]+1}/C{r[2]+1}" for r in v]
    print(f"  • {k[:40]}...  ×{len(v)}  @ {locs}")

# duplicate within same exam (same topic+exam, different q_idx)
within_exam = defaultdict(list)
for r in all_q:
    within_exam[(r[0], r[1])].append(r[3])
dup_within = {k:[x for x in v if v.count(x)>1] for k,v in within_exam.items()}
dup_within = {k:v for k,v in dup_within.items() if v}
print("Số bài thi có câu trùng NỘI BỘ:", len(dup_within))
for k,v in list(dup_within.items())[:5]:
    print(f"  • {k[0]}/Bài{k[1]+1}: {len(v)} cặp trùng")

# ============ 2. COURSES.JSON (khóa học) ============
print()
print("="*60)
print("KHÓA HỌC — courses.json")
print("="*60)
c = json.load(open(os.path.join(BASE,"data/courses.json"), encoding="utf-8"))
course_q = []  # (course_id, sec_idx, q_text, options, answer)
for co in c["courses"]:
    for si, sec in enumerate(co["sections"]):
        for qi, ques in enumerate(sec.get("quizPreview",[])):
            course_q.append((co["id"], si, norm(ques.get("q")), ques.get("options",[]), ques.get("answer")))

print("Tổng câu quiz khóa học:", len(course_q))
by_ctext = defaultdict(list)
for r in course_q:
    by_ctext[r[2]].append(r)
cdups = {k:v for k,v in by_ctext.items() if len(v)>1}
print("Câu quiz khóa học BỊ TRÙNG:", len(cdups))
for k,v in list(cdups.items())[:10]:
    locs = [f"{r[0]}/S{r[1]+1}" for r in v]
    print(f"  • {k[:40]}...  ×{len(v)}  @ {locs}")

# ============ 3. CROSS: course quiz vs exam ============
print()
print("="*60)
print("CHÉO: câu quiz khóa học trùng với câu thi gốc?")
print("="*60)
exam_texts = set(r[3] for r in all_q)
cross = [r for r in course_q if r[2] in exam_texts]
print("Câu quiz khóa học trùng với thi gốc (expected, vì sinh từ data):", len(cross), "/", len(course_q))
