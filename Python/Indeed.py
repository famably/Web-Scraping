import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# AntiCaptcha API Key
API_KEY = 'ec4be39b3fb0d0e2f17a66aa90078be0'  # Replace with your AntiCaptcha API Key

def solve_hcaptcha(site_key, page_url):
    """Solve the hCaptcha using AntiCaptcha"""
    # Step 1: Send request to AntiCaptcha to create a task
    url = "https://api.anti-captcha.com/createTask"
    data = {
        "clientKey": API_KEY,
        "task": {
            "type": "HCaptchaTaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key  # The site_key for hCaptcha
        }
    }

    response = requests.post(url, json=data)
    task_id = response.json()['taskId']

    # Step 2: Wait for the task to be solved by AntiCaptcha
    result_url = "https://api.anti-captcha.com/getTaskResult"
    while True:
        result = requests.post(result_url, json={
            "clientKey": API_KEY,
            "taskId": task_id
        }).json()

        # Check if CAPTCHA is solved
        if result['status'] == 'ready':
            return result['solution']['gRecaptchaResponse']

        # Wait 5 seconds before checking again
        time.sleep(5)

def scrape_indeed_with_hcaptcha(page_number=1):
    url = f"https://uk.indeed.com/jobs?q=software+engineer&l=remote&start={(page_number - 1) * 10}"
    
    # Set up the Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Open the Indeed page
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(5)
    
    # Find the hCaptcha iframe
    iframe = driver.find_element(By.XPATH, "//iframe[contains(@src, 'hcaptcha.com')]")
    
    # Switch to the hCaptcha iframe
    driver.switch_to.frame(iframe)
    
    # Extract the sitekey from the iframe's src attribute
    sitekey = iframe.get_attribute("src").split("sitekey=")[1].split("&")[0]
    print("hCaptcha Sitekey:", sitekey)
    
    # Solve the hCaptcha using AntiCaptcha
    recaptcha_solution = solve_hcaptcha(sitekey, url)
    
    # Inject the hCaptcha solution into the form (reCAPTCHA response field)
    driver.execute_script(f"document.getElementById('hcaptcha-response').value = '{recaptcha_solution}';")
    
    # Switch back to the main page context
    driver.switch_to.default_content()
    
    # Now interact with the form to continue
    # For example, clicking a submit button after solving the CAPTCHA:
    driver.find_element(By.XPATH, "//button[contains(@type, 'submit')]").click()

    # Wait for the page to load after solving CAPTCHA
    time.sleep(5)

    # Continue scraping the page content
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.find_all("div", class_="job_seen_beacon")
    job_listings = []

    for job in job_cards:
        job_title = job.find("h2", class_="jobTitle").get_text() if job.find("h2", class_="jobTitle") else "N/A"
        company_name = job.find("span", class_="companyName").get_text() if job.find("span", class_="companyName") else "N/A"
        location = job.find("div", class_="companyLocation").get_text() if job.find("div", class_="companyLocation") else "N/A"
        job_link = "https://uk.indeed.com" + job.find("a", class_="jcs-JobTitle")["href"] if job.find("a", class_="jcs-JobTitle") else "N/A"
        
        job_listings.append([job_title, company_name, location, job_link])

    # Close the browser
    driver.quit()

    return job_listings

# Scrape 5 pages
job_data = scrape_indeed_with_hcaptcha(5)

# Display the results (e.g., you can save it to a CSV file or display)
import pandas as pd
df = pd.DataFrame(job_data, columns=["Job Title", "Company", "Location", "Job Link"])
print(df.head())  # Show the first few entries

# Optionally, save to a CSV file
df.to_csv("indeed_job_listings.csv", index=False)
