import os
from dotenv import load_dotenv
<<<<<<< HEAD
from sqlalchemy import create_engine, func
=======
from sqlalchemy import create_engine
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
from sqlalchemy.orm import sessionmaker
from backend.app.models.models import Link, LinkMetrics

load_dotenv()

# Database connection string
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

<<<<<<< HEAD
company_id = 2
=======
company_id = 1
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460

links = session.query(Link).filter(Link.company_id == company_id).all()

print(f"Links and statistics for company {company_id}:")
print("-" * 120)
print(f"{'ID':<5} {'Platform':<10} {'URL':<45} {'Views':<8} {'Likes':<8} {'Comments':<10} {'Updated At'}")
print("-" * 120)
<<<<<<< HEAD

total_views = 0
total_likes = 0
total_comments = 0

for link in links:
    metrics = session.query(LinkMetrics).filter(LinkMetrics.link_id == link.id).first()
    views = metrics.views if metrics and metrics.views else 0
    likes = metrics.likes if metrics and metrics.likes else 0
    comments = metrics.comments if metrics and metrics.comments else 0
    
    total_views += views
    total_likes += likes
    total_comments += comments
    
    print(f"{link.id:<5} {link.platform:<10} {link.url[:40]:<45} "
          f"{views:<8} "
          f"{likes:<8} "
          f"{comments:<10} "
          f"{(metrics.updated_at if metrics else '-')}")

print("-" * 120)
print(f"TOTALS: Views: {total_views}, Likes: {total_likes}, Comments: {total_comments}")
=======
for link in links:
    metrics = session.query(LinkMetrics).filter(LinkMetrics.link_id == link.id).first()
    print(f"{link.id:<5} {link.platform:<10} {link.url[:40]:<45} "
          f"{(metrics.views if metrics else '-'): <8} "
          f"{(metrics.likes if metrics else '-'): <8} "
          f"{(metrics.comments if metrics else '-'): <10} "
          f"{(metrics.updated_at if metrics else '-')}")
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
print("-" * 120)
session.close() 