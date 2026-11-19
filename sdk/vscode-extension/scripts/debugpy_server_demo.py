#!/usr/bin/env python3
"""
S&R CoreSync - debugpy Remote Server Demo
Demonstrates how debugpy listens for VS Code remote attachment.
"""
import time
import sys

def main():
    print("=" * 65)
    print("🚀 S&R CoreSync - Remote debugpy Target Server")
    print("=" * 65)
    try:
        import debugpy
        host = "localhost"
        port = 5678
        print(f"📡 جاري الاستماع على {host}:{port} بانتظار اتصال مصحح VS Code...")
        debugpy.listen((host, port))
        print("⏳ الخادم بانتظار إرفاق المصحح (Attach Debugger)...")
        # debugpy.wait_for_client() # ألغِ التعليق إن رغبت بإيقاف التنفيذ حتى يرتبط المحرر
        print("🔗 المصحح متصل بنجاح! جاري تنفيذ العمليات الحسابية والذكية...")
    except ImportError:
        print("⚠️ مكتبة debugpy غير مثبتة في البيئة الحالية. قم بتثبيتها عبر: pip install debugpy")

    iteration = 0
    while iteration < 10:
        iteration += 1
        print(f"⚡ [دورة {iteration}] معالجة مصفوفة الذكاء الاصطناعي... الوقت: {time.strftime('%X')}")
        time.sleep(1)

    print("✅ اكتملت الدورة بنجاح.")

if __name__ == "__main__":
    main()
