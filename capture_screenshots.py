import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run():
    print("Initializing Chrome browser for real screenshot captures...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1280,950')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    os.makedirs('screenshots', exist_ok=True)

    try:
        # ==========================================
        # TASK 3: Capture 03-admin-site.png
        # ==========================================
        print("\n--- Generating Screenshot: screenshots/03-admin-site.png ---")
        driver.get("http://127.0.0.1:8000/admin/")
        time.sleep(1)

        # Log in if on login page
        username_field = driver.find_elements(By.NAME, "username")
        if username_field:
            print("Logging into Django Admin...")
            username_field[0].send_keys("admin")
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys("adminpassword123")
            submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit_btn.click()
            time.sleep(2)

        # Wait for Admin index dashboard
        wait.until(EC.presence_of_element_located((By.ID, "content-main")))
        print("Admin dashboard loaded. Current URL:", driver.current_url)
        
        # Verify both sections are present
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "authentication and authorization" in body_text.lower(), "Auth section missing"
        assert "onlinecourse" in body_text.lower(), "OnlineCourse section missing"
        print("Verified: 'Authentication and Authorization' and 'OnlineCourse' sections are both clearly visible.")

        admin_screenshot_path = os.path.abspath("screenshots/03-admin-site.png")
        driver.save_screenshot(admin_screenshot_path)
        print("Saved genuine screenshot:", admin_screenshot_path)

        # ==========================================
        # TASK 7: Complete Mock Exam & Capture 07-final.png
        # ==========================================
        print("\n--- Generating Screenshot: screenshots/07-final.png ---")
        driver.get("http://127.0.0.1:8000/onlinecourse/")
        time.sleep(1)

        # Navigate to Exam page
        driver.get("http://127.0.0.1:8000/onlinecourse/course/1/exam/")
        wait.until(EC.presence_of_element_located((By.ID, "take-exam-form")))
        print("Exam page loaded successfully. Selecting correct answers...")

        # Select correct choices for all 5 questions
        # Q1: Model-View-Template (MVT)
        # Q2: python manage.py makemigrations
        # Q3: admin.TabularInline or admin.StackedInline
        # Q4: {% for lesson in course.lesson_set.all %}
        # Q5: {% csrf_token %}
        correct_keywords = [
            "Model-View-Template (MVT)",
            "python manage.py makemigrations",
            "admin.TabularInline or admin.StackedInline",
            "{% for lesson in course.lesson_set.all %}",
            "{% csrf_token %}",
        ]

        labels = driver.find_elements(By.CSS_SELECTOR, "label.list-group-item")
        selected_count = 0
        for label in labels:
            text = label.text
            for kw in correct_keywords:
                if kw in text:
                    radio = label.find_element(By.CSS_SELECTOR, "input[type='radio']")
                    driver.execute_script("arguments[0].click();", radio)
                    selected_count += 1
                    print(f"Selected correct choice: {kw}")
                    break

        print(f"Total correct answers selected: {selected_count}")
        time.sleep(1)

        # Submit the exam form
        submit_btn = driver.find_element(By.ID, "submit-assessment-btn")
        driver.execute_script("arguments[0].click();", submit_btn)
        print("Exam submitted. Waiting for results page...")

        # Wait for results page
        wait.until(EC.presence_of_element_located((By.ID, "congratulations-banner")))
        time.sleep(1)
        print("Results page loaded. Current URL:", driver.current_url)

        # Verify results
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Congratulations! You Passed the Exam!" in body_text, "Congratulations banner missing"
        assert "100.0%" in body_text or "100%" in body_text, "100% score missing"
        assert "5 / 5" in body_text, "5 / 5 correct questions count missing"
        assert "PASSED" in body_text, "PASSED status missing"
        print("Verified: Congratulations banner, 100% score, 5/5 correct questions, and PASSED status are displayed.")

        final_screenshot_path = os.path.abspath("screenshots/07-final.png")
        driver.save_screenshot(final_screenshot_path)
        print("Saved genuine screenshot:", final_screenshot_path)

        print("\nAll genuine screenshots captured successfully!")

    finally:
        driver.quit()

if __name__ == '__main__':
    run()
