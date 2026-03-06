require('dotenv').config();

const config = {
    port: process.env.PORT || 3001,
    databaseUrl: process.env.DATABASE_URL,
    redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
    jwtSecret: process.env.JWT_SECRET || 'change-me',
    accessTokenExpireMinutes: parseInt(process.env.ACCESS_TOKEN_EXPIRE_MINUTES || '30', 10),
    youtubeApiKey: process.env.YOUTUBE_API_KEY,
    rapidApiKey: process.env.RAPIDAPI_KEY,
    mondayApiToken: process.env.MONDAY_API_TOKEN,
    apifyApiToken: process.env.APIFY_API_TOKEN,
    nodeEnv: process.env.NODE_ENV || 'development',
};

module.exports = config;
