import streamlit as st
import pandas as pd
import re
from supabase import create_client

st.set_page_config(
    page_title="مُعرّف | أكواد جهات التمويل",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== CATEGORIES & CONSTANTS =====================
CATEGORIES = [
    "البنوك المصرية (PC)",
    "البنوك التجارية (CB)",
    "البنوك المتخصصة (SB/NB)",
    "البنوك الأجنبية (FB)",
    "البنوك الاستثمارية (IB)",
    "شركات التمويل متناهي الصغر (MF)",
    "شركات التمويل العقاري (MG)",
    "شركات التأجير التمويلي (LF)",
    "شركات التمويل الاستهلاكي (RC)",
    "شركات التخصيم (FS)",
    "شركات التطوير العقاري (HS)",
    "شركات التأمين (IC)",
    "شركات أخرى (CC/UC/RA)",
]

CATEGORY_INFO = {
    "البنوك المصرية (PC)":               {"icon": "🟦", "desc": "البنوك المصرية الحكومية الكبرى", "prefix": "PC"},
    "البنوك التجارية (CB)":              {"icon": "🟦", "desc": "البنوك التجارية الخاصة والمشتركة", "prefix": "CB"},
    "البنوك المتخصصة (SB/NB)":           {"icon": "🟦", "desc": "البنوك المتخصصة والبنوك الوطنية", "prefix": "SB/NB"},
    "البنوك الأجنبية (FB)":              {"icon": "🟦", "desc": "فروع البنوك الأجنبية العاملة في مصر", "prefix": "FB"},
    "البنوك الاستثمارية (IB)":           {"icon": "🟦", "desc": "بنوك الاستثمار والتنمية", "prefix": "IB"},
    "شركات التمويل متناهي الصغر (MF)":   {"icon": "🟠", "desc": "شركات وجمعيات التمويل الأصغر", "prefix": "MF"},
    "شركات التمويل العقاري (MG)":        {"icon": "🟣", "desc": "شركات التمويل العقاري والرهن", "prefix": "MG"},
    "شركات التأجير التمويلي (LF)":       {"icon": "🟣", "desc": "شركات التأجير التمويلي (ليس)", "prefix": "LF"},
    "شركات التمويل الاستهلاكي (RC)":     {"icon": "🔴", "desc": "شركات التقسيط والتمويل الاستهلاكي", "prefix": "RC"},
    "شركات التخصيم (FS)":               {"icon": "🟡", "desc": "شركات التخصيم ورأس المال المخاطر", "prefix": "FS"},
    "شركات التطوير العقاري (HS)":        {"icon": "🟡", "desc": "شركات تطوير وإسكان", "prefix": "HS"},
    "شركات التأمين (IC)":               {"icon": "🟡", "desc": "شركات التأمين التكافلي وغيره", "prefix": "IC"},
    "شركات أخرى (CC/UC/RA)":            {"icon": "🟡", "desc": "جهات تنظيمية ومتنوعة", "prefix": "CC/UC/RA"},
}

# ===================== CSS =====================
LIGHT_CSS = """
:root {
  --sage:     #6B8F75;
  --sage-lt:  #EEF4F0;
  --sage-md:  #B8D4C0;
  --ink:      #1A202C;
  --ink-2:    #2D3748;
  --muted:    #64748B;
  --border:   #E2E8F0;
  --bg:       #F7F9FB;
  --white:    #FFFFFF;
  --rose:     #DC6B6B;
  --success:  #4D8B63;
  --card-bg:  #FFFFFF;
  --nav-bg:   #FFFFFF;
  --input-bg: #FFFFFF;
  --code-bg:  #F1F5F9;
}
"""

DARK_CSS = """
:root {
  --sage:     #7FB893;
  --sage-lt:  #1A2E22;
  --sage-md:  #2D4D38;
  --ink:      #F0F4F8;
  --ink-2:    #CBD5E0;
  --muted:    #94A3B8;
  --border:   #2D3748;
  --bg:       #0F1419;
  --white:    #1A2030;
  --rose:     #F08080;
  --success:  #68D391;
  --card-bg:  #1A2030;
  --nav-bg:   #141B26;
  --input-bg: #1E2A3A;
  --code-bg:  #0D1117;
}
"""

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
  font-family: 'Cairo', sans-serif !important;
  background: var(--bg) !important;
  direction: rtl;
  transition: background 0.3s, color 0.3s;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
section[data-testid="stSidebar"] { display: none; }

/* === NAV === */
.top-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.85rem 1.5rem;
  background: var(--nav-bg);
  border-bottom: 1px solid var(--border);
  margin: -1rem -1rem 1.5rem -1rem;
  position: sticky; top: 0; z-index: 100;
}
.nav-logo { font-size: 20px; font-weight: 700; color: var(--ink); letter-spacing: -0.5px; }
.nav-logo span { color: var(--sage); }
.nav-right { display: flex; align-items: center; gap: 0.75rem; }

