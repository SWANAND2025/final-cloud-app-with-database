import os
import shutil
from pygments import highlight
from pygments.lexers import PythonLexer, HtmlDjangoLexer
from pygments.formatters import HtmlFormatter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def create_code_html(file_path, title, lexer):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    formatter = HtmlFormatter(style='monokai', linenos=True, cssclass="highlight")
    highlighted_code = highlight(code, lexer, formatter)
    css = formatter.get_style_defs('.highlight')

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        background-color: #1e1e1e;
        color: #d4d4d4;
        font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
        margin: 0;
        padding: 24px;
    }}
    .window {{
        background: #252526;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        overflow: hidden;
        border: 1px solid #333333;
    }}
    .title-bar {{
        background: #323233;
        padding: 10px 18px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #222;
    }}
    .dots {{
        display: flex;
        gap: 8px;
        margin-right: 18px;
    }}
    .dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }}
    .dot-red {{ background: #ff5f56; }}
    .dot-yellow {{ background: #ffbd2e; }}
    .dot-green {{ background: #27c93f; }}
    .filename {{
        font-size: 14px;
        font-weight: 600;
        color: #cccccc;
        letter-spacing: 0.5px;
    }}
    .code-container {{
        padding: 16px 20px;
        overflow-x: auto;
    }}
    {css}
    .highlight {{
        background: transparent !important;
        font-size: 13.5px;
        line-height: 1.5;
    }}
    .highlight pre {{
        margin: 0;
        font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
    }}
    .linenos {{
        color: #6e7681;
        padding-right: 15px;
        user-select: none;
    }}
</style>
</head>
<body>
<div class="window">
    <div class="title-bar">
        <div class="dots">
            <div class="dot dot-red"></div>
            <div class="dot dot-yellow"></div>
            <div class="dot dot-green"></div>
        </div>
        <div class="filename">IBM Coursera Project &mdash; {title}</div>
    </div>
    <div class="code-container">
        {highlighted_code}
    </div>
</div>
</body>
</html>"""
    return html

def render_html_to_image(driver, html_content, output_path, width=1280):
    temp_html_path = os.path.abspath("temp_code_preview.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    driver.get(f"file:///{temp_html_path}")
    
    total_height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
    )
    driver.set_window_size(width, total_height + 50)
    driver.save_screenshot(output_path)
    print(f"Captured {output_path} (height: {total_height}px)")
    
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

def main():
    print("Setting up Chrome headless driver...")
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--window-size=1280,1000')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=opts)

    os.makedirs("screenshots", exist_ok=True)
    submission_dir = os.path.abspath("Coursera_Final_Submission")
    os.makedirs(submission_dir, exist_ok=True)

    tasks = [
        {
            "src": "onlinecourse/models.py",
            "title": "onlinecourse/models.py (Question, Choice, Submission Models)",
            "lexer": PythonLexer(),
            "out": "screenshots/01-models.png",
        },
        {
            "src": "onlinecourse/admin.py",
            "title": "onlinecourse/admin.py (QuestionInline, ChoiceInline, LessonAdmin, QuestionAdmin)",
            "lexer": PythonLexer(),
            "out": "screenshots/02-admin-file.png",
        },
        {
            "src": "onlinecourse/templates/onlinecourse/course_details_bootstrap.html",
            "title": "onlinecourse/templates/onlinecourse/course_details_bootstrap.html",
            "lexer": HtmlDjangoLexer(),
            "out": "screenshots/04-course-details.png",
        },
        {
            "src": "onlinecourse/views.py",
            "title": "onlinecourse/views.py (submit & show_exam_result Views)",
            "lexer": PythonLexer(),
            "out": "screenshots/05-views.png",
        },
        {
            "src": "onlinecourse/urls.py",
            "title": "onlinecourse/urls.py (URL Patterns for submit & show_exam_result)",
            "lexer": PythonLexer(),
            "out": "screenshots/06-urls.png",
        },
    ]

    try:
        for t in tasks:
            html = create_code_html(t["src"], t["title"], t["lexer"])
            render_html_to_image(driver, html, t["out"])
            # Copy to Coursera_Final_Submission folder
            dest = os.path.join(submission_dir, os.path.basename(t["out"]))
            shutil.copy(t["out"], dest)

        # Copy existing verified 03-admin-site.png and 07-final.png
        shutil.copy("screenshots/03-admin-site.png", os.path.join(submission_dir, "03-admin-site.png"))
        print("Copied 03-admin-site.png to Coursera_Final_Submission")

        shutil.copy("screenshots/07-final.png", os.path.join(submission_dir, "07-final.png"))
        print("Copied 07-final.png to Coursera_Final_Submission")

    finally:
        driver.quit()

    print("\nAll 7 screenshots created and organized in Coursera_Final_Submission successfully!")

if __name__ == '__main__':
    main()
