#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR toan bo 7 file PDF tieng Nhat -> raw text. Tiet kiem quota: moi trang 1 request, image <1MB."""
import os, glob, json, time, fitz, requests

SRC = r"C:/Users/Admin/Downloads/japan"
OUT = r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/raw_ocr"
KEY = "K82673044688957"
os.makedirs(OUT, exist_ok=True)

def ocr_image(img_path):
    for attempt in range(3):
        try:
            r = requests.post("https://api.ocr.space/parse/image",
                files={"image": open(img_path, "rb")},
                data={"apikey": KEY, "language": "jpn", "scale": True,
                      "OCREngine": 2, "isOverlayRequired": False},
                timeout=45)
            j = r.json()
            if j.get("OCRExitCode") in (1, 2, 3):
                return j["ParsedResults"][0].get("ParsedText", "")
            if j.get("ErrorMessage"):
                # quota/limit -> return None de dung
                return f"__ERR__{j.get('ErrorMessage')}"
        except Exception as e:
            time.sleep(3)
    return ""

def process_file(pdf_path):
    name = os.path.splitext(os.path.basename(pdf_path))[0]
    out_txt = os.path.join(OUT, f"{name}.txt")
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 1000:
        print(f"  [skip] {name} da co"); return True
    doc = fitz.open(pdf_path)
    print(f"[file] {name}: {doc.page_count} trang")
    all_text = []
    for i in range(doc.page_count):
        # cat trang thanh image dpi thap de <1MB
        pix = doc[i].get_pixmap(dpi=110)
        ip = os.path.join(OUT, f"_{name}_{i}.png")
        pix.save(ip)
        if os.path.getsize(ip) > 950000:
            # giam dpi
            pix = doc[i].get_pixmap(dpi=80); pix.save(ip)
        t = ocr_image(ip)
        os.remove(ip)
        if t.startswith("__ERR__"):
            print(f"  [STOP] loi quota: {t}"); break
        all_text.append(f"\n===== PAGE {i+1} =====\n{t}")
        if (i+1) % 10 == 0:
            print(f"  page {i+1}/{doc.page_count}, chars={len(t)}")
        time.sleep(1)  # tranh rate limit
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))
    print(f"  -> luu {out_txt} ({os.path.getsize(out_txt)//1024} KB)")
    return True

if __name__ == "__main__":
    # ghi pid file de auto_ocr_build.py biet OCR dang chay (fix: truoc day khong ghi nen bi build nham luc OCR chua xong)
    _pidf = r"C:/Users/Admin/Documents/DongBao_Works/04_Japan_Learning_Web/ocr_running_pid.txt"
    try: open(_pidf,"w").write(str(os.getpid()))
    except Exception: pass
    pdfs = sorted(glob.glob(os.path.join(SRC, "*.pdf")))
    for p in pdfs:
        try:
            process_file(p)
        except Exception as e:
            print(f"  [file err] {p}: {e}")
    print("DONE OCR")
    try: os.remove(_pidf)
    except Exception: pass
