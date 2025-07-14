# Web Scraping with Python
## ✨ Goal
Automate web scraping from a website using Python and Apache Airflow.

## 💡 Explanation
1. Choose an example URL for web scraping (e.g., http://books.toscrape.com).
2. Write Python code to scrape data from the website and load it into Snowflake.
3. Use Apache Airflow to automate the scraping process by scheduling and managing the workflow.


## 🔗 Step-by-Step Guide

### 1. Snowflake Setup
✅ Create an account at https://www.snowflake.com/

✅ In the Snowflake dashboard:
- Navigate to Admin > Warehouses → click “+ Warehouse” to create a compute warehouse.
- Navigate to Data > Databases → click “+ Database” to create a logical database.
- Select the newly created database → click “+ Schema” to create a schema.
- Create a new table under the created schema to store your web scraping data.

### 2. Astronomer Setup
🔍 Note: Astronomer is a managed service that provides Apache Airflow as a cloud-native solution.

#### 1) Set Up Astronomer Account
1. Sign up for an account on https://www.astronomer.io/

#### 2) Set Up a Local Development Environment
1. Install Astronomer CLI on your local machine.
- Download astro_1.18.2_windows_amd64.exe
- Rename the file to astro.exe
- Add the filepath for the directory containing the new astro.exe as a PATH environment variable.
2. Initialize Astronomer Project.
- Create initial project:
   ```shell
   astro dev init
   ```
3. Write Python script under **dags** directory.

   For example, write “scrape_books.py” file to
- Scrape the books data
- Clean the data
- Save the scraped data to snowflake
- Define Airflow DAG
- Create the tasks in Airflow
- Set task dependencies

4. Write Python dependencies in **requirements.txt**
   
   Ensure you have all the necessary Python dependencies (such as requests, beautifulsoup4, pandas, and snowflake-connector) listed in your requirements.txt.

5. Build and Run Airflow Locally
   ```shell
   astro dev start
   ```

   This will build and start the Airflow containers locally using Docker. You can access the Airflow UI locally by going to http://localhost:8080.

#### 3) Push the Project to Astronomer
1. Log In to Astronomer CLI
   ```shell
   astro login
   ```

2. Deploy Your Project

   Use the astro deploy command to push your project to the Astronomer platform.


   ```shell
   astro deploy
   ```