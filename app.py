#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Web hoc tap Nhat N1 - Flask app: lam bai trac nghiem, tu cham, luu ket qua."""
import os, json, uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.after_request
def add_no_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

def load_questions():
    p = os.path.join(DATA, "questions.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {"topics": []}

@app.route("/api/topics")
def api_topics():
    q = load_questions()
    return jsonify([{"id": t["id"], "name": t["name"],
                     "difficulty": t.get("difficulty"),
                     "exams": len(t.get("exams", [])),
                     "questions_per_exam": len(t["exams"][0]["questions"]) if t.get("exams") else 0}
                    for t in q.get("topics", [])])

@app.route("/topic/<topic_id>")
def topic_page(topic_id):
    q = load_questions()
    topic = next((t for t in q["topics"] if t["id"] == topic_id), None)
    if not topic: return "Not found", 404
    # trang chu de co the nhan ?name= de hien trang thai; mac dinh anonymous
    uname = request.args.get("name") or "anonymous"
    done = {}  # exam_idx -> best_score
    if uname:
        for f in os.listdir(RESULTS):
            if f.startswith(f"{uname}_{topic_id}_"):
                try:
                    rec = json.load(open(os.path.join(RESULTS, f), encoding="utf-8"))
                    ei = rec["exam"] - 1
                    done[ei] = max(done.get(ei, 0), rec["score"])
                except: pass
    return render_template("topic.html", topic=topic, uname=uname, done=done)

@app.route("/topics")
def topics_page():
    return render_template("topics.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    pin = request.args.get("pin", "")
    if pin != "n1admin":
        return """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Admin Login</title>
        <script src="https://cdn.tailwindcss.com"></script></head>
        <body class="min-h-screen bg-slate-900 flex items-center justify-center text-slate-100">
        <form method="get" class="bg-slate-800 p-8 rounded-2xl shadow-xl text-center">
          <h1 class="font-bold mb-4">Admin N1Master</h1>
          <input name="pin" placeholder="Ma pin" class="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 mb-3 w-full">
          <button class="w-full py-2 rounded-lg bg-amber-400 text-slate-900 font-bold">Vao</button>
          <p class="text-xs text-slate-500 mt-3">Mac dinh: n1admin</p>
        </form></body></html>"""
    recs=[]
    for f in os.listdir(RESULTS):
        if not f.endswith('.json'): continue
        try:
            d=json.load(open(os.path.join(RESULTS,f),encoding='utf-8'))
            recs.append({'user':d.get('user','?'),'topic':d.get('topic','?'),'topic_id':d.get('topic_id',''),
                         'exam':d.get('exam',0),'score':d.get('score',0),'correct':d.get('correct',0),
                         'total':d.get('total',0),'time':d.get('time',''),'detail':d.get('detail',[])})
        except: pass
    recs.sort(key=lambda x:x['time'],reverse=True)
    return render_template("admin.html", data=recs)

@app.route("/exam/<topic_id>/<int:exam_idx>")
def exam(topic_id, exam_idx):
    q = load_questions()
    topic = next((t for t in q["topics"] if t["id"] == topic_id), None)
    if not topic or exam_idx >= len(topic.get("exams", [])):
        return "Not found", 404
    # kiem tra mo khoa: bai dau tien luon mo; bai sau can bai truoc pass>=80
    if exam_idx > 0:
        uname = request.args.get("name") or "anonymous"
        prev = exam_idx - 1
        best = 0
        for f in os.listdir(RESULTS):
            if f.startswith(f"{uname}_{topic_id}_{prev}_"):
                try:
                    rec = json.load(open(os.path.join(RESULTS, f), encoding="utf-8"))
                    best = max(best, rec["score"])
                except: pass
        if best < 80:
            return redirect(f"/topic/{topic_id}?name={uname}&locked=1")
    ex = topic["exams"][exam_idx]
    return render_template("exam.html", topic=topic, exam=ex, exam_idx=exam_idx)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    topic_id = data.get("topic_id"); exam_idx = data.get("exam_idx")
    answers = data.get("answers", {})  # {qid: choice_idx}
    user_name = data.get("user_name", "anonymous")
    q = load_questions()
    topic = next((t for t in q["topics"] if t["id"] == topic_id), None)
    if not topic: return jsonify({"error": "topic not found"}), 404
    ex = topic["exams"][exam_idx]
    # flatten tat ca cau hoi tu blocks (reading/listening co block lồng)
    flat = []
    for blk in ex["questions"]:
        if blk.get("type") in ("reading","listening"):
            for qi, sub in enumerate(blk["questions"]):
                flat.append(sub)
        else:
            flat.append(blk)
    total = len(flat); correct = 0; detail = []
    for i, ques in enumerate(flat):
        qid = str(i)
        chosen = answers.get(qid, -1)
        right = ques.get("answer", -1)
        multi = ques.get("multi", False)
        if multi:
            if not isinstance(chosen, list): chosen = [chosen] if chosen >= 0 else []
            if not isinstance(right, list): right = [right]
            ok = set(chosen) == set(right)
            chosen_disp = chosen
        else:
            ok = (chosen == right)
            chosen_disp = chosen
        if ok: correct += 1
        detail.append({"q": ques["q"], "chosen": chosen_disp, "right": right,
                       "ok": ok, "options": ques["options"], "multi": multi})
    score = round(correct/total*100, 1)
    rec = {"user": user_name, "topic": topic["name"], "topic_id": topic_id, "exam": exam_idx+1,
           "score": score, "correct": correct, "total": total,
           "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "detail": detail}
    fn = os.path.join(RESULTS, f"{user_name}_{topic_id}_{exam_idx}_{uuid.uuid4().hex[:6]}.json")
    with open(fn, "w", encoding="utf-8") as f: json.dump(rec, f, ensure_ascii=False, indent=2)
    return jsonify({"score": score, "correct": correct, "total": total, "detail": detail})

@app.route("/result/<topic_id>/<int:exam_idx>")
def result_page(topic_id, exam_idx):
    user = request.args.get("name", "anonymous")
    # tim file moi nhat cua user+topic+exam
    recs = []
    for f in os.listdir(RESULTS):
        if f.startswith(f"{user}_{topic_id}_{exam_idx}_"):
            recs.append(json.load(open(os.path.join(RESULTS, f), encoding="utf-8")))
    recs = sorted(recs, key=lambda x: x["time"], reverse=True)
    if not recs: return "Chưa có kết quả", 404
    rec = recs[0]
    return render_template("result.html", rec=rec)

@app.route("/results/<user_name>")
def results(user_name):
    recs = []
    for f in os.listdir(RESULTS):
        if f.startswith(user_name):
            recs.append(json.load(open(os.path.join(RESULTS, f), encoding="utf-8")))
    recs.sort(key=lambda x: x["time"], reverse=True)
    return render_template("results.html", name=user_name, recs=recs)

# ===================== THI TRẮC NGHIỆM (client thi qua API) =====================
@app.route("/thi")
@app.route("/thi/")
def thi_page():
    return render_template("thi.html")

# ===================== API CHO ADMIN QUẢN LÝ WEB LEARNING JAPAN =====================
EXAM_RESULTS = os.path.join(HERE, "exam_results")
os.makedirs(EXAM_RESULTS, exist_ok=True)
EXAMS_FILE = os.path.join(HERE, "exams.json")

@app.after_request
def cors_exam(resp):
    if request.path.startswith("/api/"):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp

@app.route("/api/exams", methods=["GET"])
def api_exams():
    p = EXAMS_FILE
    if os.path.exists(p):
        return jsonify(json.load(open(p, encoding="utf-8")))
    return jsonify([])

@app.route("/api/exams", methods=["PUT", "OPTIONS"])
def api_save_exams():
    if request.method == "OPTIONS": return ("", 204)
    data = request.get_json(silent=True)
    if not isinstance(data, list): return jsonify({"ok": False, "error": "expected array"}), 400
    json.dump(data, open(EXAMS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return jsonify({"ok": True, "count": len(data)})

@app.route("/api/submit", methods=["POST", "OPTIONS"])
def api_submit():
    if request.method == "OPTIONS": return ("", 204)
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    user = (data.get("user") or "anonymous").strip() or "anonymous"
    rec = {
        "id": "SUB" + uuid.uuid4().hex[:8],
        "user": user,
        "exam": data.get("exam") or "quizapp_vocab",
        "examTitle": data.get("examTitle") or "Từ vựng N1 (100 câu)",
        "score": data.get("score", 0),
        "correct": data.get("correct", 0),
        "total": data.get("total", 0),
        "passed": data.get("score", 0) >= (data.get("passingScore") or 80),
        "timeSec": data.get("timeSec", 0),
        "submittedAt": datetime.now().isoformat(),
        "answers": data.get("answers", []),
    }
    json.dump(rec, open(os.path.join(EXAM_RESULTS, f"{rec['id']}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return jsonify({"ok": True, "id": rec["id"]})

@app.route("/api/results", methods=["GET"])
def api_results():
    out = []
    for f in os.listdir(EXAM_RESULTS):
        if f.endswith(".json"):
            try: out.append(json.load(open(os.path.join(EXAM_RESULTS, f), encoding="utf-8")))
            except: pass
    out.sort(key=lambda x: x.get("submittedAt", ""), reverse=True)
    return jsonify(out)

# ===================== API QUẢN LÝ N1MASTER (questions.json) =====================
QUESTIONS_FILE = os.path.join(DATA, "questions.json")

@app.route("/api/n1master", methods=["GET"])
def api_n1master_get():
    if os.path.exists(QUESTIONS_FILE):
        return jsonify(json.load(open(QUESTIONS_FILE, encoding="utf-8")))
    return jsonify({"topics": []})

@app.route("/api/n1master", methods=["PUT", "OPTIONS"])
def api_n1master_put():
    if request.method == "OPTIONS": return ("", 204)
    data = request.get_json(force=True, silent=True)
    if not isinstance(data, dict) or "topics" not in data:
        return jsonify({"ok": False, "error": "expected {topics:[...]}"}), 400
    json.dump(data, open(QUESTIONS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return jsonify({"ok": True, "topics": len(data["topics"])})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

# PythonAnywhere / WSGI compatibility
application = app
