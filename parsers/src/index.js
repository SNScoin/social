const { PLATFORMS } = require('social-common');
const YouTubeParser = require('./youtube');
const TikTokParser = require('./tiktok');
const InstagramParser = require('./instagram');
const FacebookParser = require('./facebook');

const parserMap = {
    [PLATFORMS.YOUTUBE]: new YouTubeParser(),
    [PLATFORMS.TIKTOK]: new TikTokParser(),
    [PLATFORMS.INSTAGRAM]: new InstagramParser(),
    [PLATFORMS.FACEBOOK]: new FacebookParser(),
};

/**
 * Get a parser instance for the given platform.
 * @param {string} platform - One of: youtube, tiktok, instagram, facebook
 * @returns {import('./base')} Parser instance
 */
function getParser(platform) {
    const parser = parserMap[platform?.toLowerCase()];
    if (!parser) {
        throw new Error(`No parser available for platform: ${platform}`);
    }
    return parser;
}

module.exports = { getParser, parserMap };
