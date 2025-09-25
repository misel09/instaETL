from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from kafka import KafkaProducer
import time
import json
import concurrent.futures
import re

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def clean_number(text):
    """Extracts and returns only the numeric part from a string, handling K/M abbreviations."""
    if not text:
        return "N/A"
    text = text.replace(",", "").replace(" ", "")
    match = re.search(r"([\d\.]+)([kKmM]?)", text)
    if not match:
        return "N/A"
    num, suffix = match.groups()
    try:
        num = float(num)
        if suffix.lower() == 'k':
            num *= 1_000
        elif suffix.lower() == 'm':
            num *= 1_000_000
        return int(num)
    except Exception:
        return "N/A"

def scrape_profile(target, credential):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-minimized")
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    # Step 1: Login to Instagram
    driver.get("https://www.instagram.com/accounts/login/")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(credential["username"])
    password_input.send_keys(credential["password"])
    password_input.send_keys(Keys.RETURN)

    # Handle "Save Your Login Info?" popup
    try:
        time.sleep(6)
        not_now_btn = driver.find_element(By.XPATH, "//button[contains(., 'Not now') or contains(., 'Not Now')]")
        not_now_btn.click()
        time.sleep(2)
        print("Clicked 'Not now' on login info popup.")
    except Exception:
        print("No 'Save Your Login Info?' popup appeared.")

    # Step 2: Go to the business profile
    driver.get(f"https://www.instagram.com/{target}/")
    time.sleep(5)

    posts = followers = following = "N/A"
    try:
        stats = driver.find_elements(By.XPATH, "//header//li")
        if len(stats) >= 3:
            posts = clean_number(stats[0].find_element(By.TAG_NAME, "span").text)
            followers_span = driver.find_element(By.XPATH, "//header//li[2]//span[contains(@class, 'x5n08af')]")
            followers_text = followers_span.get_attribute("title") or followers_span.text
            followers = clean_number(followers_text)
            following = clean_number(stats[2].find_element(By.TAG_NAME, "span").text)
            print(f"Profile: {target}, Posts: {posts}, Followers: {followers}, Following: {following}")
    except Exception as e:
        print("❌ Couldn't find profile stats:", e)

    # Scroll slightly
    driver.execute_script("window.scrollBy(0, 300);")
    time.sleep(1)

    try:
        grid_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div._ac7v"))
        )
        first_post_div = grid_container.find_element(By.XPATH, ".//div[contains(@class, '_aagw')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", first_post_div)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", first_post_div)
        time.sleep(2)
    except Exception as e:
        print("❌ Could not click the first post:", e)
        driver.quit()
        return

    for idx in range(5):
        now = datetime.now()
        scraping_date = now.strftime("%Y-%m-%d")
        scraping_time = now.strftime("%H:%M:%S")

        likes = "N/A"
        try:
            likes_elem = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH,
                    "//section//span[contains(text(),' likes') or contains(text(),' views') or contains(@class,'_aacl')]"
                ))
            )
            likes = clean_number(likes_elem.text)
        except Exception:
            pass

        post_url = driver.current_url
        post_code = "N/A"
        if "/p/" in post_url:
            try:
                post_code = post_url.split("/p/")[1].split("/")[0]
            except Exception:
                pass

        comment_count = "N/A"
        if post_code != "N/A":
            graphql_url = (
                f"https://www.instagram.com/graphql/query/"
                f"?query_hash=97b41c52301f77ce508f55e66d17620e"
                f"&variables={{\"shortcode\":\"{post_code}\",\"first\":1}}"
            )
            try:
                response = driver.execute_script("""
                    return fetch(arguments[0])
                        .then(r => r.text())
                """, graphql_url)
                if response and not response.strip().startswith("<"):
                    data = json.loads(response)
                    comment_count = data['data']['shortcode_media']['edge_media_to_parent_comment']['count']
            except Exception:
                pass

        upload_date = upload_time = "N/A"
        try:
            time_elem = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//time"))
            )
            full_datetime = time_elem.get_attribute("datetime")
            if full_datetime:
                dt_obj = datetime.fromisoformat(full_datetime.replace("Z", "+00:00"))
                upload_date = dt_obj.date().isoformat()
                upload_time = dt_obj.time().isoformat(timespec='seconds')
        except Exception:
            pass

        image_url = "N/A"
        try:
            image_elem = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//article//img"))
            )
            image_url = image_elem.get_attribute("src")
        except Exception:
            pass

        # Send to Kafka
        data = {
            "account": target,
            "upload_date": upload_date,
            "upload_time": upload_time,
            "scraping_date": scraping_date,
            "scraping_time": scraping_time,
            "likes": likes,
            "comment_count": comment_count,
            "image_url": image_url,
            "posts": posts,
            "followers": followers,
            "following": following
        }

        producer.send("insta-business-data", value=data)
        print(f"\n✅ Post {idx+1} sent to Kafka:\n{data}")

        if idx < 4:
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_RIGHT)
            except Exception as e:
                print(f"Could not go to next post: {e}")
                break

    producer.flush()
    driver.quit()

if __name__ == "__main__":
    profiles = ["zara", "nike", "gucci", "adidas", "puma"]
    credentials = [
        {"username": "smitp_09_", "password": "23it077"},
        {"username": "p_prince_016_", "password": "23it085"},
        {"username": "__.prince.__.09__", "password": "23it085"}
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(
                scrape_profile,
                profile,
                credentials[i % len(credentials)]
            )
            for i, profile in enumerate(profiles)
        ]
        concurrent.futures.wait(futures)
    producer.close()
