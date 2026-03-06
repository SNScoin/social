/**
 * URL validation — single source of truth.
 * Used by the backend before saving to DB, and by parsers for sanity checks.
 */

const { PLATFORM_PATTERNS } = require('./platforms');

/**
 * Validate a social media URL and determine its platform.
 * @param {string} url - The URL to validate.
 * @returns {{ url: string, platform: string }} - The cleaned URL and detected platform.
 * @throws {Error} If the URL is empty or doesn't match any known platform.
 */
function validateSocialUrl(url) {
    if (!url || typeof url !== 'string') {
        throw new Error('URL cannot be empty');
    }

    const cleaned = url.trim();

    for (const [platform, patterns] of Object.entries(PLATFORM_PATTERNS)) {
        for (const pattern of patterns) {
            if (pattern.test(cleaned)) {
                return { url: cleaned, platform };
            }
        }
    }

    throw new Error(
        'Invalid social media URL. Please provide a valid YouTube, TikTok, Instagram, or Facebook URL.'
    );
}

module.exports = { validateSocialUrl };
