# Google Job Scraper

This script scrapes job listings from various job portals indexed by Google. It searches for job listings based on specific queries and stores the job details in a PostgreSQL database.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Database Setup](#database-setup)
- [Notes](#notes)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/google-job-scraper.git
    cd google-job-scraper
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure the PostgreSQL connection parameters in the script:
    ```python
    DB_HOST = "localhost"
    DB_NAME = "google_jobs"
    DB_USER = "postgres_user"
    DB_PASSWORD = "postgres_password"
    DB_PORT = 5432
    ```

## Usage

1. Run the script:
    ```bash
    python scraper.py
    ```

2. The script will perform the following actions:
    - Generate a Google search URL based on the specified query.
    - Scrape job listing URLs from Google search results.
    - Extract job details from the job listing pages.
    - Insert the job details into the PostgreSQL database.

## Configuration

- The script uses a configuration file `fart.conf` to keep track of the last used sites.
- You can modify the search query in the `main()` function to change the job search criteria.

## Dependencies

- Python 3.x
- Required Python packages (listed in `requirements.txt`):
    - `requests`
    - `beautifulsoup4`
    - `psycopg2`
    - `urllib3`

## Database Setup

1. Ensure PostgreSQL is installed and running.

2. Create a PostgreSQL database and table:
    ```sql
    CREATE DATABASE google_jobs;
    
    \c google_jobs

    CREATE TABLE google_jobs (
        id SERIAL PRIMARY KEY,
        url TEXT UNIQUE NOT NULL,
        title TEXT,
        company_name TEXT,
        location TEXT,
        html_content TEXT
    );
    ```

## Notes

- The script uses a random sleep interval to avoid being blocked by Google for sending too many requests in a short period.
- It handles different job listing formats from various job portals.
- Proxy support is available but not configured by default (`PROXY` dictionary).
- Ensure the PostgreSQL credentials and database details are correctly configured before running the script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
