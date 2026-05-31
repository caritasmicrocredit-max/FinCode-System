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
# الصفحة الثالثة: لوحة تحكم الأدمن التلقائية المستقرة والمحمية بنظام الـ Callbacks
# ----------------------------------------
elif page == "🔐 لوحة تحكم الأدمن":
    st.title("🔐 إدارة النظام والموافقات والأكواد")
    
    # التحقق من حالة الدخول السابقة أو استقبال كلمة مرور جديدة
    if not st.sidebar.get("admin_logged_in", False) and "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        admin_password = st.sidebar.text_input("أدخل كلمة مرور الأدمن", type="password")
        if admin_password == "admin123": # يمكنك تعديل الباسورد هنا
            st.session_state["admin_logged_in"] = True
            st.rerun()
        elif admin_password != "":
            st.sidebar.error("❌ كلمة المرور خاطئة!")
    
    # عرض اللوحة فقط إذا كان الأدمن مسجل الدخول في الذاكرة
    if st.session_state["admin_logged_in"]:
        st.success("🔓 مرحباً بك يا أدمن. متصل بقاعدة البيانات بشكل كامل وصلاحيات الإدراج مفعلة.")
        
        # خيار لتسجيل الخروج من لوحة التحكم في القائمة الجانبية
        if st.sidebar.button("🔒 تسجيل الخروج من لوحة الأدمن"):
            st.session_state["admin_logged_in"] = False
            st.rerun()
            
        st.subheader("📥 الطلبات والاقتراحات المعلقة الحالية:")
        
        # جلب الطلبات من جدول entity_suggestions
        requests_response = supabase.table("entity_suggestions").select("*").execute()
        pending_list = requests_response.data
        
        if not pending_list:
            st.info("لا توجد طلبات معلقة حالياً في قاعدة البيانات.")
        else:
            # دالة مستقلة للموافقة والاعتماد (تم نقلها خارج الواجهة لضمان الاستقرار)
            def approve_request(req_data, record_id):
                try:
                    if req_data.get('req_type') in ["إضافة كود جديد", "تعديل اسم كود الحالي"] and req_data.get('code_affected'):
                        # تحديد الفئة التقريبية للكود الجديد لتصنيفه تلقائياً
                        code_prefix = str(req_data['code_affected'])[:2].upper()
                        category_map = {
                            "CB": "بنوك", "FB": "بنوك", "IB": "بنوك", 
                            "MF": "تمويل متناهي الصغر", "LF": "تأجير تمويلي", 
                            "FS": "تخصيم", "MG": "تمويل عقاري وإسكان", 
                            "HS": "تمويل عقاري وإسكان", "RC": "تمويل استهلاكي / شركات تجارية"
                        }
                        determined_cat = category_map.get(code_prefix, "أخرى")

                        # تحديث البيانات في جدول الأكواد الرئيسي
                        supabase.table("entities").upsert({
                            "code": req_data['code_affected'].strip(),
                            "name": req_data['details'].strip(),
                            "category": determined_cat,
                            "is_active": True
                        }, on_conflict="code").execute()
                    
                    # حذف الطلب من جدول الاقتراحات
                    supabase.table("entity_suggestions").delete().eq("id", record_id).execute()
                except Exception as e:
                    pass

            # دالة مستقلة للرفض والحذف
            def reject_request(record_id):
                try:
                    supabase.table("entity_suggestions").delete().eq("id", record_id).execute()
                except Exception as e:
                    pass

            # عرض الطلبات باستخدام حلقة تكرارية آمنة تعتمد على الطابع الزمني والـ UUID المطور للـ Keys
            for idx, req in enumerate(pending_list):
                # تأمين تصنيع معرف فريد جداً ومستحيل التكرار في الذاكرة لكل عنصر واجهة
                req_id = req.get('id', idx)
                unique_key_suffix = f"__id_{req_id}__idx_{idx}__code_{req.get('code_affected', 'none')}"
                
                # إنشاء صندوق حاوية منفصل معزول برمجياً تماماً
                with st.container(border=True):
                    st.markdown(f"### 📋 طلب من: **{req.get('user_name', 'مجهول')}**")
                    st.write(f"**نوع الطلب:** {req.get('req_type', 'عام')}")
                    st.write(f"**رقم الهاتف:** {req.get('user_phone', 'غير مسجل')}")
                    
                    if req.get('code_affected'):
                        st.write(f"**الكود المعني:** `{req['code_affected']}`")
                        
                    st.info(f"**البيان / الاسم المقترح:** {req.get('details', '')}")
                    
                    # إنشاء الأزرار بشكل مباشر مع ربطها بالـ Callbacks وتمرير المعطيات كـ args
                    c1, c2, _ = st.columns([1, 1, 3])
                    with c1:
                        st.button(
                            "✅ موافقة واعتماد", 
                            key=f"btn_approve_{unique_key_suffix}", 
                            type="primary",
                            on_click=approve_request,
                            args=(req, req_id)
                        )
                    with c2:
                        st.button(
                            "❌ رفض وحذف", 
                            key=f"btn_reject_{unique_key_suffix}", 
                            type="danger",
                            on_click=reject_request,
                            args=(req_id,)
                        )
                            
        st.divider()
        st.subheader("📊 معاينة سريعة لآخر 5 جهات تم تحديثها في جدولك الفعلي (entities):")
        total_response = supabase.table("entities").select("code, name, updated_at").order("updated_at", desc=True).limit(5).execute()
        if total_response.data:
            st.dataframe(pd.DataFrame(total_response.data), use_container_width=True)
    else:
        st.info("💡 يرجى إدخال كلمة مرور الأدمن في القائمة الجانبية لتتمكن من التحكم وتحديث الأكواد.")