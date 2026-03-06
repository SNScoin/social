const BaseParser = require('./base');
const axios = require('axios');

/**
 * Instagram parser using Real-Time Instagram Scraper API (RapidAPI).
 * API: https://rapidapi.com/allapiservice/api/real-time-instagram-scraper-api1
 * Requires RAPIDAPI_KEY environment variable.
 */
class InstagramParser extends BaseParser {
    constructor() {
        super('instagram');
        this.apiHost = 'real-time-instagram-scraper-api1.p.rapidapi.com';
    }

    /**
     * Extract post shortcode from Instagram URL
     * Supports: /p/CODE/, /reel/CODE/, /tv/CODE/
     */
    extractShortcode(url) {
        const match = url.match(/instagram\.com\/(?:[A-Za-z0-9_.]+\/)?(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
        return match ? match[1] : null;
    }

    async parse(url) {
        const apiKey = process.env.RAPIDAPI_KEY;
        if (!apiKey) {
            throw new Error('RAPIDAPI_KEY not configured — set it in your .env file');
        }

        const shortcode = this.extractShortcode(url);
        if (!shortcode) {
            throw new Error(`Could not extract Instagram shortcode from URL: ${url}`);
        }

        try {
            // STRATEGY 1: real-time-instagram-scraper-api1
            return await this._parseWithRealTimeApi(apiKey, shortcode);
        } catch (err) {
            // STRATEGY 2: Fallback to ScrapeNinja (legacy method) for restricted/sensitive reels
            try {
                return await this._parseWithScrapeNinja(apiKey, url, shortcode);
            } catch (fallbackErr) {
                // Throw the original error if fallback also fails
                throw err;
            }
        }
    }

    async _parseWithRealTimeApi(apiKey, shortcode) {
        const response = await axios.get(`https://${this.apiHost}/v1/media_info`, {
            headers: {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': this.apiHost,
            },
            params: { code_or_id_or_url: shortcode },
            timeout: 15000,
        });

        if (response.data?.status === 'error' || response.data?.message === 'media is not available') {
            throw new Error('media is not available via primary API');
        }

        const data = response.data?.data?.items?.[0];
        if (!data) {
            throw new Error('No data returned from primary Instagram API');
        }

        const caption = data.caption?.text || data.edge_media_to_caption?.edges?.[0]?.node?.text || '';
        const title = caption.length > 100 ? caption.substring(0, 97) + '...' : caption;

        return {
            title: title || `Instagram Post ${shortcode}`,
            views: data.video_view_count || data.play_count || data.view_count || 0,
            likes: data.edge_media_preview_like?.count || data.like_count || 0,
            comments: data.edge_media_to_comment?.count || data.comment_count || 0,
        };
    }

    async _parseWithScrapeNinja(apiKey, url, shortcode) {
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
            timeout: 25000,
        });

        const html = response.data?.body;
        if (!html) throw new Error('No HTML returned from ScrapeNinja');

        // Extract from meta description: 'content="123 likes, 45 comments..."'
        const descMatch = html.match(/content="([^"]*likes[^"]*comments[^"]*)"/);
        let likes = 0, comments = 0;

        if (descMatch) {
            const desc = descMatch[1];
            const likesStr = desc.match(/([\d,]+)\s*likes/);
            const commentsStr = desc.match(/([\d,]+)\s*comments/);
            if (likesStr) likes = parseInt(likesStr[1].replace(/,/g, ''), 10);
            if (commentsStr) comments = parseInt(commentsStr[1].replace(/,/g, ''), 10);
        }

        // Extract views from JSON embedded in HTML
        let views = 0;
        const viewMatch = html.match(/"view_count":(\d+)/g);
        if (viewMatch && viewMatch.length > 0) {
            for (const match of viewMatch) {
                const val = parseInt(match.match(/\d+/)[0], 10);
                if (val > 0) {
                    views = val;
                    break;
                }
            }
        }

        // If still 0 views but has likes, estimate it (legacy fallback feature)
        if (views === 0 && likes > 0) {
            views = Math.min(10000000, Math.max(1000, Math.floor((likes + comments) / 0.02)));
        }

        return {
            title: `Instagram Post ${shortcode}`,
            views,
            likes,
            comments,
        };
    }
}

module.exports = InstagramParser;
