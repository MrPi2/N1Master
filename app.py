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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

# PythonAnywhere / WSGI compatibility
application = app
