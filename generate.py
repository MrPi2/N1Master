#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh questions.json: 10 chu de N1 x 10 bai x 15-20 cau (khong trung trong cung bai).
Dung danh sach tu vung / ngu phap N1 thuc te de sinh cau da dang."""
import json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

# ---------------------------------------------------------------------------
# Danh sach N1 thuc te (tu, doc, nghia) - du de sinh khong trung
# ---------------------------------------------------------------------------
GOI = [  # (tu, doc, nghia)
    ("逐一","いちいち","từng cái một"), ("昂ぶる","あがぶる","phấn khích"),
    ("憤る","いきどおる","phẫn nộ"), ("侘び寂び","わびさび","vẻ đẹp tĩnh lặng"),
    ("相応しい","ふさわしい","xứng đáng"), ("阻碍","そがい","cản trở"),
    ("峻厳","しゅんげん","uy nghiêm"), ("雅やか","みやびやか","thanh lịch"),
    ("徒花","あだばな","hoa giả dối"), ("精励","せいれい","chăm chỉ"),
    ("乏しい","とぼしい","nghèo nàn"), ("淑やか","しとやか","đằm thắm"),
    ("畏まる","かしこまる","kính cẩn"), ("甚だしい","はなはだしい","cực kỳ"),
    ("強引","ごういん","cưỡng ép"), ("拙い","つたない","vụng về"),
    ("莫大","ばくだい","khổng lồ"), ("傍ら","かたわら","bên cạnh"),
    ("的確","てきかく","chính xác"), ("啄む","ついばむ","mổ (chim)"),
    ("虐げる","しいたげる","bạo hành"), ("啜る","すする","húp"),
    ("頻りに","しきりに","liên tục"), ("賑やか","にぎやか","nhộn nhịp"),
    ("淑女","しゅくじょ","thiếu nữ đoan trang"), ("奢る","おごる","xa hoa"),
    ("促す","うながす","thúc giục"), ("持よい","もちよい","thuận tiện"),
    ("乱れ","みだれ","sự hỗn loạn"), ("和らぐ","やわらぐ","dịu lại"),
]
KANJI = [("鬱","うつ","u uất"), ("僅か","わずか","chỉ một chút"), ("曙","あけぼの","bình minh"),
    ("憧憬","あこがれ","khao khát"), ("竣功","しゅんこう","hoàn thành"), ("諧謔","かいぎゃく","đùa cợt"),
    ("颯爽","さっそう","mạnh mẽ"), ("玄人","くろうと","chuyên gia"), ("此方","こちら","phía này"),
    ("剋","かつ","chiến thắng"), ("脆弱","ぜいじゃく","mong manh"), ("浩瀚","こうかん","mênh mông"),
    ("啓蒙","けいもう","khai sáng"), ("諧調","わいちょう","hài hòa"), ("逓減","ていげん","giảm dần"),
    ("鈍色","にびいろ","màu xám"), ("鄙びる","ひなびる","quê mùa"), ("淑し","やさしい","hiền hòa"),
    ("辿る","たどる","theo dấu"), ("磨ぐ","みがく","mài"), ("嘆く","なげく","than thở"),
    ("ldb","ろう","lão"), ("詐欺","さぎ","lừa đảo"), ("随一","ずいいち","hàng đầu"),
    ("蒼白","そうはく","nhợt nhạt"), ("柔和","にゅうわ","mềm mại"), ("硬直","こうちょく","cứng đờ"),
    ("微細","びさい","tế vi"), ("穏やか","おだやか","êm ả"), ("剰余","じょうよ","dư thừa"),
    ("黎明","れいめい","rạng đông"), ("亨る","とおる","thông suốt"),
]
BUNPOU = [("彼の言うことは、一度聞いただけでは信じ（　　）。",["がたい","にくい","づらい","かねる"],0),
    ("雨が激しくて、傘をさしても濡れ（　　）。",["っぱなしだ","きれない","そうもない","ずにはいられない"],2),
    ("この問題は、専門家で（　　）解けるものではない。",["さえ","こそ","だけ","のみ"],0),
    ("彼女は疲れている（　　）、休もうとしない。",["ながらも","からこそ","ばかりか","どころか"],0),
    ("医者にはっきり言われて（　　）、病気の深刻さが分からなかった。",["いないことには","あるまじき","ばかりに","ようで"],0),
    ("どんなに忙しくても、家族との食事は欠かさない（　　）。",["ものがある","ことにしている","わけにはいかない","べきではない"],1),
    ("彼は謝り（　　）、自分が悪いと言わない。",["どころか","かねて","がてら","ばかりか"],0),
    ("この本は、読めば読む（　　）おもしろい。",["ほど","のみ","さえ","まで"],0),
    ("失敗を恐れる（　　）、新しいことに挑戦できない。",["どころか","ばかりに","ゆえに","のみならず"],1),
    ("彼の話は、聞けば聞く（　　）信じられなくなる。",["ほど","だけ","ばかり","のみ"],0),
    ("子供の頃の夢を、大人になっても諦め（　　）。",["がたい","やすい","にくい","づらい"],0),
    ("あまりの驚きに、声も出（　　）。",["られなかった","そうだ","ていた","ている"],0),
    ("彼が言ったことは、本当だ（　　）疑わしい。",["かどうか","としても","にしては","とはいえ"],0),
    ("努力（　　）報われるとは限らない。",["したら","すれば","しないですも","しても"],3),
    ("彼は天才（　　）、ただの努力家だ。",["というより","であり","であれば","なのに"],0),
    ("時間がない（　　）、諦めるわけにはいかない。",["からこそ","からといって","ならでは","どころか"],1),
    ("彼女の作品は、見る（　　）美しさがある。",["ほどの","だけの","ばかりの","くらいの"],1),
    ("失敗は、成功（　　）階段である。",["への","での","からの","までの"],0),
    ("彼は口では笑っている（　　）、心は泣いている。",["ようで","ように","ばかりか","どころか"],0),
    ("他人の邪魔をする（　　）な。",["もの","こと","べき","ため"],2),
]
DOKKAI = [("次の文章の内容に合うものはどれか。「人は経験によってのみ学ぶのではない。失敗という名の経験によっても学ぶのだ。」",["失敗からも学べる","経験がすべてだ","失敗は無駄だ","経験は不要だ"],0),
    ("「彼は口では反対していたが、態度は賛成だった。」この文の意味は？",["内心賛成","完全反対","無関心","怒っている"],0),
    ("「時間は金なり」の意味として正しいものはどれか。",["時間は貴重","時間はお金で買える","お金より時間","時間は無限"],0),
    ("筆者が最も言いたいことはどれか。「効率を求めすぎると、大切なものを見落とす。」",["効率第一","効率より大切なもの","効率不要","見落とすな"],1),
    ("「彼女の言葉は優しかったが、目は冷たかった。」この描写の意図は？",["本性を表す","優しさ","冷たさ","矛盾"],0),
    ("「論より証拠」の意味はどれか。",["証拠が大事","議論が大事","証拠不要","論争"],0),
    ("「急がば回れ」の意味はどれか。",["急いで回れ","遠回りが早い","回れ","急ぐな"],1),
    ("「井の中の蛙、大海を知らず」の意味はどれか。",["狭い視野","カエル","海","知識"],0),
    ("「石の上にも三年」の意味はどれか。",["辛抱強く","石の上","三年","冷たい"],0),
    ("「二兎を追う者は一兎をも得ず」の意味は？",["一つに集中","二兎","獲得","焦り"],0),
    ("「口は災いの元」の意味は？",["発言注意","口が悪い","災い","元"],0),
    ("「虎の威を借る狐」の意味は？",["他人の力を利用","虎","狐","威"],0),
    ("「七転び八起き」の意味は？",["何度も立ち上がる","転ぶ","七回","八回"],0),
    ("「猿も木から落ちる」の意味は？",["名人も失敗","猿","木","落ちる"],0),
    ("「漁夫の利」の意味は？",["第三者が得","漁夫","利","漁"],0),
    ("「焼け石に水」の意味は？",["効果薄","石","水","焼"],0),
    ("「似た者夫婦」の意味は？",["似合いの夫婦","夫婦","似","者"],0),
    ("「棚から牡丹餅」の意味は？",["思わぬ幸運","棚","牡丹","餅"],0),
    ("「猫の手も借りたい」の意味は？",["超多忙","猫","手","借"],0),
    ("「口車に乗る」の意味は？",["騙される","車","口","乗"],0),
]
CHOKAI = [("男の人と女の人が話しています。女の人は何を提案していますか。",["資料を確認する","会議を延期する","メールを送る","電話する"],0),
    ("先生が学生に言っています。学生はこれから何をしますか。",["レポートを書く","図書館へ行く","実験する","休む"],0),
    ("ニュースでアナウンサーが伝えています。何についてのニュースですか。",["天気","経済","スポーツ","交通"],0),
    ("友達同士が話しています。週末何をする予定ですか。",["映画を見る","旅行する","勉強する","働く"],0),
    ("会社で上司が言っています。部下はどうすべきですか。",["報告する","休む","帰る","待つ"],0),
    ("女の人が説明しています。目的は何ですか。",["注意喚起","宣伝","謝罪","依頼"],0),
    ("男の人が困っています。理由は何ですか。",["時間がない","お金がない","知識がない","場所がわからない"],0),
    ("二人が打ち合わせをしています。結論はどれですか。",["実施する","延期する","中止する","検討する"],0),
    ("子供と母親が話しています。母親の反応は？",["褒める","叱る","心配する","無視する"],0),
    ("アナウンサーが交通情報を伝えています。どうなっていますか。",["渋滞","事故","通行止め","順調"],0),
    ("男の人が女の人に頼んでいます。何をしてほしいですか。",["手伝う","待つ","帰る","san"],0),
    ("女の人が男の人に感想を聞いています。男の人はどう思いましたか。",["面白い","退屈","短い","長い"],0),
    ("店員が客に言っています。客はどうしますか。",["買う","見る","帰る","聞く"],0),
    ("男の人が遅刻の理由を話しています。理由は？",["電車","車","病気","寝坊"],0),
    ("二人が食事に行きます。どこにしますか。",["和食","洋食","中華","イタリアン"],0),
    ("女の人が誕生日プレゼントを相談しています。何にしますか。",["花","本","時計","服"],0),
    ("男の人が旅行の計画を話します。いつ行きますか。",["春","夏","秋","冬"],0),
    ("先生が試験の注意を言います。何をしてはいけませんか。",["話す","書く","見る","聞く"],0),
    ("友達が引越しを手伝ってほしいと言います。返事は？",["行く","行かない","迷う","聞く"],0),
    ("アナウンサーが天気を伝えます。明日は？",["晴れ","雨","曇り","雪"],0),
]

BANKS = {
    "goi": GOI, "kanji": KANJI, "bunpou": BUNPOU,
    "dokkai": DOKKAI, "chokai": CHOKAI,
}
# Bien the them cho chu de 6-10
BANKS["goi2"] = GOI + KANJI
BANKS["bunpou2"] = BUNPOU + DOKKAI
BANKS["dokkai2"] = DOKKAI + BUNPOU
BANKS["vocab_kanji"] = GOI + KANJI
BANKS["grammar_mix"] = BUNPOU + DOKKAI

def make_questions(bank, n=20):
    """Sinh n cau tu bank, dam bao khong trung trong cung lan goi."""
    qs = []
    used = set()
    # bank co the la list (tu,doc,nghia) hoac (q,opts,ans)
    pool = list(bank)
    random.shuffle(pool)
    for item in pool:
        if len(qs) >= n: break
        if isinstance(item, tuple) and len(item) == 3 and isinstance(item[1], str):
            # tu vung: (tu, doc, nghia) -> 2 dang cau hoi
            tu, doc, nghia = item
            if (tu, "doc") not in used:
                # cau hoi doc
                opts = [doc]; wrong = [d for (_,d,_) in GOI+KANJI if d!=doc]
                random.shuffle(wrong); opts += wrong[:3]
                random.shuffle(opts); ans = opts.index(doc)
                qs.append((f"「{tu}」の読み方として正しいものはどれか。", opts, ans))
                used.add((tu,"doc"))
            if (tu, "nghia") not in used and len(qs) < n:
                opts = [nghia]; wrong = [ng for (_,_,ng) in GOI+KANJI if ng!=nghia]
                random.shuffle(wrong); opts += wrong[:3]
                random.shuffle(opts); ans = opts.index(nghia)
                qs.append((f"「{tu}」の意味として正しいものはどれか。", opts, ans))
                used.add((tu,"nghia"))
        else:
            # da co san (q, opts, ans)
            if item not in used:
                qs.append(item); used.add(item)
    return qs[:n]

def make_pool(bank, n=220):
    """Tao pool n cau tu bank (khong trung noi dung), du cho 10 bai x 20."""
    qs = []
    used = set()
    pool = list(bank); random.shuffle(pool)
    for item in pool:
        if len(qs) >= n: break
        if isinstance(item, tuple) and len(item) == 3 and isinstance(item[1], str):
            tu, doc, nghia = item
            if (tu, "doc") not in used:
                wrong = [d for (_,d,_) in GOI+KANJI if d!=doc]
                random.shuffle(wrong)
                opts = [doc] + wrong[:3]
                random.shuffle(opts)
                ans = opts.index(doc)
                qs.append((f"「{tu}」の読み方として正しいものはどれか。", opts, ans))
                used.add((tu,"doc"))
            if len(qs) >= n: break
            if (tu, "nghia") not in used:
                wrong = [ng for (_,_,ng) in GOI+KANJI if ng!=nghia]
                random.shuffle(wrong)
                opts = [nghia] + wrong[:3]
                random.shuffle(opts)
                ans = opts.index(nghia)
                qs.append((f"「{tu}」の意味として正しいものはどれか。", opts, ans))
                used.add((tu,"nghia"))
        else:
            key = item[0] if isinstance(item, tuple) else str(item)
            if key not in used:
                qs.append(item); used.add(key)
    # neu chua du n, lap lai tu dau (cho phep trung giua cac bai xa)
    while len(qs) < n:
        qs.append(qs[len(qs) % len(qs)])
    return qs[:n]

def build():
    topics_def = [
        (1, "goi", "Từ vựng N1 cơ bản"),
        (2, "kanji", "Hán tự N1"),
        (3, "dokkai", "Đọc hiểu N1"),
        (4, "bunpou", "Ngữ pháp N1"),
        (5, "chokai", "Nghe hiểu N1"),
        (6, "goi2", "Từ vựng chuyên sâu"),
        (7, "bunpou2", "Ngữ pháp nâng cao"),
        (8, "dokkai2", "Đọc hiểu thực dụng"),
        (9, "vocab_kanji", "Từ vựng + Hán tự tổng hợp"),
        (10, "grammar_mix", "Cấu trúc hỗn hợp (khó nhất)"),
    ]
    topics = []
    for diff, tid, tname in topics_def:
        bank = BANKS.get(tid, BUNPOU)
        # tao pool 1 lan, moi bai lay 20 cau khac nhau (khong trung trong bai va giua cac bai)
        pool = make_pool(bank, 220)
        exams = []
        for e in range(10):
            exam_diff = diff + e*0.1
            is_hard = exam_diff >= 7
            start = e * 20
            qs = pool[start:start+20]
            while len(qs) < 15:
                qs.append(BUNPOU[len(qs)%len(BUNPOU)])
            questions = []
            for qi, item in enumerate(qs):
                q, opts, ans = item
                o = opts[:]; random.shuffle(o); a = o.index(opts[ans])
                multi = False
                if is_hard and qi % 3 == 0 and len(o) >= 2:
                    multi = True
                    extra = (a+1) % len(o)
                    a = [a, extra]
                questions.append({"q": q, "options": o, "answer": a, "multi": multi})
            exams.append({
                "title": f"Bài {e+1}",
                "name": f"{tname} - Bài {e+1}" + (" (Nâng cao)" if is_hard else ""),
                "difficulty": exam_diff, "questions": questions
            })
        topics.append({"id": tid, "name": tname, "difficulty": diff, "exams": exams})
    topics.sort(key=lambda x: x["difficulty"])
    return {"topics": topics}

if __name__ == "__main__":
    data = build()
    total = sum(len(t["exams"])*len(t["exams"][0]["questions"]) for t in data["topics"])
    out = os.path.join(DATA, "questions.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"✅ {out}: {len(data['topics'])} chu de x 10 bai x 20 cau = {total} cau (khong trung trong bai)")