/* Dark mode toggle */
.dm-toggle {
  width: 38px; height: 22px; border-radius: 11px;
  background: var(--border); border: none; cursor: pointer;
  position: relative; transition: background 0.2s;
  flex-shrink: 0;
}
.dm-toggle.on { background: var(--sage); }
.dm-toggle::after {
  content: ''; position: absolute;
  width: 16px; height: 16px; border-radius: 50%;
  background: white; top: 3px; right: 3px;
  transition: transform 0.2s;
}
.dm-toggle.on::after { transform: translateX(-16px); }

/* === HERO === */
.hero { text-align: center; padding: 2rem 1rem 1.5rem; }
.hero h2 { font-size: 28px; font-weight: 700; color: var(--ink); margin-bottom: 6px; letter-spacing: -0.5px; }
.hero p { font-size: 15px; color: var(--muted); }

/* === SEARCH WRAP === */
.search-outer { max-width: 540px; margin: 0 auto 1.5rem; }
.search-outer .stTextInput input {
  border-radius: 100px !important;
  border: 2px solid var(--border) !important;
  padding: 13px 22px !important;
  font-size: 16px !important;
  background: var(--input-bg) !important;
  color: var(--ink) !important;
  font-family: 'Cairo', sans-serif !important;
  transition: border-color 0.2s !important;
}
.search-outer .stTextInput input:focus {
  border-color: var(--sage) !important;
  box-shadow: 0 0 0 3px rgba(107,143,117,0.15) !important;
}

/* === CATEGORIES GRID === */
.cat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px,1fr)); gap: 10px; margin-bottom: 1.5rem; }
.cat-card {
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: 12px; padding: 14px 16px;
  cursor: default;
}
.cat-card-icon { font-size: 20px; margin-bottom: 6px; }
.cat-card-name { font-size: 14px; font-weight: 600; color: var(--ink); margin-bottom: 3px; }
.cat-card-desc { font-size: 12px; color: var(--muted); }
.cat-card-count { font-size: 12px; font-weight: 700; color: var(--sage); margin-top: 6px; }

/* === RESULT TABLE === */
.stDataFrame { border: none !important; }
.stDataFrame th {
  background: var(--sage-lt) !important;
  color: var(--sage) !important;
  font-weight: 600 !important; font-size: 13px !important;
  padding: 11px 14px !important; border: none !important;
}
.stDataFrame td {
  padding: 10px 14px !important; font-size: 14px !important;
  color: var(--ink) !important;
  border-bottom: 1px solid var(--border) !important;
  border-left: none !important; border-right: none !important;
  background: var(--card-bg) !important;
}
.stDataFrame tr:last-child td { border-bottom: none !important; }
.stDataFrame tr:hover td { background: var(--sage-lt) !important; }

/* === TEXTAREA === */
.stTextArea textarea {
  border-radius: 12px !important; border: 2px solid var(--border) !important;
  font-family: 'IBM Plex Mono', monospace !important; font-size: 14px !important;
  line-height: 1.7 !important; background: var(--input-bg) !important;
  color: var(--ink) !important; direction: ltr;
}
.stTextArea textarea:focus { border-color: var(--sage) !important; }

