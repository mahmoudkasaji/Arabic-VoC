"""
Main entry point for Flask Arabic Voice of Customer Platform
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Basic routes for UX testing
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>منصة صوت العميل العربية</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; direction: rtl; }
            .nav-menu { margin: 20px 0; }
            .nav-menu a { margin: 10px; padding: 10px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .dashboard-container { margin: 20px 0; }
            .metric { display: inline-block; margin: 10px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            button { padding: 10px 15px; margin: 5px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>لوحة التحكم الرئيسية</h1>
        <div class="nav-menu">
            <a href="/feedback" id="nav-feedback">الملاحظات</a>
            <a href="/analytics" id="nav-analytics">التحليلات</a>
            <a href="/surveys" id="nav-surveys">الاستبيانات</a>
            <a href="/integrations" id="nav-integrations">التكاملات</a>
            <a href="/settings" id="nav-settings">الإعدادات</a>
        </div>
        <div class="dashboard-container">
            <div class="metric" data-metric="total-feedback">إجمالي التعليقات: 142</div>
            <div class="metric" data-metric="positive-sentiment">إيجابي: 89</div>
            <div class="metric" data-metric="negative-sentiment">سلبي: 23</div>
            <button data-action="refresh" onclick="alert('تم التحديث')">تحديث</button>
            <button data-action="export" onclick="alert('جاري التصدير')">تصدير</button>
            <button class="filter-toggle" onclick="alert('تم تطبيق التصفية')">تصفية</button>
        </div>
    </body>
    </html>
    """

@app.route('/feedback')
def feedback_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>نموذج التعليقات</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; direction: rtl; }
            form { max-width: 500px; }
            input, textarea, select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 15px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .success-message { color: green; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>نموذج إرسال التعليقات</h1>
        <form id="feedback-form" onsubmit="submitFeedback(event)">
            <textarea name="content" placeholder="اكتب تعليقك هنا..." required></textarea>
            <select name="channel">
                <option value="website">الموقع الإلكتروني</option>
                <option value="mobile">التطبيق المحمول</option>
                <option value="email">البريد الإلكتروني</option>
            </select>
            <input type="email" name="customer_email" placeholder="بريدك الإلكتروني" required>
            <button type="submit">إرسال التعليق</button>
        </form>
        <div id="message"></div>
        <script>
            function submitFeedback(event) {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                
                fetch('/api/feedback', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        content: formData.get('content'),
                        channel: formData.get('channel'),
                        customer_email: formData.get('customer_email')
                    })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('message').innerHTML = '<div class="success-message">تم إرسال التعليق بنجاح!</div>';
                    form.reset();
                })
                .catch(error => {
                    document.getElementById('message').innerHTML = '<div style="color: red;">حدث خطأ في الإرسال</div>';
                });
            }
        </script>
    </body>
    </html>
    """

@app.route('/analytics')
def analytics_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>التحليلات</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; direction: rtl; }
            .analytics-dashboard { margin: 20px 0; }
            .chart-container { width: 400px; height: 300px; background: #f8f9fa; margin: 20px 0; border-radius: 5px; display: flex; align-items: center; justify-content: center; }
            .filter-button { padding: 10px; margin: 5px; background: #17a2b8; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>لوحة التحليلات</h1>
        <div class="analytics-dashboard">
            <div data-metric="total-feedback">إجمالي التعليقات: 142</div>
            <div data-metric="avg-sentiment">متوسط المشاعر: 3.4/5</div>
            <div class="chart-container">رسم بياني للمشاعر</div>
            <button class="filter-button" onclick="applyFilter('positive')">الإيجابية فقط</button>
            <button class="filter-button" onclick="applyFilter('negative')">السلبية فقط</button>
            <button data-action="refresh" onclick="refreshData()">تحديث البيانات</button>
        </div>
        <script>
            function applyFilter(type) {
                alert('تم تطبيق تصفية: ' + type);
            }
            function refreshData() {
                alert('تم تحديث البيانات');
            }
        </script>
    </body>
    </html>
    """

