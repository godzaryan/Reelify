from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pyautogui
import time


# Function to log in to Instagram and upload a video
def login_and_upload_video(username, password, video_path, caption):
    # Initialize WebDriver and open Instagram login page
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get('https://www.instagram.com/accounts/login/')
    wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds

    # Enter username and password and log in
    print("Logging in...")
    wait.until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(username)
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.find_element(By.NAME, 'password').send_keys(Keys.ENTER)

    # Wait for the home page to load after login
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'svg[aria-label="Home"]')))
        print("Login successful, home page loaded.")
    except Exception as e:
        print("Error loading home page:", e)
        driver.quit()
        return

    # Click the 'New post' button using updated XPath
    try:
        print("Navigating to create new post...")
        new_post_svg = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]')))
        new_post_svg.click()

        # Wait for the new post element to load and click the specific <a> element
        print("Clicking the 'Post' link...")
        post_span = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Post" and contains(@class, "x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft")]')))
        post_span.click()

        print("Clicking the 'Select from computer' button...")
        select_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Select From Computer"]')))
        select_button.click()

    except Exception as e:
        print("Error finding 'New post' button:", e)
        driver.quit()
        return


    print("Selected video file...")
    # Step 2: Wait for the file dialog to open
    time.sleep(2)  # Adjust sleep time as needed for the file dialog to appear

    # Step 4: Type the video path and press Enter to select the file
    pyautogui.write(video_path)
    pyautogui.press('enter')




    # Wait for the next button to appear and click it
    try:
        print("Proceeding to next step...")
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="OK"]')))
        next_button.click()
    except Exception as e:
        print("Error proceeding to next step:", e)
        driver.quit()
        return

    try:
        print("Proceeding to next step...")
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Next"]')))
        next_button.click()
    except Exception as e:
        print("Error proceeding to next step:", e)
        driver.quit()
        return

    try:
        print("Proceeding to next step...")
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Next"]')))
        next_button.click()
    except Exception as e:
        print("Error proceeding to next step:", e)
        driver.quit()
        return

    # Wait for the caption area to appear and add the caption
    try:
        print("Adding caption...")

        # Locate the contenteditable div element for caption
        caption_area = wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Write a caption..."]'))
        )

        # Bring the element into view and click to focus
        driver.execute_script("arguments[0].scrollIntoView(true);", caption_area)
        caption_area.click()

        # Execute a command to insert text using JavaScript (execCommand is deprecated, but still works in many cases)
        driver.execute_script("""
                const text = arguments[1];
                const captionDiv = arguments[0];
                captionDiv.focus();
                document.execCommand('insertText', false, text);
            """, caption_area, caption)

        print("Caption added successfully.")
    except Exception as e:
        print("Error adding caption:", e)
        driver.quit()
        return

    # Click the 'Share' button to post the video
    try:
        print("Posting video...")
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Share"]')))
        next_button.click()
    except Exception as e:
        print("Error sharing the post:", e)
        driver.quit()
        return

    print("Waiting for 'Your reel has been shared.' confirmation...")

    # Wait until the element with the text "Your reel has been shared." appears on the page
    shared_confirmation = WebDriverWait(driver, 240).until(
        EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Your reel has been shared.")]'))
    )

    # Log the success and close the browser
    print("Video successfully posted!")




# Replace with your Instagram login credentials, video path, and caption
username = "movies_onyourdemand"
password = "JfHidpQ264-ubPq"
video_path = "C:\\Users\\Aryan\\Videos\\Reelify\\input_video.mp4"
caption = "This is a test video upload using Selenium!"

# Call the function to log in and upload the video
login_and_upload_video(username, password, video_path, caption)