/* === INPUTS === */
.stTextInput input {
  border-radius: 10px !important; border: 1.5px solid var(--border) !important;
  font-family: 'Cairo', sans-serif !important; font-size: 15px !important;
  background: var(--input-bg) !important; color: var(--ink) !important;
}
.stTextInput input:focus { border-color: var(--sage) !important; box-shadow: 0 0 0 3px rgba(107,143,117,0.12) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label {
  font-size: 13px !important; font-weight: 600 !important; color: var(--ink-2) !important;
}
div[data-baseweb="select"] > div {
  border-radius: 10px !important; border: 1.5px solid var(--border) !important;
  background: var(--input-bg) !important; color: var(--ink) !important;
}

/* === BUTTONS === */
.stButton button {
  border-radius: 100px !important; font-family: 'Cairo', sans-serif !important;
  font-weight: 600 !important; font-size: 14px !important;
  padding: 9px 22px !important; transition: all 0.15s !important;
  border: 1.5px solid var(--border) !important;
  background: var(--card-bg) !important; color: var(--ink) !important;
}
.stButton button:hover {
  background: var(--ink) !important; color: var(--bg) !important;
  border-color: var(--ink) !important; transform: translateY(-1px) !important;
}
.stButton button[kind="primary"] {
  background: var(--sage) !important; color: white !important; border-color: var(--sage) !important;
}
.stButton button[kind="primary"]:hover { background: #4D7A5A !important; border-color: #4D7A5A !important; }

/* === CARDS === */
.info-card {
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 0.75rem;
}
.stat-box {
  background: var(--card-bg); border: 1px solid var(--border);
  border-radius: 12px; padding: 1rem 1.25rem; text-align: center;
}
.stat-num { font-size: 26px; font-weight: 700; color: var(--sage); }
.stat-lbl { font-size: 12px; color: var(--muted); margin-top: 2px; }

/* === REQ CARD === */
.req-card {
  background: var(--card-bg); border: 1px solid var(--border);
  border-right: 4px solid var(--sage); border-radius: 12px;
  padding: 1rem 1.25rem; margin-bottom: 0.75rem;
}
.req-type {
  display: inline-block; padding: 3px 11px; border-radius: 100px;
  font-size: 12px; font-weight: 600; background: var(--sage-lt); color: var(--sage); margin-bottom: 6px;
}
.req-meta { font-size: 13px; color: var(--muted); }
.req-detail {
  font-size: 14px; color: var(--ink-2); background: var(--bg);
  border-radius: 8px; padding: 9px 13px; margin-top: 8px; border: 1px solid var(--border);
}

/* === TABS === */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important; gap: 2px !important;
  border-bottom: 2px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 0 !important; font-family: 'Cairo', sans-serif !important;
  font-size: 14px !important; font-weight: 600 !important; color: var(--muted) !important;
  padding: 9px 18px !important; background: transparent !important;
  border-bottom: 2px solid transparent !important; margin-bottom: -2px !important;
}
.stTabs [aria-selected="true"] { color: var(--sage) !important; border-bottom-color: var(--sage) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem !important; }

/* === MISC === */
[data-testid="stForm"] { border: none !important; padding: 0 !important; }
.section-title {
  font-size: 16px; font-weight: 700; color: var(--ink); margin-bottom: 0.75rem;
  padding-bottom: 8px; border-bottom: 1px solid var(--border);
}
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--sage);
  display: inline-block; margin-left: 7px; vertical-align: middle; }
