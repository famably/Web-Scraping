import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import snowflake.connector

# 1. Scrape the books data
def scrape_books(url):
    all_books_data = []
    page_num = 1

    # Scrape 5 pages (you can increase this number to scrape more pages)
    while page_num <= 5:
        print(f"Fetching data from page {page_num}...")
        books_data = fetch_books_data(url, page_num)
        
        if not books_data:  # Stop if no data is fetched (end of pages)
            break

        all_books_data.extend(books_data)
        page_num += 1

    # Create a DataFrame from the scraped data
    books_df = pd.DataFrame(all_books_data)

    return books_df

# Function to fetch the books data from a page
def fetch_books_data(url, page_num):
    url = f'{url}/catalogue/page-{page_num}.html'
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve page {page_num}. Status code: {response.status_code}")
        return None

    # Parse the HTML page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all book containers on the page
    books = soup.find_all('article', class_='product_pod')
    
    # List to store the scraped book data
    books_data = []

    # Loop through each book and extract the details
    for book in books:
        title = book.find('h3').find('a')['title']
        price = book.find('p', class_='price_color').get_text()
        rating = book.find('p', class_='star-rating')['class'][1]
        
        # Store the extracted data
        books_data.append({
            'TITLE': title,
            'PRICE': price,
            'RATING': rating
        })
    
    return books_data

# 2. Clean the data
def clean_data(df):
    df.columns = df.columns.str.strip()  # Clean column names
    df['PRICE'] = df['PRICE'].replace({'Â£': '', '€': '', '$': '', '₹': ''}, regex=True)  # Remove currency symbols
    df['PRICE'] = pd.to_numeric(df['PRICE'], errors='coerce')  # Convert PRICE to numeric
    return df

# Function to save the scraped data to snowflake
def load_to_snowflake(books_df):
    # create connection
    conn = snowflake.connector.connect(
        user='Henry',
        password='P@ssw0rd!QAZ1qaz',
        account='dwqcxnk-bd52592',
        warehouse='MY_WAREHOUSE',
        database='M_MYDATABASE',
        schema='MY_SCHEMA'
    )

    cursor = conn.cursor()

    for _, row in books_df.iterrows():
        title = row['TITLE']
        
        # Check if the book already exists by title
        cursor.execute("""
            SELECT COUNT(*) FROM books WHERE title = %s
        """, (title,))  # Use parameterized query to avoid SQL injection
        count = cursor.fetchone()[0]
        
        if count == 0:  # If the book doesn't exist, insert the data
            cursor.execute("""
                INSERT INTO books (TITLE, PRICE, RATING)
                VALUES (%s, %s, %s)
            """, tuple(row))
        else:
            print(f"Skipping duplicate book: {title}")

    # conn.commit()
    cursor.close()
    conn.close()


# Airflow DAG definition
default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 7, 10),
}

dag = DAG(
    'web_scraping_books_toscrape',
    default_args=default_args,
    description='A DAG to scrape books data from books.toscrape.com',
    schedule='@daily',  # Schedule this DAG to run daily
    catchup=False,
)

# Define PythonOperator tasks
def task_scrape_books():
    url = 'http://books.toscrape.com'
    books_df = scrape_books(url)
    return books_df

def task_clean_data(books_df):
    cleaned_df = clean_data(books_df)
    return cleaned_df

def task_load_to_snowflake(cleaned_df):
    load_to_snowflake(cleaned_df)

# Create the tasks in Airflow
scrape_books_task = PythonOperator(
    task_id='scrape_books',
    python_callable=task_scrape_books,
    dag=dag,
)

clean_data_task = PythonOperator(
    task_id='clean_data',
    python_callable=task_clean_data,
    op_args=[scrape_books_task.output],  # Pass the output of scrape_books task
    dag=dag,
)

load_to_snowflake_task = PythonOperator(
    task_id='load_to_snowflake',
    python_callable=task_load_to_snowflake,
    op_args=[clean_data_task.output],  # Pass the output of clean_data task
    dag=dag,
)

# Set task dependencies
scrape_books_task >> clean_data_task >> load_to_snowflake_task