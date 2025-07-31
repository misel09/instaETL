# 📚 Instagram Business Profile Analysis System

A web-based and automated platform to analyze business Instagram profiles. It scrapes profile statistics and post metrics, stores them in PostgreSQL, and visualizes insights using Grafana dashboards.

---

## 🌐 Tech Stack

### Scraper & Backend:

* **Python**
* **Selenium (with undetected-chromedriver)**
* **PostgreSQL**

### Visualization:

* **Grafana**

---

## ⚙️ .env Configuration

While running locally, ensure the following environment variables are configured as needed:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=instagram_analysis
DB_USER=your_db_user
DB_PASS=your_password
```
---

## Clone the Repository
```
git clone https://github.com/misel09/instaETL.git
```
---

## Install Python Dependencies
```
pip install -r requirements.txt
```
---

## Set Instagram Credentials
```
username_input.send_keys("your_username")
password_input.send_keys("your_password")
```
---

## Run the Scraper
```
python app.py
```
---

## Connect Grafana
- Add PostgreSQL as a data source  
- Import pre-configured dashboards or create your own

---

## ✅ Features

- Scrape followers, likes, comments, and post data  
- Schedule scraping with cron  
- Store results securely in PostgreSQL  
- Analyze trends with Grafana  
- Filter top-performing posts

---

## 📊 Grafana Visualization Ideas

- 📈 Follower Growth Trend  
- ❤️ Likes vs Time  
- 💬 Avg Comments per Post  
- 🔁 Post Frequency Heatmap  
- 🔍 Post Engagement Insights

---

## 🧠 Best Practices

- Use virtualenv for dependency management  
- Store secrets in a `.env` file or environment variables  
- Avoid scraping too fast to prevent bans  
- Validate and clean data before storing

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

Thanks to open-source contributors, Selenium, Grafana community, and all developers working to make social media analytics more accessible.

