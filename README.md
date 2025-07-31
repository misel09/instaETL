📊 Instagram Business Profile Analysis
This project scrapes public business profiles from Instagram using Selenium, stores structured post analytics (likes, comments, time, etc.) in PostgreSQL, and visualizes the insights with Grafana.

🚀 Features
✅ Auto-login and profile navigation

📦 Scrapes:

Total posts, followers, following

First 15 posts: likes/views, comment count, upload time, and URL

💾 Data saved to PostgreSQL

📊 Dashboard analysis using Grafana

🖥️ Technologies Used
Tool	Purpose
Selenium	Browser automation & scraping
PostgreSQL	Data storage
Grafana	Interactive dashboard & analytics
Python	Core scripting language

📌 Project Structure
bash
Copy
Edit
instagram-profile-analyzer/
│
├── scraper.py                 # Selenium-based scraper script
├── db_store.py               # Script to store data into PostgreSQL
├── dashboard.png             # Grafana dashboard screenshot
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
⚙️ Setup Instructions
Clone Repository

bash
Copy
Edit
git clone https://github.com/yourusername/instagram-profile-analyzer.git
cd instagram-profile-analyzer
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Update Credentials

In scraper.py:

python
Copy
Edit
username_input.send_keys("your_instagram_username")
password_input.send_keys("your_password")
Run Scraper

bash
Copy
Edit
python scraper.py
Store to PostgreSQL

Create your DB schema, then use db_store.py to insert data.

Grafana Dashboard

Connect Grafana to PostgreSQL and build your analytics board using SQL queries or import existing .json config (if provided).

📊 Example Grafana Panel Ideas
Followers Trend

Average Likes per Post

Comment-to-Like Ratio

Top Performing Posts

Post Frequency Timeline

📃 License
MIT License – Feel free to use and modify.
