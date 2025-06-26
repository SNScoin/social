# Social Media Stats Dashboard

A comprehensive dashboard application for tracking and analyzing performance metrics across multiple social media platforms, with Monday.com integration for project management.

## Features

- Multi-platform social media tracking
  - YouTube
  - TikTok
  - Instagram
  - Facebook
- Real-time stats updates and metrics tracking
  - Views
  - Likes
  - Comments
  - Engagement rates
- Monday.com integration
  - Automatic sync of social media metrics
  - Custom board and item mapping
  - Real-time updates
- Advanced analytics and reporting
  - Platform performance comparison
  - Engagement analysis
  - Growth trends
  - Custom date range filtering
- User authentication and authorization
- Company-based organization
- Clean and modern UI with Tailwind CSS
- RESTful API backend with FastAPI
- PostgreSQL database for data persistence

## Prerequisites

- Python 3.8+
- PostgreSQL
- Monday.com account (for integration)
- Social media API credentials:
  - YouTube Data API key
    - Google Cloud Console (https://console.cloud.google.com)
    - Enable YouTube Data API v3
  - TikTok API access
    - TikTok for Developers (https://developers.tiktok.com)
    - Create an app in TikTok Developer Portal
  - Instagram Graph API
    - Meta for Developers (https://developers.facebook.com)
    - Create an app in Meta Developer Portal
    - Enable Instagram Graph API
  - Facebook Graph API
    - Meta for Developers (https://developers.facebook.com)
    - Create an app in Meta Developer Portal
    - Enable Facebook Graph API
  - Monday.com API token
    - Monday.com Developer Portal (https://monday.com/developers)
    - Generate API token from your account settings

## API Configuration Guide

### YouTube Data API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the generated API key
5. Add the API key to your `.env` file:
   ```
   YOUTUBE_API_KEY=your-api-key-here
   ```

### TikTok API Setup
1. Visit [TikTok for Developers](https://developers.tiktok.com)
2. Create a developer account
3. Create a new app:
   - Click "Create App"
   - Fill in app details
   - Select required permissions
4. Get your API credentials:
   - Client Key
   - Client Secret
5. Add to your `.env` file:
   ```
   TIKTOK_API_KEY=your-client-key-here
   TIKTOK_API_SECRET=your-client-secret-here
   ```

### Instagram Graph API Setup
1. Go to [Meta for Developers](https://developers.facebook.com)
2. Create a new app or use existing one
3. Add Instagram Graph API:
   - Go to "Add Products"
   - Find "Instagram Graph API"
   - Click "Set Up"
4. Configure Instagram Basic Display:
   - Add Instagram Basic Display product
   - Configure OAuth settings
5. Get your credentials:
   - App ID
   - App Secret
6. Add to your `.env` file:
   ```
   INSTAGRAM_APP_ID=your-app-id-here
   INSTAGRAM_APP_SECRET=your-app-secret-here
   ```

### Facebook Graph API Setup
1. In your [Meta for Developers](https://developers.facebook.com) account
2. Add Facebook Graph API:
   - Go to "Add Products"
   - Find "Facebook Graph API"
   - Click "Set Up"
3. Configure permissions:
   - Add required permissions
   - Configure OAuth settings
4. Get your credentials:
   - App ID
   - App Secret
5. Add to your `.env` file:
   ```
   FACEBOOK_APP_ID=your-app-id-here
   FACEBOOK_APP_SECRET=your-app-secret-here
   ```

### Monday.com API Setup
1. Log in to your Monday.com account
2. Go to [Monday.com Developer Portal](https://monday.com/developers)
3. Generate API token:
   - Click on your profile picture
   - Go to "Admin" > "API"
   - Click "Generate Token"
4. Add to your `.env` file:
   ```
   MONDAY_API_TOKEN=your-api-token-here
   ```

### Environment Variables
Create a `.env` file in your project root with all the required variables:
```
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/social_stats

# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
YOUTUBE_API_KEY=your-youtube-api-key
TIKTOK_API_KEY=your-tiktok-api-key
TIKTOK_API_SECRET=your-tiktok-api-secret
INSTAGRAM_APP_ID=your-instagram-app-id
INSTAGRAM_APP_SECRET=your-instagram-app-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
MONDAY_API_TOKEN=your-monday-api-token
```

### Testing API Connections
After setting up your API credentials, you can test the connections:

1. YouTube API Test:
   ```bash
   python test_youtube.py
   ```

2. TikTok API Test:
   ```bash
   python test_tiktok.py
   ```

3. Instagram API Test:
   ```bash
   python test_instagram_api.py
   ```

4. Monday.com API Test:
   ```bash
   python test_monday_connection_full.py
   ```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd social-media-stats-dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL database:
   ```bash
   createdb social_stats
   ```

5. Initialize the database:
   ```bash
   python init_db.py
   ```

6. Create a root user:
   ```bash
   python create_root_user.py
   ```

7. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

8. Access the application at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /token` - Login and get access token
- `GET /verify_token` - Verify token validity

### Companies
- `GET /api/companies/` - List user's companies
- `POST /api/companies/` - Create new company
- `DELETE /api/companies/{company_id}` - Delete company

### Links
- `GET /api/links/` - List company's links
- `POST /api/links/` - Add new link
- `DELETE /api/links/{link_id}` - Delete link
- `POST /api/links/{link_id}/refresh` - Refresh link metrics

### Reports
- `GET /api/reports/platform-performance` - Get platform performance report
- `GET /api/reports/engagement-analysis` - Get engagement analysis
- `GET /api/reports/growth-trends` - Get growth trends

### Monday.com Integration
- `POST /api/monday/connect` - Connect Monday.com account
- `GET /api/monday/workspaces` - List Monday.com workspaces
- `GET /api/monday/boards` - List workspace boards
- `GET /api/monday/items` - List board items
- `GET /api/monday/verify_token` - Verify Monday.com token

## Development

### Project Structure
```
├── alembic/              # Database migrations
├── migrations/           # Migration files
├── parsers/             # Social media parsers
├── routers/             # API routers
├── static/              # Static files
├── templates/           # HTML templates
├── utils/               # Utility functions
├── main.py             # Main application file
├── models.py           # Database models
├── database.py         # Database configuration
└── requirements.txt    # Python dependencies
```

### Key Technologies
- Frontend: HTML, Tailwind CSS, JavaScript
- Backend: FastAPI, SQLAlchemy, PostgreSQL
- Authentication: JWT tokens
- API Integration: Monday.com API, Social Media APIs
- Testing: pytest

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For support, please open an issue in the repository or contact the maintainers.