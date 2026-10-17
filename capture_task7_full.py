import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run():
    print("Initializing Chrome browser for full-page screenshot of 07-final.png...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1280,1000')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        # Navigate to Exam page
        print("Opening exam page...")
        driver.get("http://127.0.0.1:8000/onlinecourse/course/1/exam/")
        wait.until(EC.presence_of_element_located((By.ID, "take-exam-form")))
        print("Exam page loaded successfully. Selecting all 5 correct answers...")

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
        print("Results page loaded:", driver.current_url)

        # Verify all elements
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Congratulations! You Passed the Exam!" in body_text
        assert "100.0%" in body_text or "100%" in body_text
        assert "5 / 5" in body_text
        assert "PASSED" in body_text
        assert "Question 1" in body_text and "Question 2" in body_text and "Question 3" in body_text and "Question 4" in body_text and "Question 5" in body_text

        print("Verification passed! Resizing window to capture entire document from top to bottom...")

        # Dynamically calculate the total document height to capture the full page
        total_height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
        )
        print(f"Calculated full document height: {total_height}px")
        
        # Set browser window size to full height + margin
        driver.set_window_size(1280, total_height + 100)
        time.sleep(1)

        final_screenshot_path = os.path.abspath("screenshots/07-final.png")
        driver.save_screenshot(final_screenshot_path)
        print(f"Saved complete full-page screenshot to: {final_screenshot_path}")

        file_size = os.path.getsize(final_screenshot_path)
        print(f"Screenshot size: {file_size} bytes")

    finally:
        driver.quit()

if __name__ == '__main__':
    run()