hr { border: none; border-top: 1px solid var(--border); margin: 1.25rem 0; }
.badge {
  display: inline-block; padding: 2px 10px; border-radius: 100px; font-size: 12px;
  font-weight: 600; background: var(--sage-lt); color: var(--sage); font-family: 'IBM Plex Mono', monospace;
}
.stSuccess { border-radius: 10px !important; }
.stError { border-radius: 10px !important; }
.stWarning { border-radius: 10px !important; }
.stInfo { border-radius: 10px !important; }
"""

# ===================== DARK MODE STATE =====================
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

theme_css = DARK_CSS if st.session_state["dark_mode"] else LIGHT_CSS

st.markdown(f"<style>{theme_css}{BASE_CSS}</style>", unsafe_allow_html=True)

# ===================== Supabase =====================
@st.cache_resource
def get_supabase():
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    return create_client(URL, KEY)

supabase = get_supabase()

# ===================== Session State =====================
for key, default in [
    ("admin_logged_in", False),
    ("page", "search"),
    ("search_q", ""),
    ("admin_search", ""),
    ("qa_success", []),
    ("edit_row", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ===================== NAV =====================
pages = {
    "search": "◈ بحث سريع",
    "bulk":   "⇄ استبدال جماعي",
    "submit": "+ تقديم طلب",
    "admin":  "⚙ الإدارة",
}

dm_icon = "🌙" if not st.session_state["dark_mode"] else "☀️"
dm_label = f"{dm_icon} الوضع الداكن" if not st.session_state["dark_mode"] else f"{dm_icon} الوضع الفاتح"

nav_cols = st.columns([3] + [1]*len(pages) + [1])
with nav_cols[0]:
    st.markdown('<div style="padding-top:6px"><span style="font-size:19px;font-weight:700;color:var(--ink)">مُعرّف <span style="color:var(--sage)">◈</span></span></div>', unsafe_allow_html=True)

for i, (key, label) in enumerate(pages.items()):
    with nav_cols[i+1]:
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if st.session_state["page"]==key else "secondary"):
            st.session_state["page"] = key
            st.rerun()

with nav_cols[-1]:
    if st.button(dm_label, key="dm_btn", use_container_width=True):
        st.session_state["dark_mode"] = not st.session_state["dark_mode"]
        st.rerun()

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

page = st.session_state["page"]

# ===================== HELPER =====================
def pill(text, color="sage"):
    colors = {"sage": ("var(--sage-lt)","var(--sage)"), "rose": ("#FFEBEB","var(--rose)"), "success": ("#EBFAF1","var(--success)")}
    bg, fg = colors.get(color, colors["sage"])
    return f'<span style="background:{bg};color:{fg};font-size:12px;font-weight:600;padding:3px 11px;border-radius:100px;font-family:Cairo,sans-serif">{text}</span>'

# ============================================================
# PAGE 1 — QUICK SEARCH
# ============================================================
if page == "search":
    st.markdown("""
    <div class="hero">
      <h2>ابحث عن أي جهة تمويلية</h2>
      <p>اكتب الكود أو اسم الجهة أو التصنيف — والنتائج تظهر فوراً</p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="search-outer">', unsafe_allow_html=True)
    st.text_input("", placeholder="🔍  ابدأ الكتابة...",
                  label_visibility="collapsed", key="search_q",
                  on_change=lambda: None)
    st.markdown('</div>', unsafe_allow_html=True)

    query = st.session_state["search_q"].strip()

    if query:
        resp = supabase.table("entities").select(
            "code, name, category, sub_category, is_active"
        ).or_(
            f"code.ilike.%{query}%,name.ilike.%{query}%,category.ilike.%{query}%"
        ).execute()

        if resp.data:
            count = len(resp.data)
            st.markdown(f'<div style="text-align:center;margin-bottom:1rem">{pill(f"{count} نتيجة")}</div>',
                        unsafe_allow_html=True)

            df = pd.DataFrame(resp.data)
            df.columns = ["الكود", "اسم الجهة", "التصنيف", "الفرعي", "نشط"]
            df["نشط"] = df["نشط"].map({True: "✓ نشط", False: "✗ موقوف"})

            # Show table + per-row edit request button
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            with st.expander("🖊 طلب تعديل على أحد النتائج"):
                sel_code = st.selectbox("اختر الكود المراد تعديله",
                    options=[r["code"] for r in resp.data],
                    format_func=lambda c: f"{c}  —  {next((r['name'] for r in resp.data if r['code']==c), '')}")
                sel_detail = st.text_area("الاسم الصحيح أو التفصيل المطلوب", height=90, key="inline_detail")
                user_name_inline = st.text_input("اسمك", key="inline_name")
                user_phone_inline = st.text_input("واتساب", key="inline_phone")
                if st.button("إرسال طلب التعديل", type="primary", key="inline_submit"):
                    if sel_detail and user_name_inline and user_phone_inline:
                        supabase.table("entity_suggestions").insert({
                            "user_name": user_name_inline.strip(),
                            "user_phone": user_phone_inline.strip(),
                            "req_type": "تعديل اسم كود الحالي",
                            "code_affected": sel_code,
                            "details": sel_detail.strip()
                        }).execute()
                        st.success("✅ تم إرسال طلب التعديل!")
                    else:
                        st.error("يرجى ملء جميع الحقول")
        else:
            st.markdown("""
            <div style="text-align:center;padding:2.5rem;color:var(--muted)">
              <div style="font-size:36px;opacity:.3;margin-bottom:8px">◌</div>
              <div style="font-size:15px;font-weight:500">لا توجد نتائج مطابقة</div>
              <div style="font-size:13px;margin-top:4px">جرّب بحثاً مختلفاً أو قدّم طلب إضافة</div>
            </div>""", unsafe_allow_html=True)
    else:
        # Show categories overview
        st.markdown('<div class="section-title"><span class="dot"></span>نبذة عن قاعدة البيانات</div>',
                    unsafe_allow_html=True)

        # Count per category from DB (cached)
        @st.cache_data(ttl=120)
        def get_counts():
            r = supabase.table("entities").select("category").execute()
            counts = {}
            for row in r.data:
                c = row.get("category") or "أخرى"
                counts[c] = counts.get(c, 0) + 1
            return counts

        try:
            counts = get_counts()
        except Exception:
            counts = {}

        html_cats = '<div class="cat-grid">'
        for cat, info in CATEGORY_INFO.items():
            # match any key containing prefix
            prefix = info["prefix"].split("/")[0]
            count = sum(v for k, v in counts.items() if prefix.lower() in k.lower()) if counts else 0
            count_str = f"{count} جهة" if count else "—"
            html_cats += f"""
            <div class="cat-card">
              <div class="cat-card-icon">{info['icon']}</div>
              <div class="cat-card-name">{cat}</div>
              <div class="cat-card-desc">{info['desc']}</div>
              <div class="cat-card-count">{count_str}</div>
            </div>"""
        html_cats += "</div>"
        st.markdown(html_cats, unsafe_allow_html=True)

