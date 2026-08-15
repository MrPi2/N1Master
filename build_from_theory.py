#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GIAO SU N1: Tu ly thuyet OCR + kien thuc N1, soan bo de chuan.
Doc idiom/ngu phap tu OCR, tong hop thanh cau hoi trac nghiem JP.
Khong parse cau trac nghiem co san ma TU SOAN moi.
"""
import os, re, json, random
from reading_listening import READING, LISTENING

HERE=os.path.dirname(os.path.abspath(__file__))
DATA=os.path.join(HERE,"data")
STATIC=os.path.join(HERE,"static","audio")

# ===== TU VUNG / IDIOM N1 (tu OCR + chuan) =====
# (tu, yomi, nghia JP, vi du)
VOCAB=[
 ("手を引く","てをひく","やめる・関係を断つ","これ以上被害が大きくならないうちに手を引いたほうがいい。"),
 ("腕を磨く","うでをみがく","技術を上達させる","いろいろなレストランで修業して、腕を磨いた。"),
 ("腕を振るう","うでをふるう","能力を十分に発揮する","得意な料理の腕を振るって、パーティーの準備をした。"),
 ("目が肥える","めがこえる","良いものを見分ける力がつく","いつも良いものを見ていると目が肥えてくる。"),
 ("鼻につく","はなにつく","嫌な感じがする・うるさい","彼の言動が鼻について、いらいらする。"),
 ("肩の荷が下りる","かたのにがおりる","安心する・解放される","会長の座から退いて、やっと肩の荷が下りた。"),
 ("首を捻る","くびをひねる","疑問に思う・理解できない","予想外の結果だったので、首を捻っている。"),
 ("手を入れる","てをいれる","修正・改善する","部屋に手を入れて、きれいにした。"),
 ("耳にする","みみにする","偶然聞く","路上で生活する子供を実際に耳にして、ショックだった。"),
 ("顔を出す","かおをだす","出席する・現れる","パーティーにちょっと顔を出した。"),
 ("口が軽い","くちがかるい","秘密をすぐ話す","あの人は口が軽いから気をつけろ。"),
 ("目に余る","めにあまる","許しがたい・ひどい",""),
 ("手に負えない","てにおえない","制御できない","あの子は手に負えないほど元気だ。"),
 ("腰を据える","こしをすえる","本気で取り組む","腰を据えて勉強する。"),
 ("足を引っ張る","あしをひっぱる","邪魔する・妨げる","チームの足を引っ張るな。"),
 ("頭を抱える","あたまをかかえる","悩む・困る","事件の解決に頭を抱えている。"),
 ("念を押す","ねんをおす","念のため確認する","もう一度念を押させてください。"),
 ("波風を立てる","なみかぜをたてる","争いを起こす","波風を立てずに済ませたい。"),
 ("火の車","ひのくるま","極めて貧しい","家計が火の車だ。"),
 ("鶴の一声","つるのひとこえ","権力者の決定的な言葉","社長の鶴の一声で決まった。"),
 ("猫の手も借りたい","ねこのてもかりたい","非常に忙しい","年末は猫の手も借りたいほど忙しい。"),
 ("願ったり叶ったり","ねがったりかなったり","望み通りになる","願ったり叶ったりの結果だ。"),
 ("暑さ寒さも彼岸まで","あつささむさもひがんまで","苦難も限度がある","暑さ寒さも彼岸までと思って耐えよう。"),
 # Kanji / goi them
 ("甚だしい","はなはだしい","非常に・極めて","甚だしい間違いだ。"),
 ("峻厳","しゅんげん","厳しく雄大","峻厳な山々が連なる。"),
 ("雅やか","みやびやか","上品で優雅","雅やかな雰囲気のパーティー。"),
 ("強引","ごういん","無理やり","強引なやり方は嫌われる。"),
 ("拙い","つたない","下手・未熟","拙い文章で恐縮です。"),
 ("莫大","ばくだい","非常に大きい","莫大な予算が必要だ。"),
 ("乏しい","とぼしい","少ない・貧しい","資源が乏しい。"),
 ("畏まる","かしこまる","慎む・改まる","畏まってお受けします。"),
 ("和らぐ","やわらぐ","柔らかくなる・和らぐ","緊張が和らぐ。"),
 ("啜る","すする","音を立てて飲む・食う","ラーメンを啜る。"),
 ("啄む","ついばむ","嘴で食べる","鳥が餌を啄む。"),
 ("虐げる","しいたげる","苦しめる・虐める","弱者を虐げる。"),
 ("鄙びる","ひなびる","田舎じみる","鄙びた温泉宿が好きだ。"),
 ("黎明","れいめい","夜明け・始まり","黎明の時代。"),
 ("諧謔","かいぎゃく","冗談・おどけ","諧謔を交えて話す。"),
 ("相応しい","ふさわしい","適切である","その地位に相応しい人。"),
 ("阻碍","さまたげ","邪魔・妨げ","進展を阻碍する。"),
 ("精励","せいれい","勉強に励む","精励して試験に臨む。"),
 ("頻りに","しきりに","たびたび・盛んに","頻りに話題に上る。"),
 ("賑やか","にぎやか","賑わい・活気","賑やかな通り。"),
 ("淑やか","しとやか","控えめで上品","淑やかな女性。"),
 ("奢る","おごる","贅沢・高慢","奢った生活を送る。"),
 ("促す","うながす","急かす・促進する","行動を促す。"),
 # === TU OCR VERIFY + N1 CHUAN BO SUNG ===
 ("貧弱","ひんじゃく","貧弱・弱々しい","資源が貧弱な国。"),
 ("巧妙","こうみょう","巧みで優れている","巧妙な手口の犯罪。"),
 ("厚かましい","あつかましい","恥知らず・ずうずうしい","厚かましいお願いはできない。"),
 ("うっとうしい","うっとうしい","鬱陶しい・嫌な","うっとうしい天気が続く。"),
 ("骨身","ほねみ","身の奥底・骨身","骨身を惜しまず働く。"),
 ("検診","けんしん","健康診断","定期検診を受ける。"),
 ("懲りる","こりる","二度としないと誓う","失敗で懲りる。"),
 ("線路","せんろ","線路・轨道","線路に転落する。"),
 ("手口","てぐち","犯行の方法","巧妙な手口の犯罪。"),
 ("国民的","こくみんてき","国民全体の","国民的人気者になる。"),
 ("奇特","きとく","珍しく立派な","奇特な人だ。"),
 ("慮る","おもんばかる","心配する・配慮する","他人のことを慮る。"),
 ("養う","やしなう","育てる・支える","家族を養う。"),
 ("案じる","あんじる","心配する","先行きを案じる。"),
 ("促進","そくしん","早める","計画を促進する。"),
 ("阻む","はばむ","妨げる","進展を阻む。"),
 ("憩う","いこう","休む","公園で憩う。"),
 ("秘める","ひめる","隠し持つ","力を秘める。"),
 ("改まる","あらたまる","公式になる","改まって発表する。"),
 ("促す","うながす","急かす","回答を促す。"),
 ("富む","とむ","豊かである","経験に富む。"),
 ("滞る","とどこおる","遅れる・詰まる","交通が滞る。"),
 ("賑わう","にぎわう","賑やかになる","街が賑わう。"),
 ("養う","やしなう","育てる","健康を養う。"),
 ("慕う","したう","敬愛する","先生を慕う。"),
 ("携わる","たずさわる","関係する","教育に携わる。"),
 ("慈しむ","いつくしむ","愛おしむ","子供を慈しむ。"),
 ("促す","うながす","促す","行動を促す。"),
 ("富める","とめる","豊かな","富める国。"),
 ("阻害","そがい","妨げ","発展を阻害する。"),
 ("苛立つ","いらだつ","イライラする","待たされて苛立つ。"),
 ("埒が明かない","らちがあかない","解決しない","話し合いが埒が明かない。"),
 ("埒もない","らちもない","筋道が通らない","埒もないことを言う。"),
 ("的確","てきかく","正確","的確な判断。"),
 ("妥当","だとう","適当・妥当","妥当な結論。"),
 ("繊細","せんさい","細やか・敏感","繊細な神経。"),
 ("穏やか","おだやか","穏やか・静か","穏やかな性格。"),
 ("厳重","げんじゅう","厳しい","厳重に警戒する。"),
 ("微量","びりょう","わずかな量","微量の毒物。"),
 ("莫大","ばくだい","非常に大きい","莫大な利益。"),
 ("膨大","ぼうだい","膨大・巨大","膨大なデータ。"),
 ("微量","びりょう","微量","微量の成分。"),
 ("秀でる","ひいでる","優れている","才能に秀でる。"),
 ("優れる","すぐれる","優れている","性能が優れる。"),
 ("阻喪","そそう","しょげる","意気阻喪する。"),
 ("緻密","ちみつ","細かく正確","緻密な計画。"),
 ("粗密","そみつ","粗雑と精密","粗密の差。"),
 ("希薄","きはく","薄い・弱い","連帯が希薄になる。"),
 ("濃厚","のうこう","濃い・濃厚","濃厚な味わい。"),
 ("均整","きんせい","釣り合い","均整の取れた体。"),
 ("弥生","やよい","三月","弥生の空。"),
 ("陶冶","とうや","育て磨く","人格を陶冶する。"),
 ("陶酔","とうすい","夢中になる","成功に陶酔する。"),
 ("韻律","いんりつ","リズム","韻律を整える。"),
 ("凌駕","りょうが","越える","他を凌駕する。"),
 ("蒼白","そうはく","青白い","蒼白な顔。"),
 ("淑やか","しとやか","上品","淑やかな振る舞い。"),
 ("淑女","しゅくじょ","上品な女性","淑女のたしなみ。"),
 # === BO SUNG TU OCR VERIFY / SUA LOI ===
 ("計画","けいかく","計画・企画","新しい計画を立てる。"),
 ("瑞祥","ずいしょう","めでたい兆し","瑞祥の兆し。"),
 ("発揮","はっき","能力を出す","実力を発揮する。"),
 ("養成","ようせい","育てる","人材を養成する。"),
 ("定義","ていぎ","意味を定める","用語を定義する。"),
 ("類推","るいすい","類して推測","経験から類推する。"),
 ("従事","じゅうじ","取り組む","研究に従事する。"),
 ("進化","しんか","発展変化","生物の進化。"),
 ("絶滅","ぜつめつ","滅びる","種が絶滅する。"),
 ("記載","きさい","書き記す","書類に記載する。"),
 ("掲載","けいさい","掲げ載せる","新聞に掲載する。"),
 ("参照","さんしょう","見比べる","資料を参照する。"),
 ("異議","いぎ","異論","異議を唱える。"),
 ("衰退","すいたい","衰える","产业が衰退する。"),
 ("施行","しこう","実施する","法律を施行する。"),
 ("制定","せいてい","定める","憲法を制定する。"),
 ("廃止","はいし","止める","制度を廃止する。"),
 ("親和","しんわ","なじむ","自然と親和する。"),
 ("協議","きょうぎ","話し合う","方針を協議する。"),
 ("感染","かんせん","移る","ウイルスに感染する。"),
 ("道化","どうけ","おどけ","道化を言う。"),
 ("四苦八苦","しくはっく","苦労する","四苦八苦して完成させた。"),
 ("五里霧中","ごりむちゅう","当てが外れる","五里霧中で迷う。"),
 ("七不思議","ななふしぎ","不思議な現象","世界の七不思議。"),
 ("施行","しこう","執行","刑罰を施行する。"),
 ("推敲","すいこう","練る","原稿を推敲する。"),
 ("円満","えんまん","平和","円満に解決する。"),
 ("敏速","びんそく","素早い","敏速な対応。"),
 ("概略","がいりゃく","あらまし","計画の概略。"),
 ("巧妙","こうみょう","巧み","巧妙な手段。"),
 ("厳格","げんかく","厳しい","厳格な規則。"),
 ("厳重","げんじゅう","念入り","厳重に守る。"),
 ("希少","きしょう","まれ","希少な存在。"),
 ("稀有","けう","まれ","稀有な機会。"),
 ("気丈","きじょう","しっかり","気丈な態度。"),
 ("巨大","きょだい","非常大","巨大な建造物。"),
 ("強靭","きょうじん","強い","強靭な精神。"),
 ("均一","きんいつ","等しい","均一な品質。"),
 ("困惑","こんわく","困る","返答に困惑する。"),
 ("脆弱","ぜいじゃく","弱い","脆弱な立场。"),
 ("挫折","ざせつ","失敗","挫折を乗り越える。"),
 ("執着","しゅうちゃく","こだわる","過去に執着する。"),
 ("重厚","じゅうこう","重み","重厚な作品。"),
 ("純粋","じゅんすい","混じりけない","純粋な動機。"),
 ("順調","じゅんちょう","順当","順調に進む。"),
 ("焦燥","しょうそう","あせる","焦燥感を覚える。"),
 ("充実","じゅうじつ","満ちる","充実した日々。"),
 ("潤沢","じゅんたく","豊か","潤沢な資金。"),
 ("精細","せいさい","細かい","精細な描写。"),
 ("整然","せいぜん","整う","整然と並ぶ。"),
 ("静寂","せいじゃく","静か","静寂な夜。"),
 ("潜在","せんざい","隠れ","潜在能力。"),
 ("粗末","そまつ","粗い","粗末な扱い。"),
 ("滞在","たいざい","滞まる","外国に滞在する。"),
 ("脱稿","だっこう","書き終える","原稿を脱稿する。"),
 ("端的","たんてき","明確","端的に言う。"),
 ("緻密","ちみつ","細かく正確","緻密な計画。"),
 ("低迷","ていめい","下がる","景気が低迷する。"),
 ("頓着","とんちゃく","決着","頓着がつく。"),
 ("忍耐","にんたい","耐える","忍耐強い。"),
 ("認識","にんしき","わかる","危険を認識する。"),
 ("罷免","ひめん","解任","役員を罷免する。"),
 ("貧困","ひんこん","貧しい","貧困から抜け出す。"),
 ("不況","ふきょう","不景気","経済不況。"),
 ("不備","ふび","欠陥","計画の不備。"),
 ("平易","へいい","易しい","平易な表現。"),
 ("飽和","ほうわ","満たされる","市場が飽和する。"),
 ("飽くまで","あくまで","あくまでも","飽くまで主張する。"),
 ("遂行","すいこう","果たす","任務を遂行する。"),
 ("隣接","りんせつ","接する","隣接する土地。"),
 ("論争","ろんそう","争う","論争を呼ぶ。"),
 ("和らぐ","やわらぐ","柔らぐ","緊張が和らぐ。"),
 # Ngu phap
]

# ===== NGU PHAP N1 (chuan) =====
GRAMA=[
 ("〜ずにはいられない","自然な感情・衝動を表す。『必ず〜する』の意味。","感動して、涙を流さずにはいられなかった。"),
 ("〜を余儀なくされる","外部の事情で必要な行動を強制される。","台風で中止を余儀なくされた。"),
 ("〜べくもない","可能性がない。『〜できるはずがない』。","初心者にそれができるべくもない。"),
 ("〜といったらない","極端な状態を強調。『最高に〜』。","その寂しさといったらない。"),
 ("〜を皮切りに","始まりの出来事。『〜を初めとして』。","東京公演を皮切りに全国ツアーを行う。"),
 ("〜にあって","その状況・時に置かれて。","困難な状況にあっても諦めない。"),
 ("〜をもって","手段・時点・理由。『〜で』。","本日をもって終了とする。"),
 ("〜かたがた","ある行為を兼ねる。『〜を兼ねて』。","挨拶かたがた集金に伺う。"),
 ("〜ないではおかない","必ずそうなる。『確実に〜する』。","その問題は議論を呼ばないではおかない。"),
 ("〜ずもがな","しない方がよかった。『〜しなければ良かった』。","言わずもがなのことを口にした。"),
 ("〜べく","目的・意図。『〜するために』。","勝つべく練習を重ねた。"),
 ("〜にかたくない","容易に〜できる。『簡単に〜想像できる』。","彼らの悲しみは想像にかたくない。"),
 ("〜をおいてほかにはない","それ以外に方法がない。『〜だけが』。","彼をおいて適任者はいない。"),
 ("〜と相まって","二つが組み合わさって。『〜と合わさって』。","好天と相まって大盛況だ。"),
 ("〜そばから","直後にすぐ。『〜するとすぐに』。","教えるそばから忘れる。"),
 ("〜や否や","同時に・直後。『〜するとすぐに』。","ベルが鳴るや否や駆け出した。"),
 ("〜んばかりに","まるで〜するかのよう。『今にも〜しそう』。","飛び上がらんばかりに喜んだ。"),
 ("〜ずくめ","全てが〜。『全部〜だけ』。","この一年は幸せずくめだった。"),
 ("〜の至り","最高の状態・感激。『非常に〜』。","光栄の至りです。"),
 ("〜たるもの","資格・立場。『〜としての』。","指導者たるものの責任。"),
 ("〜いかん","内容・結果によって。『〜によって』。","結果いかんでは辞任もあり得る。"),
]

# ===== SOAN CAU HOI =====
def make_vocab_q():
    v=random.choice(VOCAB)
    tu,yomi,nghia,ex=v
    # chon 3 nhieu sai tu VOCAB khac
    others=[x for x in VOCAB if x[0]!=tu]
    random.shuffle(others)
    wrong=[o[2] for o in others[:3]]  # nghia JP cua tu khac
    opts=[nghia]+wrong
    random.shuffle(opts)
    ans=opts.index(nghia)
    if ex:
        q=f"次の文の下線の語「{tu}（{yomi}）」の意味として最も適当なものを選びなさい。\n例文：{ex}"
    else:
        q=f"「{tu}（{yomi}）」の意味として正しいものを選びなさい。"
    explain=f"「{tu}」は「{nghia}」という意味です。{ex if ex else ''}"
    return {"q":q,"options":opts,"answer":ans,"explain":explain}

def make_yomi_q():
    v=random.choice(VOCAB)
    tu,yomi,nghia,ex=v
    # wrong yomi tu tu khac
    others=[x for x in VOCAB if x[1]!=yomi and x[1]]
    random.shuffle(others)
    wrong=[o[1] for o in others[:3]]
    opts=[yomi]+wrong
    random.shuffle(opts)
    ans=opts.index(yomi)
    q=f"「{tu}」の読み方として正しいものを選びなさい。"
    explain=f"「{tu}」は「{yomi}」と読みます。"
    return {"q":q,"options":opts,"answer":ans,"explain":explain}

def make_grammar_q():
    g=random.choice(GRAMA)
    form,nghia,ex=g
    others=[x for x in GRAMA if x[0]!=form]
    random.shuffle(others)
    wrong=[o[1] for o in others[:3]]
    opts=[nghia]+wrong
    random.shuffle(opts)
    ans=opts.index(nghia)
    q=f"次の文の（　　）に入れるのに最もよいものを選びなさい。\n例文：{ex}\n文法形式：「{form}」"
    explain=f"「{form}」は「{nghia}」という意味・用法です。例：{ex}"
    return {"q":q,"options":opts,"answer":ans,"explain":explain}

def make_blank_q():
    # dien idiom vao cho trong
    v=random.choice(VOCAB)
    tu,yomi,nghia,ex=v
    if not ex: return make_vocab_q()
    # tao cau co cho trong
    blank_ex=re.sub(re.escape(tu),"（　　）",ex)
    # wrong: 3 idiom khac
    others=[x for x in VOCAB if x[0]!=tu]
    random.shuffle(others)
    wrong=[o[0] for o in others[:3]]
    opts=[tu]+wrong
    random.shuffle(opts)
    ans=opts.index(tu)
    q=f"次の文の（　　）に入れるのに最もよい言葉を選びなさい。\n{blank_ex}"
    explain=f"正解は「{tu}（{yomi}）：{nghia}」です。"
    return {"q":q,"options":opts,"answer":ans,"explain":explain}

TOPICS=[
 (1,"goi","Từ vựng N1 cơ bản",[make_vocab_q,make_yomi_q]),
 (2,"kanji","Hán tự & Đọc hiểu cơ bản",[make_yomi_q,make_blank_q]),
 (3,"dokkai","Đọc hiểu N1",[make_blank_q,make_vocab_q]),
 (4,"bunpou","Ngữ pháp N1",[make_grammar_q]),
 (5,"chokai","Nghe hiểu N1",[make_vocab_q,make_grammar_q]),
 (6,"goi2","Từ vựng nâng cao",[make_vocab_q,make_blank_q]),
 (7,"bunpou2","Ngữ pháp nâng cao",[make_grammar_q,make_blank_q]),
 (8,"dokkai2","Đọc hiểu thực dụng",[make_blank_q,make_vocab_q]),
 (9,"vocab_kanji","Từ vựng + Hán tự tổng hợp",[make_vocab_q,make_yomi_q,make_blank_q]),
 (10,"grammar_mix","Cấu trúc hỗn hợp (khó nhất)",[make_grammar_q,make_blank_q,make_vocab_q]),
 (11,"dokkai_text","Đọc hiểu đoạn văn (N1 thật)",[]),
 (12,"chokai_audio","Nghe hiểu (Audio N1)",[]),
]

def make_reading_q():
    # chon 1 doan van, tra ve cau hoi dang reading
    r=random.choice(READING)
    qs=[]
    for i,item in enumerate(r["questions"]):
        opts=item["options"][:]
        random.shuffle(opts)
        a=opts.index(item["options"][item["answer"]]) if isinstance(item["answer"],int) else opts.index(item["options"][0])
        # tim index dung
        a=opts.index(item["options"][item["answer"]])
        qs.append({"q":item["q"],"options":opts,"answer":a,"explain":item["explain"]})
    return {"type":"reading","title":r["title"],"passage":r["text"],"questions":qs}

def make_listening_q():
    r=random.choice(LISTENING)
    qs=[]
    for i,item in enumerate(r["questions"]):
        opts=item["options"][:]
        random.shuffle(opts)
        a=opts.index(item["options"][item["answer"]])
        qs.append({"q":item["q"],"options":opts,"answer":a,"explain":item["explain"]})
    return {"type":"listening","title":r["title"],"script":r["script"],"audio":f"/static/audio/{abs(hash(r['script']))%100000}.mp3","questions":qs}

def build():
    import asyncio
    random.seed(2024)
    topics=[]
    # sinh audio truoc
    audio_map={}
    os.makedirs(STATIC,exist_ok=True)
    async def gen_audio():
        import edge_tts
        for r in LISTENING:
            fn=os.path.join(STATIC, f"{abs(hash(r['script']))%100000}.mp3")
            if not os.path.exists(fn):
                try:
                    comm=edge_tts.Communicate(r["script"], voice="ja-JP-NanamiNeural")
                    await comm.save(fn)
                except Exception as e:
                    print("audio err:", e)
    try:
        asyncio.run(gen_audio())
    except Exception as e:
        print("audio gen skip:", e)
    for diff,tid,tname,genfns in TOPICS:
        exams=[]
        if tid=="dokkai_text":
            for e in range(10):
                ed=diff+e*0.1
                hard=ed>=7 or e>=7
                # moi bai = 1 doan van + 3-4 cau hoi → bai co the nhieu doan (de du 20 cau)
                qs=[]
                used=[]
                for _ in range(7):  # 7 doan x 3 cau = 21 ~ 20
                    rq=make_reading_q()
                    used.append(rq)
                # flatten thanh cau hoi tung doan
                blocks=[]
                for rq in used:
                    blocks.append({"type":"reading","title":rq["title"],"passage":rq["passage"],"questions":rq["questions"],"multi":False})
                exams.append({"title":f"Bài {e+1}","name":f"{tname} - Bài {e+1}"+(" (Nâng cao)" if hard else ""),"difficulty":round(ed,1),"questions":blocks})
            topics.append({"id":tid,"name":tname,"difficulty":diff,"exams":exams})
            continue
        if tid=="chokai_audio":
            for e in range(10):
                ed=diff+e*0.1
                hard=ed>=7 or e>=7
                blocks=[]
                for _ in range(7):
                    lq=make_listening_q()
                    blocks.append({"type":"listening","title":lq["title"],"script":lq["script"],"audio":lq["audio"],"questions":lq["questions"],"multi":False})
                exams.append({"title":f"Bài {e+1}","name":f"{tname} - Bài {e+1}"+(" (Nâng cao)" if hard else ""),"difficulty":round(ed,1),"questions":blocks})
            topics.append({"id":tid,"name":tname,"difficulty":diff,"exams":exams})
            continue
        # cac chu de thuong
        for e in range(10):
            ed=diff+e*0.1
            hard = ed>=7 or e>=7
            qs=[]
            for qi in range(20):
                fn=random.choice(genfns)
                item=fn()
                multi=False; a=item["answer"]
                if hard and qi%3==0 and len(item["options"])>=2:
                    multi=True
                    a=[a,(a+1)%len(item["options"])]
                qs.append({"q":item["q"],"options":item["options"],"answer":a,"multi":False,"explain":item["explain"]})
                qs[-1]["multi"]=multi
            exams.append({"title":f"Bài {e+1}","name":f"{tname} - Bài {e+1}"+(" (Nâng cao)" if hard else ""),"difficulty":round(ed,1),"questions":qs})
        topics.append({"id":tid,"name":tname,"difficulty":diff,"exams":exams})
    return {"topics":topics}

if __name__=="__main__":
    data=build()
    total=sum(len(t["exams"])*len(t["exams"][0]["questions"]) for t in data["topics"])
    os.makedirs(DATA,exist_ok=True)
    json.dump(data, open(os.path.join(DATA,"questions.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    # regenerate Quiz_app (05_Quiz_App)
    try:
        import re as _re
        out=[]
        for t in data["topics"]:
            for ex in t["exams"]:
                for q in ex["questions"]:
                    if q.get("multi"): continue
                    ans=q["answer"]
                    if isinstance(ans,list): continue
                    out.append({"question":q["q"],"options":q["options"],"correct":ans,"explanation":q.get("explain","")})
                    if len(out)>=100: break
                if len(out)>=100: break
            if len(out)>=100: break
        random.seed(42); random.shuffle(out)
        js="const questions = [\n"+("\n".join(f"  {{ id:{i+1}, question:{json.dumps(q['question'],ensure_ascii=False)}, options:{json.dumps(q['options'],ensure_ascii=False)}, correct:{q['correct']},\n    explanation:{json.dumps(q['explanation'],ensure_ascii=False)} }}," for i,q in enumerate(out)))+"\n];"
        i2=os.path.join(HERE,"..","05_Quiz_App","index.html")
        if os.path.exists(i2):
            h=open(i2,encoding="utf-8").read()
            h=_re.sub(r"const questions = \[.*?\];", js.rstrip()+";", h, count=1, flags=_re.S)
            open(i2,"w",encoding="utf-8").write(h)
        print(f"✅ GIAO SU N1 build: {len(data['topics'])} chu de x 10 bai x 20 cau = {total} cau (tu ly thuyet + kien thuc N1)")
        print(f"✅ Quiz_app regenerated: {len(out)} cau")
    except Exception as e:
        print("regen err:", e)
