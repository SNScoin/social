/**
 * BaseParser — abstract class that all platform parsers extend.
 */

class BaseParser {
    constructor(platformName) {
        this.platform = platformName;
    }

    /**
     * Parse a URL and return metrics.
     * @param {string} url - The social media URL to parse.
     * @returns {Promise<{title: string, views: number, likes: number, comments: number}>}
     */
    async parse(url) {
        throw new Error(`parse() not implemented for ${this.platform}`);
    }
}

module.exports = BaseParser;
