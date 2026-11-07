import { db } from "@/db";
import { sql } from "drizzle-orm";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  await db.execute(sql`select 1`);

  return (
    <main
      dir="rtl"
      lang="ar"
      style={{
        fontFamily: "'Cairo', sans-serif",
        background: "linear-gradient(135deg, #1a56db 0%, #1e3a8a 60%, #0f172a 100%)",
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 20px",
      }}
    >
      <link
        href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap"
        rel="stylesheet"
      />
      <div
        style={{
          background: "#fff",
          borderRadius: "20px",
          padding: "50px 40px",
          maxWidth: "700px",
          width: "100%",
          boxShadow: "0 30px 60px rgba(0,0,0,0.3)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            marginBottom: "24px",
          }}
        >
          <div
            style={{
              width: "60px",
              height: "60px",
              background: "linear-gradient(135deg, #1a56db, #1e40af)",
              borderRadius: "14px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "28px",
            }}
          >
            🎓
          </div>
          <div>
            <h1
              style={{
                margin: 0,
                fontSize: "24px",
                fontWeight: 800,
                color: "#1a56db",
              }}
            >
              مدرسة المستقبل الدولية
            </h1>
            <p style={{ margin: 0, fontSize: "14px", color: "#6b7280" }}>
              نظام إدارة المدرسة الشامل
            </p>
          </div>
        </div>

        <div
          style={{
            background: "#eff6ff",
            borderRadius: "12px",
            padding: "20px",
            marginBottom: "24px",
            borderRight: "4px solid #1a56db",
          }}
        >
          <h2
            style={{ margin: "0 0 8px", fontSize: "18px", color: "#1e3a8a", fontWeight: 700 }}
          >
            ✅ تم بناء المشروع بنجاح!
          </h2>
          <p style={{ margin: 0, color: "#374151", fontSize: "14px", lineHeight: 1.7 }}>
            تم إنشاء نظام إدارة المدرسة الكامل باستخدام{" "}
            <strong>Flask Framework</strong> في مجلد{" "}
            <code style={{ background: "#e5e7eb", padding: "2px 6px", borderRadius: "4px" }}>
              school_management/
            </code>
          </p>
        </div>

        <h3 style={{ color: "#1f2937", marginBottom: "16px", fontSize: "16px" }}>
          🚀 طريقة تشغيل المشروع:
        </h3>

        <div
          style={{
            background: "#0f172a",
            borderRadius: "12px",
            padding: "20px",
            marginBottom: "24px",
            fontFamily: "monospace",
            color: "#e2e8f0",
            fontSize: "13px",
            lineHeight: 1.8,
          }}
        >
          <div style={{ color: "#64748b", marginBottom: "8px" }}># 1. الانتقال إلى مجلد المشروع</div>
          <div style={{ color: "#86efac" }}>cd school_management</div>
          <br />
          <div style={{ color: "#64748b", marginBottom: "8px" }}># 2. تثبيت المتطلبات</div>
          <div style={{ color: "#86efac" }}>pip install -r requirements.txt</div>
          <br />
          <div style={{ color: "#64748b", marginBottom: "8px" }}># 3. تشغيل التطبيق</div>
          <div style={{ color: "#86efac" }}>python app.py</div>
          <br />
          <div style={{ color: "#64748b", marginBottom: "8px" }}># 4. فتح المتصفح</div>
          <div style={{ color: "#93c5fd" }}>http://127.0.0.1:5000</div>
        </div>

        <h3 style={{ color: "#1f2937", marginBottom: "16px", fontSize: "16px" }}>
          🔐 بيانات الدخول التجريبية:
        </h3>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", marginBottom: "24px" }}>
          {[
            { role: "مدير", user: "admin", pass: "admin123", color: "#ef4444", bg: "#fef2f2" },
            { role: "معلم", user: "teacher_t001", pass: "teacher123", color: "#10b981", bg: "#ecfdf5" },
            { role: "طالب", user: "student_s001", pass: "student123", color: "#1a56db", bg: "#eff6ff" },
          ].map(({ role, user, pass, color, bg }) => (
            <div
              key={role}
              style={{
                background: bg,
                borderRadius: "10px",
                padding: "14px",
                textAlign: "center",
                border: `1px solid ${color}30`,
              }}
            >
              <div
                style={{
                  color,
                  fontWeight: 700,
                  fontSize: "15px",
                  marginBottom: "8px",
                }}
              >
                {role}
              </div>
              <div style={{ fontSize: "11px", color: "#374151", lineHeight: 1.8 }}>
                <div>
                  <strong>اسم المستخدم:</strong>
                </div>
                <code style={{ fontSize: "11px" }}>{user}</code>
                <div style={{ marginTop: "4px" }}>
                  <strong>كلمة المرور:</strong>
                </div>
                <code style={{ fontSize: "11px" }}>{pass}</code>
              </div>
            </div>
          ))}
        </div>

        <h3 style={{ color: "#1f2937", marginBottom: "12px", fontSize: "16px" }}>
          📋 صفحات المشروع:
        </h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "8px",
            fontSize: "13px",
            color: "#374151",
          }}
        >
          {[
            "✅ الصفحة الرئيسية",
            "✅ من نحن",
            "✅ الكادر التعليمي",
            "✅ الأخبار والإعلانات",
            "✅ الأنشطة المدرسية",
            "✅ تواصل معنا",
            "✅ تسجيل الدخول (3 أدوار)",
            "✅ لوحة الطالب (7 صفحات)",
            "✅ لوحة المعلم (6 صفحات)",
            "✅ لوحة الإدارة (12 صفحة)",
            "✅ CRUD كامل للإدارة",
            "✅ Charts وإحصائيات",
          ].map((item) => (
            <div
              key={item}
              style={{ padding: "6px 10px", background: "#f9fafb", borderRadius: "6px" }}
            >
              {item}
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: "24px",
            padding: "16px",
            background: "#f0fdf4",
            borderRadius: "10px",
            fontSize: "13px",
            color: "#166534",
            textAlign: "center",
          }}
        >
          🏗️ مبني بـ Python | Flask | Flask-WTF | Flask-SQLAlchemy | Flask-Login | Bootstrap 5 RTL
        </div>
      </div>
    </main>
  );
}
