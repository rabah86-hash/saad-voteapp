import flet as ft
import sqlite3

# قائمة البلديات
MUNICIPALITIES = [
    "تيسمسيلت", "أولاد بسام", "خميستي", "العيون", "ثنية الحد",
    "سيدي بوتشنت", "لرجام", "ملعب", "سيدي عابد", "تملاحت",
    "برج بونعامة", "بني شعيب", "بني لحسن", "سيدي سليمان",
    "عماري", "معصم", "الأزهرية", "بوقايد", "الأربعاء",
    "برج الأمير عبد القادر", "اليوسفية", "سيدي العنتري"
]

DB_NAME = "supporters.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supporters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            municipality TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, municipality FROM supporters")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "mun": row[2]} for row in rows]

def save_data(name, mun):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO supporters (name, municipality) VALUES (?, ?)", (name, mun))
    conn.commit()
    conn.close()

def delete_voter_from_db(voter_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM supporters WHERE id = ?", (voter_id,))
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "دعم ساعد ولد قدور"
    page.rtl = True
    page.padding = 0  
    page.theme = ft.Theme(color_scheme_seed="cyan")
    page.update()

    init_db()

    name_field = ft.TextField(
        label="الاسم واللقب", 
        width=350,
        border_radius=10,
        color="#263238",
        bgcolor="white" 
    )
    
    municipality = ft.Dropdown(
        label="البلدية",
        width=350,
        border_radius=10,
        bgcolor="white",
        options=[ft.dropdown.Option(x) for x in MUNICIPALITIES]
    )

    stats = ft.Column(width=350, spacing=10)
    voters = ft.Column(width=400, spacing=10)

    def show_message(text):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text, color="white", weight="bold"),
            bgcolor="#0097A7" 
        )
        page.snack_bar.open = True
        page.update()

    def delete_voter(voter_id):
        try:
            delete_voter_from_db(voter_id)
            refresh()
            show_message("تم حذف المؤيد بنجاح.")
        except Exception as e:
            show_message(f"خطأ أثناء الحذف: {e}")

    def add_voter(e):
        if not name_field.value:
            show_message("الرجاء إدخال الاسم واللقب")
            return
        if not municipality.value:
            show_message("الرجاء اختيار البلدية")
            return

        try:
            save_data(name_field.value, municipality.value)
            name_field.value = ""
            municipality.value = None
            refresh()
            show_message("تمت إضافة المؤيد بنجاح ✨")
        except Exception as e:
            show_message(f"خطأ أثناء الحفظ: {e}")

    def refresh():
        data = load_data()
        stats.controls.clear()
        voters.controls.clear()

        stats.controls.append(
            ft.Container(
                content=ft.Text(f"إجمالي المؤيدين: {len(data)}", size=22, weight="bold", color="#1976D2", text_align="center"),
                bgcolor="#F5F5F5", padding=5, border_radius=10
            )
        )

        count = {}
        for item in data:
            mun = item["mun"]
            count[mun] = count.get(mun, 0) + 1

        for mun, total in count.items():
            stats.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon("store_rounded", size=22, color="#00BCD4"),
                        ft.Text(f"{mun}:", size=16, weight="w500"),
                        ft.Text(f"{total} مؤيد", size=16, color="#FF8F00", weight="bold")
                    ], alignment="start"),
                    padding=10,
                    bgcolor="#ffffff",
                    border_radius=10,
                )
            )

        for item in reversed(data):
            voters.controls.append(
                ft.Card(
                    elevation=3,
                    margin=5,
                    content=ft.Container(
                        padding=15,
                        border_radius=10,
                        bgcolor="white",
                        content=ft.Row(
                            controls=[
                                ft.Icon("account_circle_rounded", size=30, color="#64B5F6"),
                                ft.Column([
                                    ft.Text(f"{item['name']}", size=16, weight="bold", color="#263238"),
                                    ft.Text(f"{item['mun']}", size=14, color="#546E7A")
                                ], expand=True, spacing=2),
                                ft.IconButton(
                                    icon="delete_forever_rounded",
                                    icon_color="red",
                                    icon_size=24,
                                    tooltip="حذف نهائي",
                                    on_click=lambda e, idx=item['id']: delete_voter(idx)
                                )
                            ]
                        )
                    )
                )
            )
        page.update()

    # --- الطبقة العلوية: الواجهة والأزرار ---
    ui_layer = ft.Column(
        controls=[
            ft.Container(height=20), 
            
            ft.Container(
                content=ft.Text("دعم ساعد ولد قدور", size=28, weight="bold", color="#0D47A1"),
                bgcolor="#ffffff", padding=10, border_radius=10
            ),

            ft.Image(
                src="logo.png",  
                width=180,
                height=180,
                fit="contain",
                border_radius=15,
            ),

            name_field,
            municipality,

            ft.FilledButton(
                "إضافة مؤيد جديد",
                icon="person_add",
                width=350,
                bgcolor="#00ACC1",
                color="white",
                height=50,
                on_click=add_voter
            ),

            ft.Container(height=10),
            ft.Container(content=ft.Text("📊 إحصائيات البلديات", size=20, weight="bold", color="#0D47A1"), bgcolor="#ffffff", padding=5, border_radius=5),
            stats,

            ft.Container(height=10),
            ft.Container(content=ft.Text("👤 قائمة المؤيدين الموثقة", size=20, weight="bold", color="#0D47A1"), bgcolor="#ffffff", padding=5, border_radius=5),
            voters,
            
            ft.Container(height=10),
            ft.Container(
                content=ft.Text(
                    "نسأل الله عز وجل التوفيق والسداد وبلوغ المراد للأخ ساعد في مسيرته",
                    size=15,
                    weight="bold",
                    color="#00695C",
                    text_align="center"
                ),
                padding=10,
                bgcolor="#E0F2F1",
                border_radius=10,
                width=380
            ),

            ft.Container(height=10),
            ft.Container(
                content=ft.Column([
                    ft.Text("تم التطوير من طرف الأستاذ: بارد رابح والأستاذ: غبال محمد", size=12, color="#263238", weight="bold"),
                    ft.Text("اللهم ارحم والدي واغفر لهما كما ربياني صغيراً", size=12, color="#263238", weight="bold")
                ], horizontal_alignment="center"),
                bgcolor="#ffffff", padding=5, border_radius=10
            ),
            
            ft.Container(height=30) 
        ],
        horizontal_alignment="center",
        scroll="auto", 
        expand=True
    )

    # --- بناء نظام الطبقات المنفصلة ---
    page.add(
        ft.Stack(
            controls=[
                ft.Image(
                    src="background.png",
                    fit="cover",
                    expand=True
                ),
                ft.Container(
                    content=ui_layer,
                    padding=10,
                    expand=True
                )
            ],
            expand=True
        )
    )

    refresh()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")