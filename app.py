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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --sage:    #7C9A85;
  --sage-lt: #EEF4F0;
  --sage-md: #C8DDD0;
  --indigo:  #4A5568;
  --ink:     #1A202C;
  --ink-2:   #2D3748;
  --muted:   #718096;
  --border:  #E2E8F0;
  --bg:      #FAFBFC;
  --white:   #FFFFFF;
  --rose:    #E07B7B;
  --amber:   #D4933A;
  --success: #5A9B6E;
}

html, body, [class*="css"] {
  font-family: 'Cairo', sans-serif !important;
  background: var(--bg) !important;
  direction: rtl;
}

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
section[data-testid="stSidebar"] { display: none; }

/* === TOP NAV === */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: var(--white);
  border-bottom: 1px solid var(--border);
  margin: -1rem -1rem 2rem -1rem;
  position: sticky; top: 0; z-index: 100;
}
.nav-logo {
  font-size: 22px;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.5px;
}
.nav-logo span { color: var(--sage); }
.nav-links { display: flex; gap: 0.5rem; }
.nav-pill {
  padding: 7px 18px;
  border-radius: 100px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--muted);
  transition: all 0.15s;
  font-family: 'Cairo', sans-serif;
}
.nav-pill:hover { background: var(--sage-lt); color: var(--sage); }
.nav-pill.active { background: var(--ink); color: white; }

/* === HERO / SEARCH PAGE === */
.hero { text-align: center; padding: 2.5rem 1rem 2rem; }
.hero h2 {
  font-size: 32px; font-weight: 700;
  color: var(--ink); margin-bottom: 8px;
  letter-spacing: -1px;
}
.hero p { font-size: 16px; color: var(--muted); }

/* === SEARCH BOX === */
.search-wrap {
  max-width: 560px; margin: 0 auto 2rem;
  position: relative;
}
.search-wrap .stTextInput input {
  border-radius: 100px !important;
  border: 2px solid var(--border) !important;
  padding: 14px 24px !important;
  font-size: 16px !important;
  background: var(--white) !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
  font-family: 'Cairo', sans-serif !important;
  transition: border-color 0.2s !important;
}
.search-wrap .stTextInput input:focus {
  border-color: var(--sage) !important;
  box-shadow: 0 0 0 4px rgba(124,154,133,0.12) !important;
}

/* === RESULT TABLE === */
.stDataFrame { border: none !important; }
.stDataFrame table {
  border-collapse: collapse;
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
}
.stDataFrame th {
  background: var(--sage-lt) !important;
  color: var(--sage) !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  padding: 12px 16px !important;
  border: none !important;
}
.stDataFrame td {
  padding: 11px 16px !important;
  font-size: 14px !important;
  border-bottom: 1px solid var(--border) !important;
  border-left: none !important; border-right: none !important;
}
.stDataFrame tr:last-child td { border-bottom: none !important; }
.stDataFrame tr:hover td { background: var(--sage-lt) !important; }

/* === TEXTAREA === */
.stTextArea textarea {
  border-radius: 12px !important;
  border: 2px solid var(--border) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 14px !important;
  line-height: 1.7 !important;
  background: var(--white) !important;
  direction: ltr;
}
.stTextArea textarea:focus {
  border-color: var(--sage) !important;
  box-shadow: 0 0 0 4px rgba(124,154,133,0.12) !important;
}

/* === BUTTONS === */
.stButton button {
  border-radius: 100px !important;
  font-family: 'Cairo', sans-serif !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 10px 24px !important;
  transition: all 0.15s !important;
  border: 1px solid var(--border) !important;
  background: var(--white) !important;
  color: var(--ink) !important;
}
.stButton button:hover {
  background: var(--ink) !important;
  color: white !important;
  border-color: var(--ink) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
}
[data-testid="baseButton-primary"] button,
.stButton button[kind="primary"] {
  background: var(--sage) !important;
  color: white !important;
  border-color: var(--sage) !important;
}
[data-testid="baseButton-primary"] button:hover,
.stButton button[kind="primary"]:hover {
  background: var(--ink) !important;
  border-color: var(--ink) !important;
}