# ============================================================
# PAGE 2 — BULK REPLACE
# ============================================================
elif page == "bulk":
    st.markdown('<div class="section-title"><span class="dot"></span>استبدال جماعي للأكواد</div>',
                unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);font-size:14px;margin-bottom:1rem">أدخل الأكواد مفصولة بأسطر أو فواصل.</p>',
                unsafe_allow_html=True)

    codes_input = st.text_area("الأكواد المدخلة", placeholder="CB13000001\nMF00171007\nRC00290001", height=150)

    c1, c2 = st.columns([1, 5])
    with c1:
        run = st.button("⇄  استبدال", type="primary", use_container_width=True)

    if run:
        if codes_input.strip():
            input_codes = [c.strip() for c in re.split(r'[\s,،\n]+', codes_input.strip()) if c.strip()]
            if input_codes:
                with st.spinner("جارٍ البحث..."):
                    resp = supabase.table("entities").select("code, name").in_(
                        "code", input_codes).eq("is_active", True).execute()
                db_map = {r["code"]: r["name"] for r in resp.data}

                found, not_found, lines = [], [], []
                for code in input_codes:
                    name = db_map.get(code)
                    if name:
                        lines.append(f"{code}  →  {name}")
                        found.append(code)
                    else:
                        lines.append(f"{code}  →  ❌ غير موجود")
                        not_found.append(code)

                c1, c2, c3 = st.columns(3)
                c1.markdown(f'<div class="stat-box"><div class="stat-num">{len(input_codes)}</div><div class="stat-lbl">إجمالي</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="stat-box"><div class="stat-num" style="color:var(--success)">{len(found)}</div><div class="stat-lbl">تم التعرف</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="stat-box"><div class="stat-num" style="color:var(--rose)">{len(not_found)}</div><div class="stat-lbl">غير موجود</div></div>', unsafe_allow_html=True)

                st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                st.code("\n".join(lines), language="text")
        else:
            st.warning("من فضلك أدخل أكواداً أولاً.")

