const BaseParser = require('./base');

/**
 * TikTok parser using Apify Actor.
 * Requires APIFY_TOKEN environment variable.
 */
class TikTokParser extends BaseParser {
    constructor() {
        super('tiktok');
        this.actorId = 'S5h7zRLfKFEr8pdj7';
    }

    /**
     * Extract video ID from TikTok URL
     */
    extractVideoId(url) {
        const patterns = [
            /video\/(\d+)/,
            /\/v\/(\d+)/,
            /@[\w.-]+\/video\/(\d+)/,
            /vm\.tiktok\.com\/(\w+)/,
            /tiktok\.com\/t\/(\w+)/,
        ];
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) return match[1];
        }
        return null;
    }

    /**
     * Clean title text — remove URLs, excessive whitespace, special chars
     */
    cleanTitle(text, maxLength = 100) {
        if (!text) return 'Untitled TikTok Video';
        text = text.replace(/http\S+/g, '');
        text = text.replace(/\s+/g, ' ');
        // Remove emojis (basic range)
        text = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FEFF}\u{1F900}-\u{1F9FF}\u{200D}\u{20E3}\u{FE0F}]/gu, '');
        text = text.replace(/[^\w\s#@.,!?-]/g, '');
        text = text.trim();
        if (text.length > maxLength) {
            text = text.substring(0, maxLength - 3) + '...';
        }
        return text || 'Untitled TikTok Video';
    }

    /**
     * Get a value from an object using multiple possible keys
     */
    getFrom(data, ...keys) {
        for (const key of keys) {
            if (data[key] !== undefined) return data[key];
        }
        return null;
    }

    /**
     * Parse a TikTok URL via ScrapeNinja (RapidAPI workaround, as Apify requires a paid subscription)
     */
    async parse(url) {
        const apiKey = process.env.RAPIDAPI_KEY;
        if (!apiKey) {
            throw new Error('RAPIDAPI_KEY not configured — set it in your .env file');
        }

        const videoId = this.extractVideoId(url);
        if (!videoId) {
            throw new Error(`Could not extract TikTok video ID from URL: ${url}`);
        }

        const axios = require('axios');
        try {
            const response = await axios.post('https://scrapeninja.p.rapidapi.com/scrape', {
                url: url,
                render: true,
                wait: 3000
            }, {
                headers: {
                    'x-rapidapi-key': apiKey,
                    'x-rapidapi-host': 'scrapeninja.p.rapidapi.com',
                    'Content-Type': 'application/json'
                },
                timeout: 30000,
            });

            const html = response.data?.body;
            if (!html) throw new Error('No HTML returned from ScrapeNinja');

            // Find JSON data in the rendered HTML (Next.js state or TikTok internal state)
            const titleMatch = html.match(/<title>(.*?)<\/title>/);
            const title = titleMatch ? this.cleanTitle(titleMatch[1].replace(' | TikTok', '')) : `TikTok Video ${videoId}`;

            const playCountStr = html.match(/"playCount":(\d+)/);
            const diggCountStr = html.match(/"diggCount":(\d+)/);
            const commentCountStr = html.match(/"commentCount":(\d+)/);

            const views = playCountStr ? parseInt(playCountStr[1], 10) : 0;
            const likes = diggCountStr ? parseInt(diggCountStr[1], 10) : 0;
            const comments = commentCountStr ? parseInt(commentCountStr[1], 10) : 0;

            if (views === 0 && likes === 0) {
                // Heuristic: TikTok completely blocked the render page
                throw new Error('media is not available or blocked by TikTok captcha');
            }

            return {
                title,
                views,
                likes,
                comments,
            };
        } catch (err) {
            if (err.response?.status === 429) {
                throw new Error('RapidAPI rate limit exceeded — try again later');
            }
            throw new Error(err.message || 'Failed to parse TikTok URL');
        }
    }
}

module.exports = TikTokParser;
