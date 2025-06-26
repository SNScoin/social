import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.models import Link, LinkMetrics

load_dotenv()

# Database connection string
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

company_id = 1

links = session.query(Link).filter(Link.company_id == company_id).all()

print(f"Links and statistics for company {company_id}:")
print("-" * 120)
print(f"{'ID':<5} {'Platform':<10} {'URL':<45} {'Views':<8} {'Likes':<8} {'Comments':<10} {'Updated At'}")
print("-" * 120)
for link in links:
    metrics = session.query(LinkMetrics).filter(LinkMetrics.link_id == link.id).first()
    print(f"{link.id:<5} {link.platform:<10} {link.url[:40]:<45} "
          f"{(metrics.views if metrics else '-'): <8} "
          f"{(metrics.likes if metrics else '-'): <8} "
          f"{(metrics.comments if metrics else '-'): <10} "
          f"{(metrics.updated_at if metrics else '-')}")
print("-" * 120)
session.close() 