# ============================================================
# PAGE 3 — SUBMIT REQUEST
# ============================================================
elif page == "submit":
    st.markdown('<div class="section-title"><span class="dot"></span>تقديم طلب أو اقتراح</div>',
                unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);font-size:14px;margin-bottom:1.25rem">يسعدنا مساهمتك — سيتم مراجعة طلبك قريباً.</p>',
                unsafe_allow_html=True)

    with st.form("submit_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            user_name = st.text_input("الاسم بالكامل *")
        with c2:
            user_phone = st.text_input("رقم الواتساب *")

        req_type = st.selectbox("نوع الطلب *", [
            "إضافة كود جديد", "تعديل اسم كود الحالي", "اقتراح / شكوى عامة"])

        code_affected = ""
        if req_type in ["إضافة كود جديد", "تعديل اسم كود الحالي"]:
            code_affected = st.text_input("الكود المعني", placeholder="CB12345678")

        details = st.text_area("التفاصيل *", height=100)
        submitted = st.form_submit_button("إرسال الطلب ←", type="primary")

        if submitted:
            if not user_name.strip() or not user_phone.strip() or not details.strip():
                st.error("⚠️ يرجى ملء الحقول الإلزامية *")
            else:
                resp = supabase.table("entity_suggestions").insert({
                    "user_name": user_name.strip(),
                    "user_phone": user_phone.strip(),
                    "req_type": req_type,
                    "code_affected": code_affected.strip() or None,
                    "details": details.strip()
                }).execute()
                if resp.data:
                    st.success("✅ تم إرسال طلبك بنجاح!")
                else:
                    st.error("❌ حدث خطأ، يرجى المحاولة مرة أخرى.")

# ============================================================
# PAGE 4 — ADMIN
# ============================================================
elif page == "admin":
    st.markdown('<div class="section-title"><span class="dot"></span>لوحة تحكم الإدارة</div>',
                unsafe_allow_html=True)

    if not st.session_state["admin_logged_in"]:
        pw_col, _ = st.columns([1, 2])
        with pw_col:
            pw = st.text_input("كلمة المرور", type="password", placeholder="ادخل كلمة المرور...")
            if st.button("دخول ←", type="primary"):
                if pw == st.secrets.get("ADMIN_PASSWORD", "admin123"):
                    st.session_state["admin_logged_in"] = True
                    st.rerun()
                else:
                    st.error("كلمة مرور غير صحيحة")
    else:
        tab_req, tab_ents, tab_quick, tab_edit = st.tabs([
            "📥 الطلبات المعلقة",
            "📋 عرض وبحث",
            "⚡ إدخال سريع",
            "✏️ تعديل مباشر",
        ])

        # ---------- TAB 1: PENDING REQUESTS ----------
        with tab_req:
            resp = supabase.table("entity_suggestions").select("*").execute()
            reqs = resp.data or []

            if not reqs:
                st.markdown('<div style="text-align:center;padding:2rem;color:var(--muted)"><div style="font-size:32px">✓</div><div>لا توجد طلبات معلقة</div></div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="margin-bottom:0.75rem">{pill(f"{len(reqs)} طلب معلق")}</div>',
                            unsafe_allow_html=True)

                @st.fragment
                def show_req(req):
                    st.markdown(f"""
                    <div class="req-card">
                      <span class="req-type">{req['req_type']}</span>
                      <div class="req-meta">👤 {req['user_name']} &nbsp;·&nbsp; 📱 {req['user_phone']}</div>
                      {'<div class="req-meta">🔑 الكود: <b>' + req['code_affected'] + '</b></div>' if req.get('code_affected') else ''}
                      <div class="req-detail">{req['details']}</div>
                    </div>""", unsafe_allow_html=True)

                    ca, cb, _ = st.columns([1, 1, 4])
                    with ca:
                        if st.button("✓ موافقة", key=f"app_{req['id']}", type="primary"):
                            if req.get("code_affected") and req["req_type"] == "تعديل اسم كود الحالي":
                                supabase.table("entities").update(
                                    {"name": req["details"]}
                                ).eq("code", req["code_affected"]).execute()
                            elif req.get("code_affected") and req["req_type"] == "إضافة كود جديد":
                                supabase.table("entities").insert({
                                    "code": req["code_affected"],
                                    "name": req["details"],
                                    "is_active": True
                                }).execute()
                            supabase.table("entity_suggestions").delete().eq("id", req["id"]).execute()
                            st.rerun()
                    with cb:
                        if st.button("✗ رفض", key=f"rej_{req['id']}"):
                            supabase.table("entity_suggestions").delete().eq("id", req["id"]).execute()
                            st.rerun()

                for req in reqs:
                    show_req(req)

        # ---------- TAB 2: BROWSE & SEARCH ----------
        with tab_ents:
            def do_admin_search():
                pass

            st.text_input("بحث سريع", placeholder="كود أو اسم...", key="admin_search",
                          on_change=do_admin_search)
            q_admin = st.session_state["admin_search"].strip()

            if q_admin:
                r = supabase.table("entities").select("*").or_(
                    f"code.ilike.%{q_admin}%,name.ilike.%{q_admin}%"
                ).execute()
            else:
                r = supabase.table("entities").select("*").limit(60).execute()

            if r.data:
                df2 = pd.DataFrame(r.data)
                st.dataframe(df2, use_container_width=True, hide_index=True)

                # Edit button: pick a row and jump to edit tab
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                with st.expander("✏️ تعديل أحد النتائج مباشرة"):
                    sel = st.selectbox("اختر الكود",
                        options=[x["code"] for x in r.data],
                        format_func=lambda c: f"{c}  —  {next((x['name'] for x in r.data if x['code']==c),'')}")
                    if st.button("انتقل للتعديل", type="primary", key="goto_edit"):
                        st.session_state["edit_row"] = next((x for x in r.data if x["code"]==sel), None)
                        st.rerun()
            else:
                st.info("لا توجد نتائج")

        # ---------- TAB 3: QUICK ADD ----------
        with tab_quick:
            st.markdown('<p style="color:var(--muted);font-size:14px;margin-bottom:1rem">أدخل الأكواد مباشرة — الفورم يُمسح تلقائياً بعد كل حفظ.</p>',
                        unsafe_allow_html=True)

            with st.form("quick_add_form", clear_on_submit=True):
                qa1, qa2 = st.columns(2)
                with qa1:
                    qa_code = st.text_input("الكود *", placeholder="CB12345678")
                with qa2:
                    qa_name = st.text_input("اسم الجهة *", placeholder="اسم الجهة...")

                qa3, qa4 = st.columns(2)
                with qa3:
                    qa_cat = st.selectbox("التصنيف", ["— اختر —"] + CATEGORIES)
                with qa4:
                    qa_sub = st.text_input("التصنيف الفرعي (اختياري)")

                qa_active = st.selectbox("الحالة", ["نشط", "موقوف"])
                save_btn = st.form_submit_button("⚡ حفظ وأدخل التالي", type="primary", use_container_width=True)

                if save_btn:
                    if not qa_code.strip() or not qa_name.strip():
                        st.error("الكود والاسم مطلوبان")
                    else:
                        existing = supabase.table("entities").select("code").eq("code", qa_code.strip()).execute()
                        if existing.data:
                            st.warning(f"⚠️ الكود {qa_code.strip()} موجود مسبقاً")
                        else:
                            supabase.table("entities").insert({
                                "code": qa_code.strip(),
                                "name": qa_name.strip(),
                                "category": qa_cat if qa_cat != "— اختر —" else None,
                                "sub_category": qa_sub.strip() or None,
                                "is_active": qa_active == "نشط"
                            }).execute()
                            st.session_state["qa_success"].append({"code": qa_code.strip(), "name": qa_name.strip()})
                            st.rerun()

            if st.session_state["qa_success"]:
                added = st.session_state["qa_success"]
                st.markdown(f'<div style="margin:1rem 0 0.5rem">{pill(f"✓ تمت إضافة {len(added)} كود في هذه الجلسة")}</div>',
                            unsafe_allow_html=True)
                st.markdown('<div style="border:1px solid var(--border);border-radius:12px;overflow:hidden">', unsafe_allow_html=True)
                for item in reversed(added):
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:10px;padding:9px 14px;border-bottom:1px solid var(--border);font-size:14px">
                      <span class="badge">{item['code']}</span>
                      <span style="color:var(--ink-2);flex:1">{item['name']}</span>
                      <span style="color:var(--success);font-size:12px">✓</span>
                    </div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                if st.button("مسح السجل", key="clear_qa"):
                    st.session_state["qa_success"] = []
                    st.rerun()

        # ---------- TAB 4: DIRECT EDIT ----------
        with tab_edit:
            edit = st.session_state.get("edit_row")

            if not edit:
                st.markdown('<p style="color:var(--muted);font-size:14px;margin-bottom:1rem">ابحث عن الجهة في تاب "عرض وبحث" ثم اضغط "انتقل للتعديل"، أو ابحث هنا مباشرة.</p>',
                            unsafe_allow_html=True)
                direct_code = st.text_input("ابحث بالكود مباشرة", placeholder="CB13000001", key="direct_edit_code")
                if direct_code.strip():
                    r2 = supabase.table("entities").select("*").eq("code", direct_code.strip()).execute()
                    if r2.data:
                        st.session_state["edit_row"] = r2.data[0]
                        st.rerun()
                    else:
                        st.error("الكود غير موجود")
            else:
                st.markdown(f'<div style="margin-bottom:1rem">{pill("وضع التعديل")} <span style="font-family:IBM Plex Mono,monospace;font-size:14px;color:var(--muted);margin-right:8px">{edit["code"]}</span></div>',
                            unsafe_allow_html=True)

                with st.form("edit_form"):
                    ef1, ef2 = st.columns(2)
                    with ef1:
                        new_name = st.text_input("اسم الجهة", value=edit.get("name",""))
                    with ef2:
                        new_cat = st.selectbox("التصنيف",
                            options=["— اختر —"] + CATEGORIES,
                            index=(CATEGORIES.index(edit["category"])+1) if edit.get("category") in CATEGORIES else 0)

                    ef3, ef4 = st.columns(2)
                    with ef3:
                        new_sub = st.text_input("التصنيف الفرعي", value=edit.get("sub_category","") or "")
                    with ef4:
                        new_active = st.selectbox("الحالة",
                            ["نشط","موقوف"],
                            index=0 if edit.get("is_active") else 1)

                    sb1, sb2 = st.columns(2)
                    with sb1:
                        save_edit = st.form_submit_button("💾 حفظ التعديل", type="primary", use_container_width=True)
                    with sb2:
                        cancel = st.form_submit_button("إلغاء", use_container_width=True)

                    if save_edit:
                        supabase.table("entities").update({
                            "name": new_name.strip(),
                            "category": new_cat if new_cat != "— اختر —" else None,
                            "sub_category": new_sub.strip() or None,
                            "is_active": new_active == "نشط"
                        }).eq("code", edit["code"]).execute()
                        st.session_state["edit_row"] = None
                        st.success(f"✅ تم تعديل {edit['code']} بنجاح")
                        st.rerun()

                    if cancel:
                        st.session_state["edit_row"] = None
                        st.rerun()

        # Logout
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        if st.button("تسجيل الخروج", key="logout"):
            st.session_state["admin_logged_in"] = False
            st.rerun()