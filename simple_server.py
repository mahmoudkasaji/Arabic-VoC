#!/usr/bin/env python3
"""
Simple HTTP server for testing the Arabic Voice of Customer platform
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os

class ArabicVoCHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "Arabic VoC Platform"}).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة صوت العميل العربية</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
               background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; 
                    padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .status { background: #27ae60; color: white; padding: 15px; 
                 border-radius: 5px; text-align: center; margin: 20px 0; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .feature { background: #ecf0f1; padding: 20px; border-radius: 8px; }
        .feature h3 { color: #34495e; margin-top: 0; }
        .api-endpoints { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .endpoint { font-family: monospace; background: #e9ecef; padding: 8px; margin: 5px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>منصة صوت العميل العربية</h1>
        <div class="status">✓ النظام يعمل بنجاح - الخدمة متاحة</div>
        
        <div class="features">
            <div class="feature">
                <h3>جمع التعليقات متعدد القنوات</h3>
                <p>دعم لأكثر من 10 قنوات: البريد الإلكتروني، الهاتف، الموقع الإلكتروني، تطبيق الهاتف، وسائل التواصل الاجتماعي، واتساب، رسائل نصية، وغيرها</p>
            </div>
            
            <div class="feature">
                <h3>تحليل المشاعر بالذكاء الاصطناعي</h3>
                <p>تكامل مع OpenAI GPT-4o لتحليل النصوص العربية وتحديد المشاعر والعواطف وتصنيف التعليقات</p>
            </div>
            
            <div class="feature">
                <h3>معالجة النصوص العربية</h3>
                <p>دعم كامل للنصوص العربية مع إعادة التشكيل والتطبيع وخوارزميات الكتابة من اليمين إلى اليسار</p>
            </div>
            
            <div class="feature">
                <h3>لوحة التحليلات الفورية</h3>
                <p>مقاييس فورية وتحليلات متقدمة مع دعم التخطيط العربي وعرض البيانات من اليمين إلى اليسار</p>
            </div>
        </div>
        
        <div class="api-endpoints">
            <h3>نقاط API المتاحة:</h3>
            <div class="endpoint">POST /api/feedback/submit - إرسال التعليقات</div>
            <div class="endpoint">GET /api/feedback/list - استرجاع قائمة التعليقات</div>
            <div class="endpoint">GET /api/analytics/dashboard - مقاييس لوحة القيادة</div>
            <div class="endpoint">GET /api/analytics/sentiment - تحليل المشاعر</div>
            <div class="endpoint">GET /health - فحص حالة النظام</div>
            <div class="endpoint">GET /docs - وثائق API التفاعلية</div>
        </div>
    </div>
</body>
</html>'''
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 5000), ArabicVoCHandler)
    print("Starting Arabic Voice of Customer platform server on port 5000...")
    server.serve_forever()