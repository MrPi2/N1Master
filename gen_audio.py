import json, os, subprocess, asyncio

BASE = os.path.dirname(os.path.abspath(__file__))
q = json.load(open(os.path.join(BASE, "data/questions.json"), encoding="utf-8"))
OUT = os.path.join(BASE, "static", "audio")
os.makedirs(OUT, exist_ok=True)

VOICE = "ja-JP-NanamiNeural"

def flat_questions(ex):
    out = []
    for blk in ex["questions"]:
        if isinstance(blk, dict) and blk.get("type") in ("reading","listening") and "questions" in blk:
            out.extend(blk["questions"])
        elif isinstance(blk, dict) and "q" in blk:
            out.append(blk)
    return out

def synth(text, path):
    cmd = ["edge-tts", "--voice", VOICE, "--text", text, "--write-media", path]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
        return os.path.exists(path) and os.path.getsize(path) > 100
    except Exception as e:
        print("  ERR", e)
        return False

# chỉ 2 khóa nghe hiểu
targets = ["chokai", "chokai_audio"]
total = 0
done = 0
for t in q["topics"]:
    if t["id"] not in targets: continue
    for ei, ex in enumerate(t["exams"]):
        qs = flat_questions(ex)
        for qi, ques in enumerate(qs):
            total += 1
            fname = f"{t['id']}-{ei+1}-{qi+1}.mp3"
            fpath = os.path.join(OUT, fname)
            if os.path.exists(fpath) and os.path.getsize(fpath) > 100:
                done += 1
                continue
            # dùng câu q làm audio (hoặc explain nếu rỗng)
            txt = (ques.get("q") or "").strip()
            # bỏ ký tự không đọc được
            txt = txt.replace("\n"," ").strip()
            if not txt:
                done += 1
                continue
            if synth(txt, fpath):
                done += 1
            if done % 20 == 0:
                print(f"  progress {done}/{total}")

print(f"DONE audio: {done}/{total} files in static/audio")
