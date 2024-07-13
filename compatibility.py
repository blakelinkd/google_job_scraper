import psycopg2

# Predefined dictionary of keywords with weights
# keywords = {
#     "Technical Support": 5, "Packer": 15, "508 compliance": 15, "Support Specialist": 5, "Support Engineer": 15, 
#     "nextjs": 50, "Next.js": 50, "typescript": 15, "Python": 20, "serverless": 5, "NoSQL": 1, 
#     "DB2": 15, "JavaScript": 15, "Accessibility": 15, "Google Maps": 30,
#         "Node.js": 6, "Nodejs": 3, 
#         "Agile": 1, "AWS": 1, "CloudFormation": 1, 
#         "Lambda": 2, "pytest": 5, "playwright": 5, "Jest": 5, "Cypress": 5,
#         "SharePoint": 1, "DynamoDB": 15, "Django": 20, "Jira": 1, "Nextjs": 20, "React.js": 20, "WCAG": 3, "SonarQube": 1,
#         "Kubernetes": 4, "Prometheus": 2, "Grafana": 3, "BDD": 5, "cucumber": 5, "gherkin": 5, "Terraform": 1, "CI/CD": 3, "Docker": 4, "integration": 3, "Flask": 5,
#         "PostgreSQL": 15, "Nginx": 1, "Elasticsearch": 3, "Logstash": 2, "Kibana": 2, "BuildKite": 10, "Linux": 15,
#         "Redux": 5, "SQLAlchemy": 5, "Prisma.js": 2, "Prismajs": 2, "FastAPI": 4, "ServiceNow": 1, "Selenium": 20, "SQL": 12,
#         "Ubuntu": 5, "TDD": 5, "Responsive": 1, "Git": 4, "Jenkins": 15,
#         "Microservice": 5, "localization": 5, "SVN": 5, "subversion": 5, 
# }

keywords = {
    "python": 5,
    "java": 5,
    "javascript": 5,
    "postgresql": 5,
    "react.js": 5,
    "next.js": 5,
    "node.js": 5,
    "elasticsearch": 5,
    "Technical Support": 5,
    "integration": 5,
    "dynamodb": 5,
    "i18n": 5,
    "accessibility": 5,
    "aws": 5,
    "linux": 5,
    "docker": 5,
    "kubernetes": 5,
    "terraform": 5,
    "jenkins": 5,
    "buildkite": 5,
    "packer": 5,
    "serverless": 5,
    "lambda": 5,
    "ec2": 5,
    "s3": 5,
    "rds": 5,
}



def get_compatibility_rating_and_skills(description, keywords):
    skill_count = {}
    description_lower = description.lower()
    for keyword in keywords:
        if keyword.lower() in description_lower:
            skill_count[keyword] = keywords[keyword]
    compatibility_rating = sum(skill_count.values())
    sorted_skills = sorted(skill_count, key=lambda x: skill_count[x], reverse=True)
    return compatibility_rating, ', '.join(sorted_skills)

# Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(
        dbname="lucee",
        user="lucee",
        password="lucee",
        host="localhost"
    )
except Exception as e:
    print(f"An error occurred: {e}")
    exit()
c = conn.cursor()

# Fetch all jobs from the database
c.execute("SELECT id, html_content FROM google_jobs")
jobs = c.fetchall()

# Calculate, update compatibilityRating, and skills for each job
for job in jobs:
    jobId, jobdescription = job
    compatibility_rating, matched_skills = get_compatibility_rating_and_skills(jobdescription, keywords)
    # Use %s as placeholder for PostgreSQL
    c.execute("UPDATE google_jobs SET compatibility = %s, skills = %s WHERE id = %s", (compatibility_rating, matched_skills, jobId))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Compatibility ratings and matched skills updated successfully.")

