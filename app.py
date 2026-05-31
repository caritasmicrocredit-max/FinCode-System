import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="منظومة أكواد جهات التمويل", page_icon="🔎", layout="wide")

# 1. محاكاة قاعدة البيانات باستخدام Session State (حتى لا تضيع البيانات أثناء التنقل بين الصفحات)
if "approved_codes" not in st.session_state:
    st.session_state.approved_codes = {
        "MF00171007": "شركة أبو ظبي الإسلامي للتمويل متناهي الصغر - أرزاق",
        "CB01280001": "المصرف المتحد",
        "CB13000001": "البنك التجاري الدولي مصر",
        "CB14000001": "بنك بلوم - مصر",
        "CB15000001": "بنك الامارات دبى الوطنى",
        "CB17000001": "بنك قناة السويس",
        "CB19000001": "بنك ابوظبى الاول مصر",
        "CB20000001": "البنك الاهلي المتحد",
        "CB23000001": "بنك فيصل الاسلامى المصرى"
    }

if "pending_requests" not in st.session_state:
    st.session_state.pending_requests = [
        {
            "id": 0,
            "name": "أحمد علي",
            "phone": "01012345678",
            "type": "إضافة كود جديد",
            "code": "PC04000001",
            "details": "بنك مصــــر"
        }
    ]

# القائمة الجانبية للتنقل
st.sidebar.title("🧭 القائمة الرئيسية")
page = st.sidebar.radio("انتقل إلى:", ["🔎 البحث والاستبدال", "➕ تقديم طلب / اقتراح", "🔐 لوحة تحكم الأدمن"])

# ----------------------------------------
# الصفحة الأولى: البحث والاستبدال
# ----------------------------------------
if page == "🔎 البحث والاستبدال":
    st.title("🔎 برنامج البحث والاستبدال للأكواد جهات التمويل")
    st.write("مرحباً بك! يمكنك البحث عن جهة تمويل أو استبدال مجموعة أكواد بالأسماء دفعة واحدة.")
    
    tab1, tab2 = st.tabs(["🔄 استبدال جماعي للأكواد", "🔍 بحث سريع عن جهة"])
    
    with tab1:
        st.subheader("إدخل الأكواد (مفصولة بأسطر أو فواصل):")
        codes_input = st.text_area("الأكواد المدخلة", placeholder="مثال:\nCB01280001\nMF00171007", height=150)
        
        if st.button("🔄 استبدال بالأسماء", type="primary"):
            if codes_input.strip():
                # تقسيم المدخلات بناء على الأسطر أو الفواصل
                import re
                lines = re.split(r'[\s,،\n]+', codes_input.strip())
                results = []
                for code in lines:
                    if code:
                        name = st.session_state.approved_codes.get(code, "❌ غير موجود في قاعدة البيانات")
                        results.append(f"{code} ➝ {name}")
                
                st.subheader("📋 النتائج:")
                output_text = "\n".join(results)
                st.code(output_text, language="text")
            else:
                st.warning("من فضلك أدخل أكواد أولاً.")
                
    with tab2:
        st.subheader("البحث الذكي:")
        search_query = st.text_input("أدخل جزءاً من الكود أو اسم الجهة...")
        
        if search_query:
            found_results = []
            for code, name in st.session_state.approved_codes.items():
                if search_query.lower() in code.lower() or search_query in name:
                    found_results.append({"الكود": code, "اسم الجهة التمويلية": name})
            
            if found_results:
                st.success(f"تم العثور على {len(found_results)} نتيجة:")
                df = pd.DataFrame(found_results)
                st.dataframe(df, use_container_width=True)
            else:
                st.error("❌ لا توجد نتائج مطابقة لبحثك.")

