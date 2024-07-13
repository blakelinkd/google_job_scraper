import json
import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
import psycopg2
from urllib.parse import parse_qs, quote, urlparse
DB_HOST = "localhost"
DB_NAME = "google_jobs"
DB_USER = "postgres_user"
DB_PASSWORD = "postgres_password"
DB_PORT = 5432

PROXY = {}

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)
cur = conn.cursor()

def insert_job_data(search_result):
    sql = """
    INSERT INTO google_jobs (url, title, company_name, location, html_content)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    params = (
        search_result["url"],
        search_result["title"],
        search_result["company_name"],
        search_result["location"],
        search_result["page_content"]
    )
    try:
        cur.execute(sql, params)
        conn.commit()
        last_id = cur.fetchone()[0]  # Fetch the returned id

        print(f'last insert row: {last_id}')
    except Exception as e:
        print(f"Failed to insert data for URL {search_result['url']}: {e}")
        conn.rollback()  # Rollback the transaction on error

def job_exists(url):
    sql = "SELECT id FROM google_jobs WHERE url = %s"
    try:
        cur.execute(sql, (url,))
        conn.commit()
    except Exception as e:
        print(f"Failed to check if job exists for URL {url}: {e}")
        conn.rollback()  # Rollback the transaction on error
        return False

def generate_google_search_url(query):
    base_url = "https://www.google.com/search"
    query_param = quote(query)
    additional_params = "&oq={}&sourceid=chrome&ie=UTF-8".format(query_param)
    url = "{}?q={}{}".format(base_url, query_param, additional_params)
    return url

def search_google(query, max_pages=float("inf")):
    search_query = generate_google_search_url(query)
    print(f'search query: {search_query}')
    search_url = search_query
    results = []
    current_url = search_url
    page = 1
    print('searching google...')
    while current_url and page <= max_pages:

        headers = {
            # Use outdated user agent to disable infinite page reload
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19042"
        }
        time.sleep(random.uniform(10, 20))
        response = requests.get(current_url, headers=headers, proxies=PROXY)
        soup = BeautifulSoup(response.content, "html.parser")
        pretty_output = soup.prettify()
        with open("fart_debug.log", "w") as file:
            file.write(pretty_output)
        if "Our systems have detected unusual traffic from your computer network" in pretty_output:
            print('bot detected. Exiting.')
            return results
        elements = soup.find_all("a", attrs={'data-ved': True })
        for element in elements:
            link = element["href"]
            if not link:
                continue
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)
            extracted_url = query_params.get('url', [None])[0]
            results.append(extracted_url)

        next_page_button = soup.select_one('[aria-label="Next page"]')
        if next_page_button:
            next_page_url = next_page_button["href"]
            current_url = f"https://www.google.com{next_page_url}"
            page += 1
            print('.', end='', flush=True)
        else:
            current_url = None
    print('done.\n')
    return results



def download_and_search(urls):
    result_set = []

    for url in urls:
        if job_exists(url):
            print('-', end='', flush=True)
            continue

        try:
            response = requests.get(url, proxies=PROXY)
            time.sleep(2)
            if response.status_code == 200:
                pass
            else:
                continue
            time.sleep(random.uniform(0, 3))

            page_content = response.content
            soup = BeautifulSoup(page_content, "html.parser")
            title = ""
            company_name = ""
            location = ""
            print(f'trying url: {url}')
            if 'jobs.ashbyhq.com' in url:
                pass
            elif 'remoterocketship.com' in url:
                script_tag = soup.find('script', type='application/ld+json')
                if script_tag:
                    json_content = script_tag.string
                    data = json.loads(json_content)
                    title = data['title']
                    company_name = data['hiringOrganization']['name']
                    location = data['applicantLocationRequirements']['name']
            
            elif 'myworkdayjobs.com' in url:
                script_tag = soup.find('script', type='application/ld+json')
                if script_tag:
                    json_content = script_tag.string
                    data = json.loads(json_content)
                    title = data['identifier']['name']
                    company_name = data['hiringOrganization']['name']
                    location = data['jobLocation']['address']['addressLocality']
                    description = data['description']

            elif 'ocs.oraclecloud.com' in url:
                title = soup.find('meta', property='og:title').get('content')
                company_name = soup.find('meta', property='og:site_name').get('content')
                location = "Unkown"

            elif 'dayforcehcm.com' in url:
                    title = soup.select_one('div.posting-title-container').get_text(strip=True)
                    location = soup.select_one('span.job-location').get_text(strip=True)
                    script_tag = soup.find('script', string=re.compile(r'let gaParms = {'))
                    if script_tag:
                        script_content = script_tag.string
                        # Use regular expression to find the clientName value
                        match = re.search(r"'clientName':\s*'([^']+)'", script_content)
                        if match:
                            company_name = match.group(1)

            elif 'softgarden.io' in url:
                script_tag = soup.find('script', type='application/ld+json')
                if script_tag:
                    json_content = script_tag.string
                    data = json.loads(json_content)
                    title = data['identifier']['name']
                    company_name = data['hiringOrganization']['name']
                    location = data['jobLocation']['address']['addressLocality']

            elif 'applytojob.com' in url:
                title = soup.select_one('body > main > div.job-header > div > h1')
                if title:
                    title = title.text.strip()
                script_tag = soup.find('script', type='application/ld+json')
                json_content = json.loads(script_tag.string)
                company_name = json_content.get('name')
                location = soup.select_one('div[title="Location"]').get_text(strip=True)
                
            elif 'indeed.com' in url:
                title = soup.select_one('h1.jobsearch-JobInfoHeader-title')
                if title:
                    title = title.text.strip()
                company_name = soup.select_one('h2.jobsearch-CompanyReview--heading')
                if company_name:
                    company_name = company_name.text.strip()
                location = soup.select_one('div[data-testid="inlineHeader-companyLocation"]')
                if location:
                    location = location.text.strip()

            elif 'boards.greenhouse.io' in url:
                title = soup.select_one('h1.app-title')
                if title:
                    title = title.text.strip()
                company_name = soup.select_one('span.company-name')
                if company_name:
                    company_name = company_name.text.strip()
                location = soup.select_one('div.location')
                if location:
                    location = location.text.strip()

            elif 'www.wayup.com' in url:
                title = soup.select_one('div.posting-headline h2')
                if title:
                    title = title.text.strip()
                else:
                    title_element = soup.select_one('#root > div > div.AppChildrenContainer-sc-1685a4m-0.WNKsq > div > div.FullBleedImage__FullBleedImageWrapper-sc-16p7acd-0.cUIHFx > div.FullBleedImage__FullBleedChildWrapper-sc-16p7acd-2.GWNav > div > h1')
                    if title_element:
                        title = title_element.text.strip()

                company_name_element = soup.select_one('#root > div > div.AppChildrenContainer-sc-1685a4m-0.WNKsq > div > div.sticky-outer-wrapper > div > div > div > div > div > div.sc-ksluoS.jIcQEJ > div > div > h1')
                if company_name_element:
                    company_name = company_name_element.text.strip()

                location_element = soup.select_one('#root > div > div.AppChildrenContainer-sc-1685a4m-0.WNKsq > div > div.sticky-outer-wrapper > div > div > div > div > div > div.sc-ksluoS.WHDSa > div > div:nth-child(1) > div')
                if location_element:
                    location = location_element.text.strip()

            elif 'jobs.lever.co' in url:
                title = soup.select_one('div.posting-headline h2')
                if title:
                    title = title.text.strip()
                else:
                    title_element = soup.select_one('body > div.content-wrapper.application-page > div > div.section-wrapper.accent-section.small-accent.page-full-width > div > h2')
                    if title_element:
                        title = title_element.text.strip()

                company_name_element = soup.select_one('body > div.main-footer.page-full-width > div > p > a')
                if company_name_element:
                    company_name = company_name_element.text.strip()

                location = soup.select_one('div.location')
                if location:
                    location = location.text.strip()


            company_name = company_name.replace("at ", "")
            company_name = company_name.replace(" Home Page", "")

            if company_name or title:
                print(f'company name: {company_name} title: {title}')
                company_name = company_name.replace("at ", "")
                if description:
                    text = description
                else:
                    text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                result = {
                    "url": url,
                    "page_content": text,
                    "title": title,
                    "company_name": company_name,
                    "location": location
                }
                print(result)
                result_set.append(result)
            else:
                print('no company info.')

        except Exception as e:
            pass
    return result_set


CONF_FILE = 'fart.conf'

def load_config():
    if os.path.exists(CONF_FILE):
        with open(CONF_FILE, 'r') as f:
            return json.load(f)
    return {"last_used_sites": []}

def save_config(config):
    with open(CONF_FILE, 'w') as f:
        json.dump(config, f)

def get_next_sites(all_sites, last_used_sites, num_sites):
    available_sites = [site for site in all_sites if site not in last_used_sites]
    if len(available_sites) < num_sites:
        available_sites = all_sites  # Reset if we've used all sites
    selected_sites = random.sample(available_sites, num_sites)
    return selected_sites


def main():

    query = "site:myworkdayjobs.com | site:ocs.oraclecloud.com | site:dayforcehcm.com | site:softgarden.io | site:greenhouse.io | site:lever.co | site:www.wayup.com | site:applytojob.com linux | jenkins | docker | python | javascript remote after:2024-7-1"
    all_results = search_google(query, 2000)
    # save_config(config)
    matches = download_and_search(all_results)
    return matches

if __name__ == "__main__":
    matches = main()
    for match in matches:
        insert_job_data(match)
    cur.close()
    conn.close()
    os.system('python compatibility.py')
