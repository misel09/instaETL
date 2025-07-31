from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json

# Optional: run in non-headless mode so you can log in manually
options = webdriver.ChromeOptions()
options.add_argument("--start-minimized")  # Simulate human usage
# options.add_argument("--headless=new")     # Run Chrome in headless mode (no window)

driver = webdriver.Chrome(options=options)

# Step 1: Open Instagram and login automatically
driver.get("https://www.instagram.com/accounts/login/")
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.NAME, "username"))
)
username_input = driver.find_element(By.NAME, "username")
password_input = driver.find_element(By.NAME, "password")
username_input.send_keys("enter_login_username") # enter your username here 
password_input.send_keys("enter_pass") # enter your pass here  
password_input.send_keys(Keys.RETURN)

# Handle "Save Your Login Info?" popup if present
try:
    time.sleep(6)
    not_now_btn = driver.find_element(By.XPATH, "//button[contains(., 'Not now') or contains(., 'Not Now')]")
    not_now_btn.click()
    time.sleep(2)
    print("Clicked 'Not now' on login info popup.")
except Exception:
    print("No 'Save Your Login Info?' popup appeared.")

# Step 2: Go to the target business profile
target = "zara" # enter target profile here 
driver.get(f"https://www.instagram.com/{target}/")
time.sleep(5)

try:
    stats = driver.find_elements(By.XPATH, "//header//li")
    posts = followers = following = "N/A"

    if len(stats) >= 3:
        # Posts
        posts = stats[0].find_element(By.TAG_NAME, "span").text.strip().replace(",", "")
        # Followers: get the exact number from the title attribute if available
        followers_span = driver.find_element(By.XPATH, "//header//li[2]//span[contains(@class, 'x5n08af')]")
        followers_exact = followers_span.get_attribute("title")
        if followers_exact:
            followers_exact = followers_exact.replace(",", "").replace(" ", "")
            print(f"{followers_exact} followers")
        else:
            print(followers_span.text.strip().replace(",", ""))
        # Following
        following = stats[2].find_element(By.TAG_NAME, "span").text.strip().replace(",", "")
        print(posts)
        print(following)
except Exception as e:
    print("❌ Couldn't find profile stats:", e)



# Instead of scrolling, directly find and click the first post using the <a> tag
# Scroll down to ensure the first post is not hidden by overlays
driver.execute_script("window.scrollBy(0, 300);")
time.sleep(1)

# Wait for the post grid container to be present
try:
    grid_container = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div._ac7v"))
    )
    # Now find the first post inside the grid
    first_post_div = grid_container.find_element(By.XPATH, ".//div[contains(@class, '_aagw')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", first_post_div)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", first_post_div)
    time.sleep(2)
except Exception as e:
    print("❌ Could not click the first post:", e)
    driver.quit()
    exit()

# Now scrape likes and post URL for the first 15 posts using the modal
for idx in range(15):
    # Scrape likes/views from modal
    likes = "N/A"
    try:
        likes_elem = WebDriverWait(driver, 0.1).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//section//span[contains(text(),' likes') or contains(text(),' views') or contains(@class,'_aacl')]"
            ))
        )
        likes = likes_elem.text.strip().replace(",", "")
    except Exception:
        pass

    post_url = driver.current_url

    # Extract post code from post_url
    post_code = "N/A"
    if "/p/" in post_url:
        try:
            post_code = post_url.split("/p/")[1].split("/")[0]
        except Exception:
            pass

    # Scrape comment count using GraphQL endpoint if post_code is available
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

    # Scrape upload time from <time> element in modal
    upload_time = "N/A"
    try:
        time_elem = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, "//time"))
        )
        upload_time = time_elem.get_attribute("datetime")
    except Exception:
        pass

    print(f"\nPost {idx+1}: {post_url}")
    print(f"Likes: {likes}")
    print(f"Comment count: {comment_count}")
    print(f"Upload time: {upload_time}")

    # Use right arrow key to go to next post if not last post
    if idx < 14:
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ARROW_RIGHT)
        except Exception as e:
            print(f"Could not go to next post with right arrow for post {idx+1}: {e}")
            break

# Close modal
try:
    close_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]")
    close_btn.click()
except:
    pass

# Done
driver.quit()
