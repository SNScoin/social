const { PLATFORMS, PLATFORM_PATTERNS, PLATFORM_LIST } = require('./platforms');
const { validateSocialUrl } = require('./validators');
const { ERROR_CODES } = require('./errors');

module.exports = {
    PLATFORMS,
    PLATFORM_PATTERNS,
    PLATFORM_LIST,
    validateSocialUrl,
    ERROR_CODES,
};