# ----------------------------------------
# الصفحة الثانية: تقديم طلب أو اقتراح
# ----------------------------------------
elif page == "➕ تقديم طلب / اقتراح":
    st.title("➕ نموذج طلب إضافة / تعديل أو تقديم اقتراح")
    st.write("يسعدنا مساهمتك في تطوير قاعدة البيانات. يرجى ملء النموذج أدناه وسيتم مراجعة طلبك من قبل الإدارة.")
    
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
            
        details = st.text_area("التفاصيل أو البيان الصحيح المراد إدخاله *")
        
        submit_btn = st.form_submit_button("🚀 إرسال الطلب للإدارة")
        
        if submit_btn:
            if not user_name or not user_phone or not details:
                st.error("⚠️ يرجى ملء الحقول الإلزامية المميزة بعلامة (*)")
            else:
                # إضافة الطلب إلى قائمة الانتظار
                new_id = len(st.session_state.pending_requests)
                st.session_state.pending_requests.append({
                    "id": new_id,
                    "name": user_name,
                    "phone": user_phone,
                    "type": req_type,
                    "code": code_affected,
                    "details": details
                })
                st.success("✅ تم إرسال طلبك بنجاح! سيقوم المسؤول بمراجعته وتحديث البيانات في أقرب وقت.")

# ----------------------------------------
# الصفحة الثالثة: لوحة تحكم الأدمن
# ----------------------------------------
elif page == "🔐 لوحة تحكم الأدمن":
    st.title("🔐 إدارة النظام والموافقات")
    
    # نظام حماية بسيط بكلمة مرور
    admin_password = st.sidebar.text_input("أدخل كلمة مرور الأدمن", type="password")
    
    # يمكنك تغيير كلمة المرور هنا لما تريد
    if admin_password == "admin123":
        st.success("🔓 مرحباً بك يا أدمن. لديك الصلاحية الكاملة الآن.")
        
        st.subheader("📥 الطلبات المعلقة الحالية:")
        
        if not st.session_state.pending_requests:
            st.info("لا توجد طلبات معلقة حالياً. عمل ممتاز!")
        else:
            # عرض الطلبات في بطاقات (Cards) مع أزرار التحكم
            for req in list(st.session_state.pending_requests):
                with st.expander(f"📋 طلب من: {req['name']} | نوع الطلب: {req['type']}", expanded=True):
                    st.write(f"**رقم الهاتف:** {req['phone']}")
                    if req['code']:
                        st.write(f"**الكود المقترح:** `{req['code']}`")
                    st.write(f"**البيان / التفاصيل:** {req['details']}")
                    
                    # أزرار الموافقة والرفض
                    c1, c2, _ = st.columns([1, 1, 4])
                    with c1:
                        if st.button("✅ موافقة وإضافة", key=f"app_{req['id']}"):
                            # لو كان طلب إضافة أو تعديل أكواد نقوم بتحديث الـ approved_codes
                            if req['type'] in ["إضافة كود جديد", "تعديل اسم كود الحالي"] and req['code']:
                                st.session_state.approved_codes[req['code']] = req['details']
                                st.success(True)
                            
                            # مسح الطلب من المعلقات بعد الموافقة
                            st.session_state.pending_requests = [r for r in st.session_state.pending_requests if r['id'] != req['id']]
                            st.rerun()
                            
                    with c2:
                        if st.button("❌ رفض الطلب", key=f"rej_{req['id']}", type="danger"):
                            # مسح الطلب مباشرة
                            st.session_state.pending_requests = [r for r in st.session_state.pending_requests if r['id'] != req['id']]
                            st.error("تم رفض وحذف الطلب.")
                            st.rerun()
                            
        # عرض إحصائية سريعة لقاعدة البيانات الحالية للأدمن
        st.divider()
        st.subheader("📊 قاعدة البيانات المعتمدة الحالية:")
        st.json(st.session_state.approved_codes)
        
    elif admin_password != "":
        st.error("❌ كلمة المرور خاطئة! يرجى المحاولة مرة أخرى.")
    else:
        st.info("💡 يرجى إدخال كلمة مرور الأدمن في القائمة الجانبية لتتمكن من رؤية وإدارة الطلبات.")