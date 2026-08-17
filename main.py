import io
import os
import base64
from PIL import Image, ImageDraw, ImageFont
from js import document

# --- ファイルパス設定（リポジトリ直下の実際のファイル名） ---
FONT_PATH = "MochiyPopOne-Regular.otf"
LOGO_PATH = "hf-group-logo-78f5ba7420.png"


def load_custom_fonts():
    """フォントファイルを読み込み、失敗した場合はデフォルトフォントにフォールバック"""
    if os.path.exists(FONT_PATH):
        try:
            return {
                "header": ImageFont.truetype(FONT_PATH, 38),
                "title": ImageFont.truetype(FONT_PATH, 28),
                "badge": ImageFont.truetype(FONT_PATH, 14),
                "label": ImageFont.truetype(FONT_PATH, 15),
                "val": ImageFont.truetype(FONT_PATH, 18),
                "check": ImageFont.truetype(FONT_PATH, 15),
                "price_yen": ImageFont.truetype(FONT_PATH, 55),
                "price_val": ImageFont.truetype(FONT_PATH, 45),
                "tax_ex": ImageFont.truetype(FONT_PATH, 16),
                "footer_text": ImageFont.truetype(FONT_PATH, 10),
                "large": ImageFont.truetype(FONT_PATH, 22),
                "small": ImageFont.truetype(FONT_PATH, 12),
                "price": ImageFont.truetype(FONT_PATH, 65),
                "warranty": ImageFont.truetype(FONT_PATH, 40),
            }
        except Exception as e:
            print(f"Font load error: {e}")
    
    # フォールバック
    default_f = ImageFont.load_default()
    return {k: default_f for k in ["header", "title", "badge", "label", "val", "check", "price_yen", "price_val", "tax_ex", "footer_text", "large", "small", "price", "warranty"]}


