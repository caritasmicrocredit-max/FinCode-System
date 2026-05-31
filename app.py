import streamlit as st
import pandas as pd
import re
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="منظومة مُعرّف لأكواد التمويل", page_icon="🔎", layout="wide")

# ===================== اتصال Supabase =====================
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# تهيئة حالة تسجيل الدخول للأدمن في الذاكرة لتجنب الخروج التلقائي
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

# القائمة الجانبية للتنقل
st.sidebar.title("🧭 القائمة الرئيسية")
page = st.sidebar.radio("انتقل إلى:", ["🔎 البحث والاستبدال", "➕ تقديم طلب / اقتراح", "🔐 لوحة تحكم الأدمن"])

# ----------------------------------------
# الصفحة الأولى: البحث والاستبدال (تعتمد على جدول entities)
# ----------------------------------------
if page == "🔎 البحث والاستبدال":
    st.title("🔎 برنامج البحث والاستبدال للأكواد جهات التمويل")
    st.write("مرحباً بك! يمكنك البحث السريع أو الاستبدال الجماعي للأكواد مباشرة من قاعدة البيانات المعتمدة.")
    
    tab1, tab2 = st.tabs(["🔄 استبدال جماعي للأكواد", "🔍 بحث سريع عن جهة"])
    
    with tab1:
        st.subheader("أدخل الأكواد (مفصولة بأسطر أو فواصل):")
        codes_input = st.text_area("الأكواد المدخلة", placeholder="مثال:\nCB13000001\nMF00171007", height=150)
        
        if st.button("🔄 استبدال بالأسماء", type="primary"):
            if codes_input.strip():
                # تقسيم المدخلات بناء على الأسطر أو الفواصل وتنظيفها
                input_codes = [c.strip() for c in re.split(r'[\s, Gram,،\n]+', codes_input.strip()) if c.strip()]
                
                if input_codes:
                    # جلب الأكواد من جدولك الفعلي entities (فقط الحسابات النشطة)
                    response = supabase.table("entities").select("code, name").in_("code", input_codes).eq("is_active", True).execute()
                    db_map = {row['code']: row['name'] for row in response.data}
                    
                    results = []
                    for code in input_codes:
                        name = db_map.get(code, "❌ غير موجود في قاعدة البيانات أو غير نشط")
                        results.append(f"{code} ➝ {name}")
                    
                    st.subheader("📋 النتائج:")
                    st.code("\n".join(results), language="text")
            else:
                st.warning("من فضلك أدخل أكواد أولاً.")
                
    with tab2:
        st.subheader("البحث الذكي:")
        search_query = st.text_input("أدخل جزءاً من الكود، اسم الجهة، أو التصنيف...")
        
        if search_query:
            # البحث الذكي في الكود أو الاسم أو الـ Category داخل جدول entities
            response = supabase.table("entities").select("code, name, category, sub_category, is_active").or_(
                f"code.ilike.%{search_query}%,name.ilike.%{search_query}%,category.ilike.%{search_query}%"
            ).execute()
            
            if response.data:
                st.success(f"تم العثور على {len(response.data)} نتيجة:")
                df = pd.DataFrame(response.data)
                df.columns = ["الكود", "اسم الجهة التمويلية", "التصنيف الرئيسي", "التصنيف الفرعي", "حالة النشاط"]
                st.dataframe(df, use_container_width=True)
            else:
                st.error("❌ لا توجد نتائج مطابقة لبحثك.")

# ----------------------------------------
# الصفحة الثانية: تقديم طلب أو اقتراح (تعتمد على جدول entity_suggestions)
# ----------------------------------------
elif page == "➕ تقديم طلب / اقتراح":
    st.title("➕ نموذج طلب إضافة / تعديل أو تقديم اقتراح")
    st.write("يسعدنا مساهمتك في تطوير قاعدة البيانات. يرجى ملء النموذج أدناه وسيتم مراجعة طلبك من قبل المسئول.")
    
    with st.form("request_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("الاسم بالكامل *")
        with col2:
            user_phone = st.text_input("رقم الهاتف للتواصل (واتساب) *")
            
        req_type = st.selectbox("نوع الطلب *", ["إضافة كود جديد", "تعديل اسم كود الحالي", "اقتراح / شكوى عامة"])
        
        code_affected = ""
        if req_type in ["إضافة كود جديد", "تعديل اسم كود الحالي"]:
            code_affected = st.text_input("الكود المعني (مثال: CB12345678)")
            
        details = st.text_area("التفاصيل أو الاسم الصحيح المراد إدخاله *")
        
        submit_btn = st.form_submit_button("🚀 إرسال الطلب للإدارة")
        
        if submit_btn:
            if not user_name or not user_phone or not details:
                st.error("⚠️ يرجى ملء الحقول الإلزامية المميزة بعلامة (*)")
            else:
                # إدراج الطلب مباشرة في الجدول الجديد entity_suggestions
                data_to_insert = {
                    "user_name": user_name.strip(),
                    "user_phone": user_phone.strip(),
                    "req_type": req_type,
                    "code_affected": code_affected.strip() if code_affected else None,
                    "details": details.strip()
                }
                response = supabase.table("entity_suggestions").insert(data_to_insert).execute()
                
                if response.data:
                    st.success("✅ تم إرسال طلبك بنجاح وحفظه في قاعدة البيانات! سيقوم المسؤول بمراجعته قريباً.")
                else:
                    st.error("❌ حدث خطأ أثناء إرسال الطلب، يرجى المحاولة مرة أخرى.")

# ----------------------------------------
# الصفحة الثالثة: لوحة تحكم الأدمن (نظام الـ Fragments المطور)
# ----------------------------------------
elif page == "🔐 لوحة تحكم الأدمن":
    st.title("🔐 إدارة النظام والموافقات والأكواد")

    # تهيئة الجلسة
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        password = st.sidebar.text_input("كلمة المرور", type="password")
        if password == "admin123":
            st.session_state["admin_logged_in"] = True
            st.rerun()
    else:
        # استخدام st.fragment لعزل الطلبات عن بقية الصفحة ومنع تداخل الـ Keys
        @st.fragment
        def render_request(req):
            with st.container(border=True):
                st.write(f"📋 **الطلب:** {req['req_type']} | **الكود:** `{req.get('code_affected', 'N/A')}`")
                st.write(f"👤 {req['user_name']} - 📱 {req['user_phone']}")
                st.info(f"البيان: {req['details']}")
                
                col1, col2 = st.columns(2)
                
                if col1.button("✅ موافقة", key=f"app_{req['id']}"):
                    # 1. تحديث الجدول الأساسي
                    if req['code_affected']:
                        supabase.table("entities").update({"name": req['details']}).eq("code", req['code_affected']).execute()
                    
                    # 2. حذف الطلب
                    supabase.table("entity_suggestions").delete().eq("id", req['id']).execute()
                    st.rerun()
                    
                if col2.button("❌ رفض", key=f"rej_{req['id']}"):
                    supabase.table("entity_suggestions").delete().eq("id", req['id']).execute()
                    st.rerun()

        st.subheader("📥 الطلبات المعلقة:")
        response = supabase.table("entity_suggestions").select("*").execute()
        
        if not response.data:
            st.info("لا توجد طلبات.")
        else:
            for req in response.data:
                render_request(req)