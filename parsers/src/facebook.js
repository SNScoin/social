const BaseParser = require('./base');
const axios = require('axios');

/**
 * Facebook parser using facebook-scraper3 via RapidAPI.
 * Requires RAPIDAPI_KEY (or FACEBOOK_RAPIDAPI_KEY) environment variable.
 */
class FacebookParser extends BaseParser {
    constructor() {
        super('facebook');
        this.apiHost = 'facebook-scraper3.p.rapidapi.com';
    }

    /**
     * Extract video/reel ID from a Facebook URL
     */
    extractId(url) {
        const patterns = [
            /facebook\.com\/reel\/(\d+)/,
            /facebook\.com\/.*\/videos\/(\d+)/,
            /facebook\.com\/watch\/\?v=(\d+)/,
        ];
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) return match[1];
        }
        return null;
    }

    /**
     * Parse shortened count text like "5.3M" or "12K" into a number
     */
    parseCountText(text) {
        if (!text) return 0;
        text = String(text).trim();
        try {
            if (text.includes('M')) {
                return Math.round(parseFloat(text.replace('M', '')) * 1_000_000);
            }
            if (text.includes('K')) {
                return Math.round(parseFloat(text.replace('K', '')) * 1_000);
            }
            return parseInt(text, 10) || 0;
        } catch {
            return 0;
        }
    }

    async parse(url) {
        const apiKey = process.env.FACEBOOK_RAPIDAPI_KEY || process.env.RAPIDAPI_KEY;
        if (!apiKey) {
            throw new Error('RAPIDAPI_KEY or FACEBOOK_RAPIDAPI_KEY not configured — set it in your .env file');
        }

        const videoId = this.extractId(url);
        if (!videoId) {
            throw new Error(`Could not extract Facebook video ID from URL: ${url}`);
        }

        try {
            const response = await axios.get(`https://${this.apiHost}/post`, {
                headers: {
                    'x-rapidapi-key': apiKey,
                    'x-rapidapi-host': this.apiHost,
                },
                params: { post_id: videoId },
                timeout: 15000,
            });

            const results = response.data?.results || {};

            // Parse play_count_text (e.g., "5.3M")
            const views = this.parseCountText(results.play_count_text);

            // Extract description for title and hashtags
            const description = results.description || `Facebook Video ${videoId}`;
            const hashtags = (description.match(/#\w+/g) || []).map(t => t.slice(1));

            return {
                title: description,
                views,
                likes: results.reactions_count || 0,
                comments: results.comments_count || 0,
            };
        } catch (err) {
            if (err.response?.status === 429) {
                throw new Error('Facebook RapidAPI rate limit exceeded — try again later');
            }
            throw new Error(`Failed to parse Facebook URL: ${err.message}`);
        }
    }
}

module.exports = FacebookParser;