@app.route('/surveys')
def surveys_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>إدارة الاستبيانات</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; direction: rtl; }
        </style>
    </head>
    <body>
        <h1>إدارة الاستبيانات</h1>
        <p>صفحة إدارة الاستبيانات</p>
        <a href="/survey-builder">إنشاء استبيان جديد</a>
    </body>
    </html>
    """

@app.route('/survey-builder')
def survey_builder():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>بناء الاستبيان</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; direction: rtl; }
            .question-types { margin: 20px 0; }
            .question-types button { margin: 5px; padding: 10px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; }
            #survey-canvas { min-height: 300px; border: 2px dashed #ddd; padding: 20px; margin: 20px 0; }
            .question-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>بناء الاستبيان</h1>
        <div class="question-types">
            <button data-question-type="text" onclick="addQuestion('text')">سؤال نصي</button>
            <button data-question-type="multiple_choice" onclick="addQuestion('multiple_choice')">اختيار متعدد</button>
            <button data-question-type="rating" onclick="addQuestion('rating')">تقييم</button>
            <button data-question-type="nps" onclick="addQuestion('nps')">مقياس NPS</button>
        </div>
        <div id="survey-canvas"></div>
        <button data-action="save" onclick="saveSurvey()">حفظ الاستبيان</button>
        <script>
            let questionCount = 0;
            function addQuestion(type) {
                questionCount++;
                const canvas = document.getElementById('survey-canvas');
                const questionElement = document.createElement('div');
                questionElement.className = 'question-item';
                questionElement.innerHTML = `
                    <h4>سؤال ${questionCount} - نوع: ${type}</h4>
                    <input type="text" name="title" placeholder="عنوان السؤال" style="width: 100%; padding: 5px;">
                `;
                canvas.appendChild(questionElement);
            }
            function saveSurvey() {
                alert('تم حفظ الاستبيان بنجاح!');
            }
        </script>
    </body>
    </html>
    """

@app.route('/settings')
def settings_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>الإعدادات</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; direction: rtl; }
            .settings-container { max-width: 600px; }
            .setting-item { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            .toggle { width: 50px; height: 25px; }
            button { padding: 15px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>إعدادات النظام</h1>
        <div class="settings-container">
            <div class="setting-item">
                <label>تفعيل الإشعارات الفورية</label>
                <input type="checkbox" class="toggle" id="notifications" onchange="toggleChanged(this)">
            </div>
            <div class="setting-item">
                <label>حفظ تلقائي للتعليقات</label>
                <input type="checkbox" class="toggle" id="autosave" checked onchange="toggleChanged(this)">
            </div>
            <div class="setting-item">
                <label>عرض الإحصائيات في الوقت الفعلي</label>
                <input type="checkbox" class="toggle" id="realtime" onchange="toggleChanged(this)">
            </div>
            <button data-action="save-settings" onclick="saveSettings()">حفظ الإعدادات</button>
        </div>
        <div id="save-message"></div>
        <script>
            function toggleChanged(toggle) {
                console.log(toggle.id + ' changed to: ' + toggle.checked);
            }
            function saveSettings() {
                document.getElementById('save-message').innerHTML = '<div style="color: green; margin-top: 10px;">تم حفظ الإعدادات بنجاح!</div>';
                setTimeout(() => {
                    document.getElementById('save-message').innerHTML = '';
                }, 3000);
            }
        </script>
    </body>
    </html>
    """

@app.route('/integrations')
def integrations_page():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>التكاملات</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; direction: rtl; }
        </style>
    </head>
    <body>
        <h1>التكاملات</h1>
        <p>صفحة إدارة التكاملات</p>
    </body>
    </html>
    """

# API endpoints for testing
@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "service": "arabic-voc-platform", "timestamp": "2025-06-22"})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    # Simulate processing
    return jsonify({
        "status": "success", 
        "message": "تم استلام التعليق بنجاح",
        "feedback_id": 123,
        "content": data.get('content', ''),
        "processed": True
    })

@app.route('/api/dashboard-metrics')
def dashboard_metrics():
    return jsonify({
        "total_feedback": 142,
        "positive_sentiment": 89,
        "negative_sentiment": 23,
        "neutral_sentiment": 30,
        "average_rating": 4.2
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)