/* === RESULT CODE BLOCK === */
.stCode {
  border-radius: 12px !important;
  border: 1px solid var(--border) !important;
  font-family: 'IBM Plex Mono', monospace !important;
}

/* === CARDS / CONTAINERS === */
.result-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}
.stat-row {
  display: flex; gap: 1rem; margin-bottom: 1.5rem;
}
.stat-box {
  flex: 1; background: var(--white);
  border: 1px solid var(--border);
  border-radius: 12px; padding: 1rem 1.25rem;
  text-align: center;
}
.stat-num { font-size: 28px; font-weight: 700; color: var(--sage); }
.stat-lbl { font-size: 12px; color: var(--muted); margin-top: 2px; }

/* === FORM INPUTS === */
.stTextInput input:not(.search-wrap .stTextInput input) {
  border-radius: 10px !important;
  border: 1.5px solid var(--border) !important;
  font-family: 'Cairo', sans-serif !important;
  font-size: 15px !important;
  background: var(--white) !important;
}
.stTextInput input:focus {
  border-color: var(--sage) !important;
  box-shadow: 0 0 0 3px rgba(124,154,133,0.12) !important;
}
.stSelectbox select, div[data-baseweb="select"] {
  border-radius: 10px !important;
  font-family: 'Cairo', sans-serif !important;
}

/* === LABELS === */
.stTextInput label, .stTextArea label, .stSelectbox label {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: var(--ink-2) !important;
  margin-bottom: 4px !important;
}

/* === ALERTS === */
.stSuccess {
  border-radius: 12px !important;
  border: 1px solid #A8D5B5 !important;
  background: #F0FAF4 !important;
}
.stError {
  border-radius: 12px !important;
  border: 1px solid #F5C0C0 !important;
  background: #FFF5F5 !important;
}
.stWarning {
  border-radius: 12px !important;
  border: 1px solid #F0D5A0 !important;
  background: #FFFBF0 !important;
}
.stInfo {
  border-radius: 12px !important;
  border: 1px solid var(--sage-md) !important;
  background: var(--sage-lt) !important;
}

/* === ADMIN CARD === */
.req-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-right: 4px solid var(--sage);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1rem;
}
.req-type {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  background: var(--sage-lt);
  color: var(--sage);
  margin-bottom: 8px;
}
.req-meta { font-size: 13px; color: var(--muted); margin-bottom: 4px; }
.req-detail {
  font-size: 15px; color: var(--ink-2);
  background: var(--bg);
  border-radius: 8px; padding: 10px 14px;
  margin-top: 8px; border: 1px solid var(--border);
}

/* hide st form border */
[data-testid="stForm"] {
  border: none !important;
  padding: 0 !important;
}

/* === TABS OVERRIDE === */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  gap: 4px !important;
  border-bottom: 2px solid var(--border) !important;
  padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 0 !important;
  font-family: 'Cairo', sans-serif !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  color: var(--muted) !important;
  padding: 10px 20px !important;
  background: transparent !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -2px !important;
}
.stTabs [aria-selected="true"] {
  color: var(--sage) !important;
  border-bottom-color: var(--sage) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  padding-top: 1.5rem !important;
}

