const BaseParser = require('./base');
const { google } = require('googleapis');

class YouTubeParser extends BaseParser {
    constructor() {
        super('youtube');
    }

    /**
     * Extract the video ID from a YouTube URL.
     * Supports watch?v=, /shorts/, youtu.be/, /embed/, /v/, /live/
     */
    extractVideoId(url) {
        const patterns = [
            /(?:v=|\/shorts\/|youtu\.be\/|\/embed\/|\/v\/|\/live\/)([A-Za-z0-9_-]{11})/,
        ];
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) return match[1];
        }
        return null;
    }

    /**
     * Parse a YouTube URL and return title + metrics.
     * Uses YouTube Data API v3.
     */
    async parse(url) {
        const videoId = this.extractVideoId(url);
        if (!videoId) {
            throw new Error('Could not extract YouTube video ID from URL');
        }

        const apiKey = process.env.YOUTUBE_API_KEY;
        if (!apiKey) {
            throw new Error('YOUTUBE_API_KEY not configured — set it in your .env file');
        }

        try {
            const youtube = google.youtube({ version: 'v3', auth: apiKey });
            const response = await youtube.videos.list({
                part: 'snippet,statistics',
                id: videoId,
            });

            const video = response.data.items?.[0];
            if (!video) {
                throw new Error(`YouTube video not found (ID: ${videoId})`);
            }

            return {
                title: video.snippet?.title || '',
                thumbnail: video.snippet?.thumbnails?.medium?.url || '',
                channel: video.snippet?.channelTitle || '',
                publishedAt: video.snippet?.publishedAt || null,
                views: parseInt(video.statistics?.viewCount || '0', 10),
                likes: parseInt(video.statistics?.likeCount || '0', 10),
                comments: parseInt(video.statistics?.commentCount || '0', 10),
            };
        } catch (err) {
            // Re-throw structured errors
            if (err.response?.status === 403) {
                throw new Error('YouTube API quota exceeded — try again later');
            }
            if (err.response?.status === 400) {
                throw new Error(`YouTube API key invalid or request malformed`);
            }
            throw err;
        }
    }
}

module.exports = YouTubeParser;
