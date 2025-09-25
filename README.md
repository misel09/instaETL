

---

# 📚 Instagram Business Profile Analysis System

A web-based and automated platform to analyze business Instagram profiles.  
It scrapes profile statistics and post metrics, streams data via Kafka, stores it in **InfluxDB + PostgreSQL**, and visualizes insights using Grafana dashboards.

---

## 🌐 Tech Stack

### Scraper & Backend:
- **Python**
- **Selenium (with undetected-chromedriver)**
- **Kafka + Zookeeper**
- **InfluxDB**
- **PostgreSQL**

### Visualization:
- **Grafana**

---

## ⚙️ .env Configuration

While running locally, ensure the following environment variables are configured:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=instagram_analysis
DB_USER=your_db_user
DB_PASS=your_password
````

---

## Clone the Repository

```bash
git clone https://github.com/misel09/instaETL.git
cd instaETL
```

---

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Set Instagram Credentials

Inside the scraper code (e.g., `app.py`), update with your login details:

```python
username_input.send_keys("your_username")
password_input.send_keys("your_password")
```

---

## Run the System

### Option 1: Manual Start

1. Start **Zookeeper**

   ```bash
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```

2. Start **Kafka**

   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```

3. Start **InfluxDB**

   ```bash
   influxd
   ```

4. Run the scraper

   ```bash
   python app.py
   ```

---

### Option 2: Run with Docker Compose (Recommended 🚀)

You can use Docker Compose to run Zookeeper, Kafka, PostgreSQL, and InfluxDB together.

#### docker-compose.yml

```yaml
version: "3.8"

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: kafka
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT

  postgres:
    image: postgres:15
    container_name: postgres
    restart: always
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: instagram_analysis
      POSTGRES_USER: your_db_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    restart: always
    ports:
      - "8086:8086"
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: password
      DOCKER_INFLUXDB_INIT_ORG: my-org
      DOCKER_INFLUXDB_INIT_BUCKET: insta-metrics
    volumes:
      - influxdb_data:/var/lib/influxdb2

volumes:
  postgres_data:
  influxdb_data:
```

#### Run

```bash
docker-compose up -d
```

Then run the scraper:

```bash
python app.py
```

---

## Connect Grafana

* Add **PostgreSQL** and **InfluxDB** as data sources
* Import pre-configured dashboards or create your own

---

## ✅ Features

* Scrape followers, likes, comments, and post data
* Stream data to **Kafka + InfluxDB**
* Schedule scraping with cron
* Store results securely in PostgreSQL
* Analyze trends with Grafana
* Filter top-performing posts

---

## 📊 Grafana Visualization Ideas

* 📈 Follower Growth Trend
* ❤️ Likes vs Time
* 💬 Avg Comments per Post
* 🔁 Post Frequency Heatmap
* 🔍 Post Engagement Insights

---

## 🧠 Best Practices

* Use virtualenv for dependency management
* Store secrets in a `.env` file or environment variables
* Avoid scraping too fast to prevent bans
* Validate and clean data before storing

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

Thanks to open-source contributors, Selenium, Kafka, InfluxDB, Grafana community, and all developers working to make social media analytics more accessible.

```

---

👉 Do you also want me to add a **sample Grafana dashboard JSON** in the repo so users can import it directly, instead of building from scratch?
```