/* SECTION HEADING */
.section-title {
  font-size: 18px; font-weight: 700;
  color: var(--ink); margin-bottom: 1rem;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.dot { width: 8px; height: 8px; border-radius: 50%;
  background: var(--sage); display: inline-block;
  margin-left: 8px; vertical-align: middle; }

/* DIVIDER */
hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ===================== Supabase =====================
@st.cache_resource
def get_supabase():
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    return create_client(URL, KEY)

supabase = get_supabase()

# ===================== Session State =====================
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "search"
if "search_q" not in st.session_state:
    st.session_state["search_q"] = ""
if "admin_search" not in st.session_state:
    st.session_state["admin_search"] = ""

# ===================== NAV =====================
pages = {
    "search": "◈ بحث سريع",
    "bulk":   "⇄ استبدال جماعي",
    "submit": "+ تقديم طلب",
    "admin":  "⚙ الإدارة",
}

nav_html = '<div class="nav-bar"><div class="nav-logo">مُعرّف <span>◈</span></div><div class="nav-links">'
for key, label in pages.items():
    active = "active" if st.session_state["page"] == key else ""
    nav_html += f'<button class="nav-pill {active}" onclick="void(0)">{label}</button>'
nav_html += '</div></div>'

st.markdown(nav_html, unsafe_allow_html=True)

col_nav = st.columns(len(pages))
for i, (key, label) in enumerate(pages.items()):
    with col_nav[i]:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state["page"] = key
            st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

page = st.session_state["page"]

# ============================================================
# PAGE 1 — QUICK SEARCH
# ============================================================
if page == "search":
    st.markdown("""
    <div class="hero">
      <h2>ابحث عن أي جهة تمويلية</h2>
      <p>بحث فوري في قاعدة البيانات المعتمدة بالكود أو الاسم أو التصنيف</p>
    </div>
    """, unsafe_allow_html=True)

    def do_search():
        pass  # triggers rerun on every keystroke

    with st.container():
        st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
        st.text_input(
            "", placeholder="🔍  اكتب كود أو اسم جهة...",
            label_visibility="collapsed",
            key="search_q",
            on_change=do_search
        )
        st.markdown('</div>', unsafe_allow_html=True)

    query = st.session_state["search_q"]

    if query:
        response = supabase.table("entities").select(
            "code, name, category, sub_category, is_active"
        ).or_(
            f"code.ilike.%{query}%,name.ilike.%{query}%,category.ilike.%{query}%"
        ).execute()

        if response.data:
            count = len(response.data)
            st.markdown(f"""
            <div style="text-align:center; margin-bottom:1rem;">
              <span style="background:var(--sage-lt); color:var(--sage); font-size:13px;
                font-weight:600; padding:5px 16px; border-radius:100px; font-family:'Cairo'">
                {count} نتيجة
              </span>
            </div>""", unsafe_allow_html=True)

            df = pd.DataFrame(response.data)
            df.columns = ["الكود", "اسم الجهة", "التصنيف", "الفرعي", "نشط"]
            df["نشط"] = df["نشط"].map({True: "✓ نشط", False: "✗ موقوف"})
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:3rem; color:var(--muted)">
              <div style="font-size:40px; margin-bottom:8px">◌</div>
              <div style="font-size:16px; font-weight:500">لا توجد نتائج مطابقة</div>
              <div style="font-size:13px; margin-top:4px">جرّب بحثاً مختلفاً أو قدّم طلب إضافة</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:var(--muted)">
          <div style="font-size:48px; margin-bottom:8px; opacity:0.3">◈</div>
          <div style="font-size:15px">ابدأ الكتابة للبحث الفوري</div>
        </div>""", unsafe_allow_html=True)

# ============================================================
# PAGE 2 — BULK REPLACE
# ============================================================
elif page == "bulk":
    st.markdown('<div class="section-title"><span class="dot"></span>استبدال جماعي للأكواد</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted); font-size:14px; margin-bottom:1rem">أدخل الأكواد مفصولة بأسطر أو فواصل وسيتم استبدالها بأسماء الجهات.</p>', unsafe_allow_html=True)

    codes_input = st.text_area(
        "الأكواد المدخلة",
        placeholder="CB13000001\nMF00171007\nCB14000001",
        height=160
    )

    c1, c2 = st.columns([1, 4])
    with c1:
        run = st.button("⇄  استبدال", type="primary", use_container_width=True)

    if run:
        if codes_input.strip():
            input_codes = [c.strip() for c in re.split(r'[\s,،\n]+', codes_input.strip()) if c.strip()]
            if input_codes:
                with st.spinner("جارٍ البحث..."):
                    resp = supabase.table("entities").select("code, name").in_(
                        "code", input_codes
                    ).eq("is_active", True).execute()
                db_map = {row['code']: row['name'] for row in resp.data}

                found, not_found = [], []
                lines = []
                for code in input_codes:
                    name = db_map.get(code)
                    if name:
                        lines.append(f"{code}  →  {name}")
                        found.append(code)
                    else:
                        lines.append(f"{code}  →  ❌ غير موجود")
                        not_found.append(code)

                # stats
                sc1, sc2, sc3 = st.columns(3)
                sc1.markdown(f'<div class="stat-box"><div class="stat-num">{len(input_codes)}</div><div class="stat-lbl">إجمالي الأكواد</div></div>', unsafe_allow_html=True)
                sc2.markdown(f'<div class="stat-box"><div class="stat-num" style="color:var(--success)">{len(found)}</div><div class="stat-lbl">تم التعرف عليها</div></div>', unsafe_allow_html=True)
                sc3.markdown(f'<div class="stat-box"><div class="stat-num" style="color:var(--rose)">{len(not_found)}</div><div class="stat-lbl">غير موجودة</div></div>', unsafe_allow_html=True)

                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                st.markdown('<div class="section-title" style="font-size:15px"><span class="dot"></span>النتائج</div>', unsafe_allow_html=True)
                st.code("\n".join(lines), language="text")
        else:
            st.warning("من فضلك أدخل أكواداً أولاً.")

# ============================================================
# PAGE 3 — SUBMIT REQUEST
# ============================================================
elif page == "submit":
    st.markdown('<div class="section-title"><span class="dot"></span>تقديم طلب أو اقتراح</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted); font-size:14px; margin-bottom:1.5rem">يسعدنا مساهمتك في تطوير قاعدة البيانات — سيتم مراجعة طلبك من قبل الإدارة.</p>', unsafe_allow_html=True)

    with st.form("submit_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            user_name = st.text_input("الاسم بالكامل *")
        with c2:
            user_phone = st.text_input("رقم الواتساب *")

        req_type = st.selectbox("نوع الطلب *", [
            "إضافة كود جديد",
            "تعديل اسم كود الحالي",
            "اقتراح / شكوى عامة"
        ])

        code_affected = ""
        if req_type in ["إضافة كود جديد", "تعديل اسم كود الحالي"]:
            code_affected = st.text_input("الكود المعني", placeholder="مثال: CB12345678")

        details = st.text_area("التفاصيل أو الاسم الصحيح *", height=120)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("إرسال الطلب ←", type="primary", use_container_width=False)

        if submitted:
            if not user_name.strip() or not user_phone.strip() or not details.strip():
                st.error("⚠️ يرجى ملء جميع الحقول الإلزامية *")
            else:
                with st.spinner("جارٍ الإرسال..."):
                    data = {
                        "user_name": user_name.strip(),
                        "user_phone": user_phone.strip(),
                        "req_type": req_type,
                        "code_affected": code_affected.strip() or None,
                        "details": details.strip()
                    }
                    resp = supabase.table("entity_suggestions").insert(data).execute()

                if resp.data:
                    st.success("✅ تم إرسال طلبك بنجاح! سيتم مراجعته قريباً.")
                else:
                    st.error("❌ حدث خطأ أثناء الإرسال، يرجى المحاولة مرة أخرى.")

# ============================================================
# PAGE 4 — ADMIN PANEL
# ============================================================
elif page == "admin":
    st.markdown('<div class="section-title"><span class="dot"></span>لوحة تحكم الإدارة</div>', unsafe_allow_html=True)

    if not st.session_state["admin_logged_in"]:
        st.markdown('<p style="color:var(--muted); font-size:14px">أدخل كلمة المرور للوصول</p>', unsafe_allow_html=True)
        pw_col, _ = st.columns([1, 2])
        with pw_col:
            pw = st.text_input("كلمة المرور", type="password", label_visibility="collapsed",
                               placeholder="كلمة المرور...")
            if st.button("دخول ←", type="primary"):
                if pw == st.secrets.get("ADMIN_PASSWORD", "admin123"):
                    st.session_state["admin_logged_in"] = True
                    st.rerun()
                else:
                    st.error("كلمة مرور غير صحيحة")
    else:
        tab_req, tab_entities, tab_quickadd = st.tabs(["📥  الطلبات المعلقة", "📋  إدارة الأكواد", "⚡  إدخال سريع"])

        # ---- TAB 1: Pending requests ----
        with tab_req:
            resp = supabase.table("entity_suggestions").select("*").execute()
            reqs = resp.data or []

            if not reqs:
                st.markdown("""
                <div style="text-align:center; padding:3rem; color:var(--muted)">
                  <div style="font-size:36px; margin-bottom:8px">✓</div>
                  <div style="font-size:15px; font-weight:500">لا توجد طلبات معلقة</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin-bottom:1rem">
                  <span style="background:var(--sage-lt); color:var(--sage); font-size:13px;
                    font-weight:600; padding:5px 14px; border-radius:100px; font-family:'Cairo'">
                    {len(reqs)} طلب معلق
                  </span>
                </div>""", unsafe_allow_html=True)

                @st.fragment
                def show_req(req):
                    st.markdown(f"""
                    <div class="req-card">
                      <span class="req-type">{req['req_type']}</span>
                      <div class="req-meta">👤 {req['user_name']}  &nbsp;·&nbsp;  📱 {req['user_phone']}</div>
                      {'<div class="req-meta">🔑 الكود: <b>' + req['code_affected'] + '</b></div>' if req.get('code_affected') else ''}
                      <div class="req-detail">{req['details']}</div>
                    </div>""", unsafe_allow_html=True)

                    ca, cb, _ = st.columns([1, 1, 4])
                    with ca:
                        if st.button("✓ موافقة", key=f"app_{req['id']}", type="primary"):
                            if req.get("code_affected") and req["req_type"] != "إضافة كود جديد":
                                supabase.table("entities").update(
                                    {"name": req["details"]}
                                ).eq("code", req["code_affected"]).execute()
                            supabase.table("entity_suggestions").delete().eq("id", req["id"]).execute()
                            st.rerun()
                    with cb:
                        if st.button("✗ رفض", key=f"rej_{req['id']}"):
                            supabase.table("entity_suggestions").delete().eq("id", req["id"]).execute()
                            st.rerun()

                for req in reqs:
                    show_req(req)

        # ---- TAB 2: Manage entities ----
        with tab_entities:
            st.markdown('<p style="color:var(--muted); font-size:14px; margin-bottom:1rem">عرض وتعديل وإضافة جهات في قاعدة البيانات</p>', unsafe_allow_html=True)

            def do_admin_search():
                pass

            st.text_input("بحث سريع", placeholder="كود أو اسم جهة...", key="admin_search", on_change=do_admin_search)
            search_admin = st.session_state["admin_search"]

            if search_admin:
                r = supabase.table("entities").select("*").or_(
                    f"code.ilike.%{search_admin}%,name.ilike.%{search_admin}%"
                ).execute()
            else:
                r = supabase.table("entities").select("*").limit(50).execute()

            if r.data:
                df2 = pd.DataFrame(r.data)
                st.dataframe(df2, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد نتائج")

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="section-title" style="font-size:15px"><span class="dot"></span>إضافة كود جديد</div>', unsafe_allow_html=True)

            with st.form("add_entity"):
                fc1, fc2 = st.columns(2)
                with fc1:
                    new_code = st.text_input("الكود", placeholder="CB12345678")
                with fc2:
                    new_name = st.text_input("اسم الجهة")
                fc3, fc4 = st.columns(2)
                with fc3:
                    new_cat = st.text_input("التصنيف الرئيسي")
                with fc4:
                    new_sub = st.text_input("التصنيف الفرعي")
                add_btn = st.form_submit_button("إضافة ←", type="primary")
                if add_btn:
                    if new_code and new_name:
                        supabase.table("entities").insert({
                            "code": new_code.strip(),
                            "name": new_name.strip(),
                            "category": new_cat.strip() or None,
                            "sub_category": new_sub.strip() or None,
                            "is_active": True
                        }).execute()
                        st.success(f"✅ تمت إضافة {new_code} بنجاح")
                        st.rerun()
                    else:
                        st.error("الكود والاسم مطلوبان")

        # ---- TAB 3: Quick direct entry ----
        with tab_quickadd:
            st.markdown('<p style="color:var(--muted); font-size:14px; margin-bottom:1.5rem">أدخل أكواداً جديدة مباشرة واحداً تلو الآخر بدون أي خطوات إضافية.</p>', unsafe_allow_html=True)

            # Initialize quick-add session state
            if "qa_success" not in st.session_state:
                st.session_state["qa_success"] = []

            with st.form("quick_add_form", clear_on_submit=True):
                qa1, qa2 = st.columns(2)
                with qa1:
                    qa_code = st.text_input("الكود *", placeholder="CB12345678", key="qa_code_input")
                with qa2:
                    qa_name = st.text_input("اسم الجهة *", placeholder="البنك / الشركة...", key="qa_name_input")

                qa3, qa4, qa5 = st.columns(3)
                with qa3:
                    qa_cat = st.text_input("التصنيف", placeholder="بنك / شركة تمويل...", key="qa_cat")
                with qa4:
                    qa_sub = st.text_input("الفرعي", placeholder="اختياري", key="qa_sub")
                with qa5:
                    qa_active = st.selectbox("الحالة", ["نشط", "موقوف"], key="qa_active")

                save_btn = st.form_submit_button("⚡  حفظ وأدخل التالي", type="primary", use_container_width=True)

                if save_btn:
                    if not qa_code.strip() or not qa_name.strip():
                        st.error("الكود واسم الجهة مطلوبان")
                    else:
                        # Check if code already exists
                        existing = supabase.table("entities").select("code").eq("code", qa_code.strip()).execute()
                        if existing.data:
                            st.warning(f"⚠️ الكود {qa_code.strip()} موجود مسبقاً في قاعدة البيانات")
                        else:
                            supabase.table("entities").insert({
                                "code": qa_code.strip(),
                                "name": qa_name.strip(),
                                "category": qa_cat.strip() or None,
                                "sub_category": qa_sub.strip() or None,
                                "is_active": qa_active == "نشط"
                            }).execute()
                            st.session_state["qa_success"].append(
                                {"code": qa_code.strip(), "name": qa_name.strip()}
                            )
                            st.rerun()

            # Show running log of what was added this session
            if st.session_state["qa_success"]:
                count_added = len(st.session_state["qa_success"])
                st.markdown(f"""
                <div style="margin-top:1.5rem">
                  <div style="font-size:13px; font-weight:600; color:var(--sage); margin-bottom:10px">
                    ✓ تمت إضافة {count_added} كود في هذه الجلسة
                  </div>
                  <div style="border:1px solid var(--border); border-radius:12px; overflow:hidden;">""",
                unsafe_allow_html=True)

                for item in reversed(st.session_state["qa_success"]):
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; gap:12px; padding:10px 16px;
                      border-bottom:1px solid var(--border); font-size:14px;">
                      <span style="background:var(--sage-lt); color:var(--sage); font-size:12px;
                        font-weight:600; padding:3px 10px; border-radius:6px;
                        font-family:'IBM Plex Mono',monospace">{item['code']}</span>
                      <span style="color:var(--ink-2)">{item['name']}</span>
                      <span style="margin-right:auto; color:var(--success); font-size:12px">✓ تمت الإضافة</span>
                    </div>""", unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)

                if st.button("مسح السجل", key="clear_qa_log"):
                    st.session_state["qa_success"] = []
                    st.rerun()

        # Logout
        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        if st.button("تسجيل الخروج", key="logout"):
            st.session_state["admin_logged_in"] = False
            st.rerun()