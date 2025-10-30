import json
import os

# --- Cấu hình ---
INPUT_FILE = "cleaned_dataset.json"   # file gốc
OUTPUT_DIR = "real_articles"                                # thư mục chứa file tách
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Đọc file ---
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"📦 Tổng số bản ghi: {len(data)}")

# --- Thêm nhãn & tách ---
for i, article in enumerate(data, start=1):
    # Gán nhãn real
    article["label"] = "real"

    # Đặt tên file
    filename = article.get("filename") or f"article_{i}.json"
    if not filename.endswith(".json"):
        filename += ".json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Ghi file riêng
    with open(filepath, "w", encoding="utf-8") as f_out:
        json.dump(article, f_out, ensure_ascii=False, indent=4)

    print(f"💾 Đã lưu: {filename}")

print(f"✅ Hoàn tất! Đã tách {len(data)} file vào thư mục '{OUTPUT_DIR}'.")
