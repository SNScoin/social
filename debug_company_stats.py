import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.models import Link, LinkMetrics, Company

load_dotenv()

# Database connection string
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

company_id = 2

print(f"=== DEBUGGING COMPANY {company_id} STATS ===")

# 1. Check if company exists
company = session.query(Company).filter(Company.id == company_id).first()
if not company:
    print(f"Company {company_id} not found!")
    exit(1)
print(f"Company found: {company.name} (owner_id: {company.owner_id})")

# 2. Get all links for the company
links = session.query(Link).filter(Link.company_id == company_id).all()
print(f"\nFound {len(links)} links:")
for link in links:
    print(f"  Link ID: {link.id}, Platform: '{link.platform}', URL: {link.url[:50]}...")

# 3. Get all metrics for these links
link_ids = [link.id for link in links]
print(f"\nLink IDs: {link_ids}")

metrics_list = session.query(LinkMetrics).filter(LinkMetrics.link_id.in_(link_ids)).all() if link_ids else []
print(f"\nFound {len(metrics_list)} metrics records:")

total_views = 0
total_likes = 0
total_comments = 0

# Create a mapping of link_id to platform
link_id_to_platform = {link.id: link.platform for link in links}

for metric in metrics_list:
    views = metric.views or 0
    likes = metric.likes or 0
    comments = metric.comments or 0
    
    platform = link_id_to_platform.get(metric.link_id, 'unknown')
    
    total_views += views
    total_likes += likes
    total_comments += comments
    
    print(f"  Link ID: {metric.link_id}, Platform: '{platform}', Views: {views}, Likes: {likes}, Comments: {comments}")

print(f"\n=== TOTALS ===")
print(f"Total Views: {total_views}")
print(f"Total Likes: {total_likes}")
print(f"Total Comments: {total_comments}")

# 4. Check platform distribution
platform_counts = {}
for link in links:
    platform = link.platform
    platform_counts[platform] = platform_counts.get(platform, 0) + 1

print(f"\n=== PLATFORM DISTRIBUTION ===")
for platform, count in platform_counts.items():
    print(f"'{platform}': {count} links")

# 5. Check what platforms the API expects
api_expected_platforms = ["YouTube", "TikTok", "Instagram", "Facebook"]
print(f"\n=== API EXPECTED PLATFORMS ===")
for platform in api_expected_platforms:
    print(f"'{platform}'")

# 6. Check if there's a case mismatch
print(f"\n=== PLATFORM MATCHING ISSUE ===")
for link in links:
    if link.platform not in api_expected_platforms:
        print(f"Link {link.id} has platform '{link.platform}' which is NOT in API expected platforms")

session.close() 