# --- 1. ジャンク品ラベル生成関数 ---
def generate_junk_label(item_name, maker, model_num, status_choice, notes, price_tax_in, price_tax_ex, fonts):
    width, height = 500, 500
    bg_color = (255, 255, 255)
    theme_color = (13, 102, 58)
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # ヘッダー
    draw.rectangle([(0, 0), (width, 80)], fill=theme_color)
    draw.text((width // 2, 40), "ジャンク品", fill=(255, 255, 255), font=fonts["header"], anchor="mm")

    # 品名
    draw.text((15, 92), "品名", fill=theme_color, font=fonts["label"])
    draw.text((65, 90), item_name, fill=(0, 0, 0), font=fonts["val"])
    draw.line([(15, 125), (width - 15, 125)], fill=theme_color, width=2)

    # メーカー名 & 型番
    draw.text((15, 132), "メーカー名", fill=theme_color, font=fonts["label"])
    draw.text((115, 130), maker, fill=(0, 0, 0), font=fonts["val"])
    draw.text((270, 132), "型番", fill=theme_color, font=fonts["label"])
    draw.text((320, 130), model_num, fill=(0, 0, 0), font=fonts["val"])
    draw.line([(15, 168), (width - 15, 168)], fill=theme_color, width=2)

    # チェックボックス
    cb1_fill = theme_color if status_choice == 1 else None
    cb2_fill = theme_color if status_choice == 2 else None
    cb3_fill = theme_color if status_choice == 3 else None

    draw.rectangle([(15, 178), (28, 191)], outline=theme_color, fill=cb1_fill, width=2)
    draw.text((33, 175), "動作未確認", fill=theme_color, font=fonts["check"])

    draw.rectangle([(140, 178), (153, 191)], outline=theme_color, fill=cb2_fill, width=2)
    draw.text((158, 175), "電源は入りました", fill=theme_color, font=fonts["check"])

    draw.line([(15, 202), (width - 15, 202)], fill=theme_color, width=1)
    
    draw.rectangle([(15, 212), (28, 225)], outline=theme_color, fill=cb3_fill, width=2)
    draw.text((33, 209), "動作確認", fill=theme_color, font=fonts["check"])
    draw.text((140, 209), notes, fill=(0, 0, 0), font=fonts["label"])

    draw.line([(15, 245), (width - 15, 245)], fill=theme_color, width=2)

    # 価格
    draw.line([(15, 290), (width - 15, 290)], fill=theme_color, width=2)
    draw.text((25, 295), "¥", fill=theme_color, font=fonts["price_yen"])
    draw.text((120, 300), price_tax_in, fill=(0, 0, 0), font=fonts["price_val"])

    draw.line([(15, 365), (width - 15, 365)], fill=theme_color, width=2)
    draw.line([(15, 369), (width - 15, 369)], fill=theme_color, width=1)

    # 本体価格
    draw.text((15, 378), "本体価格 ¥", fill=theme_color, font=fonts["tax_ex"])
    draw.text((120, 376), price_tax_ex, fill=(0, 0, 0), font=fonts["val"])

    draw.line([(15, 410), (width - 15, 410)], fill=theme_color, width=2)

    # フッター (ロゴ描画)
    draw.rectangle([(15, 418), (width - 15, 450)], fill=theme_color)
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            max_h = 24
            aspect = logo.width / logo.height
            new_w = int(max_h * aspect)
            logo_resized = logo.resize((new_w, max_h), Image.LANCZOS)
            img.paste(logo_resized, ((width - new_w) // 2, 422), logo_resized)
        except Exception:
            draw.text((width // 2, 434), "HARD・OFF", fill=(255, 255, 255), font=fonts["val"], anchor="mm")
    else:
        draw.text((width // 2, 434), "HARD・OFF", fill=(255, 255, 255), font=fonts["val"], anchor="mm")

    draw.text((15, 455), "※買い取り時の動作確認のため目安であり保証するものではありません。", fill=theme_color, font=fonts["footer_text"])
    draw.text((15, 470), "※ジャンク品の商品保証及び、返品・交換はできません。", fill=theme_color, font=fonts["footer_text"])

    return img


# --- 2. リユース品ラベル生成関数 ---
def generate_reuse_label(item_name, maker, model_num, list_price, price_tax_in, price_tax_ex, warranty, year, description, notes, product_code, fonts):
    width, height = 700, 500
    bg_color = (250, 248, 245)
    theme_color = (205, 75, 88)
    text_color = (0, 0, 0)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # ヘッダー
    draw.rectangle([(0, 0), (width, 45)], fill=theme_color)
    draw.text((width // 2, 22), "♻ リユース品", fill=(255, 255, 255), font=fonts["title"], anchor="mm")

    # メーカー & 品名
    draw.rectangle([(20, 55), (85, 78)], fill=theme_color)
    draw.text((52, 66), "メーカー", fill=(255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((95, 53), maker, fill=text_color, font=fonts["large"])

    draw.rectangle([(380, 55), (435, 78)], fill=theme_color)
    draw.text((407, 66), "品名", fill=(255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((445, 53), item_name, fill=text_color, font=fonts["large"])
    draw.line([(20, 88), (width - 20, 88)], fill=theme_color, width=1)

    # 型番 & 定価
    draw.rectangle([(20, 95), (75, 118)], fill=theme_color)
    draw.text((47, 106), "型番", fill=(255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((85, 93), model_num, fill=text_color, font=fonts["large"])

    draw.rectangle([(380, 95), (435, 118)], fill=theme_color)
    draw.text((407, 106), "定価", fill=(255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((445, 93), list_price, fill=text_color, font=fonts["large"])
    draw.line([(20, 128), (width - 20, 128)], fill=theme_color, width=1)

    # 価格 & 保証枠
    draw.text((35, 138), "¥", fill=theme_color, font=fonts["price"])
    draw.text((125, 135), price_tax_in, fill=text_color, font=fonts["price"])
    draw.text((485, 170), "税\n込", fill=theme_color, font=fonts["small"])

    box_x1, box_y1, box_x2, box_y2 = 520, 140, 670, 255
    draw.rectangle([(box_x1, box_y1), (box_x2, box_y2)], outline=theme_color, width=2)
    draw.rectangle([(box_x1, box_y1), (box_x2, box_y1 + 22)], fill=theme_color)
    draw.text(((box_x1 + box_x2) // 2, box_y1 + 11), "保証期間", fill=(255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text(((box_x1 + box_x2) // 2, box_y1 + 58), warranty, fill=text_color, font=fonts["warranty"], anchor="mm")

    # 本体価格 & 年式
    draw.rectangle([(20, 220), (95, 240)], fill=theme_color)
    draw.text((57, 230), "本体価格", fill=(255, 255, 255), font=fonts["small"], anchor="mm")
    draw.text((100, 220), f"¥ {price_tax_ex}", fill=text_color, font=fonts["val"])

    draw.rectangle([(280, 220), (335, 240)], fill=theme_color)
    draw.text((307, 230), "年式", fill=(255, 255, 255), font=fonts["small"], anchor="mm")
    if year:
        draw.text((345, 220), year, fill=text_color, font=fonts["val"])

    draw.line([(20, 252), (490, 252)], fill=theme_color, width=1)

    # 補足 & 備考
    draw.text((25, 265), description, fill=text_color, font=fonts["val"])
    draw.line([(20, 325), (width - 20, 325)], fill=theme_color, width=1)

    draw.rectangle([(20, 335), (85, 358)], fill=theme_color)
    draw.text((52, 346), "備 考", fill=(255, 255, 255), font=fonts["badge"], anchor="mm")
    draw.text((95, 336), notes, fill=text_color, font=fonts["val"])

    draw.line([(15, 385), (width - 15, 385)], fill=theme_color, width=1)

    # 商品番号
    draw.text((330, 395), f"商品番号  {product_code}", fill=theme_color, font=fonts["val"])

    # フッター
    draw.rectangle([(0, 430), (width, 500)], fill=theme_color)
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            max_logo_h = 45
            aspect = logo.width / logo.height
            new_h = max_logo_h
            new_w = int(new_h * aspect)
            logo_resized = logo.resize((new_w, new_h), Image.LANCZOS)
            img.paste(logo_resized, ((width - new_w) // 2, 430 + (70 - new_h) // 2), logo_resized)
        except Exception:
            draw.text((width // 2, 465), "HARD・OFF", fill=(255, 255, 255), font=fonts["large"], anchor="mm")
    else:
        draw.text((width // 2, 465), "HARD・OFF", fill=(255, 255, 255), font=fonts["large"], anchor="mm")

    return img


# --- メイン実行処理 ---
def run_generator(event):
    fonts = load_custom_fonts()
    
    label_type = document.getElementById("label_type").value
    item_name = document.getElementById("item_name").value or "ノートPC"
    maker = document.getElementById("maker").value or "FUJITSU"
    model_num = document.getElementById("model_num").value or "FMV AH42/EY"
    price_tax_in = document.getElementById("price_tax_in").value or "3,300"
    price_tax_ex = document.getElementById("price_tax_ex").value or "3,000"
    notes = document.getElementById("notes").value or "・HDD欠品 ・ACなし"

    if label_type == "junk":
        status_choice = int(document.getElementById("status_choice").value)
        img = generate_junk_label(item_name, maker, model_num, status_choice, notes, price_tax_in, price_tax_ex, fonts)
    else:
        list_price = document.getElementById("list_price").value or "OPEN"
        warranty = document.getElementById("warranty").value or "3ヶ月"
        year = document.getElementById("year").value or ""
        description = document.getElementById("description").value or "動作確認済み"
        product_code = document.getElementById("product_code").value or "2013440000019187 ( 26)"
        img = generate_reuse_label(item_name, maker, model_num, list_price, price_tax_in, price_tax_ex, warranty, year, description, notes, product_code, fonts)

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    img_element = document.getElementById("output_image")
    img_element.src = f"data:image/png;base64,{img_str}"
    img_element.style.display = "block"

document.getElementById("status").innerText = "フォント・ロゴ準備完了やで！"
