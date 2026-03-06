const PLATFORMS = {
  YOUTUBE: 'youtube',
  TIKTOK: 'tiktok',
  INSTAGRAM: 'instagram',
  FACEBOOK: 'facebook',
  LINKEDIN: 'linkedin',
  X: 'x',
};

const PLATFORM_PATTERNS = {
  [PLATFORMS.YOUTUBE]: [
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=[\w-]+/,
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/[\w-]+/,
    /(?:https?:\/\/)?youtu\.be\/[\w-]+/,
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/@[\w.-]+/,       // profile/channel
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/channel\/[\w-]+/,
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/c\/[\w.-]+/,
  ],
  [PLATFORMS.TIKTOK]: [
    /(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@[\w.-]+\/video\/\d+/,
    /(?:https?:\/\/)?(?:www\.)?tiktok\.com\/t\/[\w-]+/,
    /(?:https?:\/\/)?vm\.tiktok\.com\/[\w-]+/,
    /(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@[\w.-]+/,        // profile
  ],
  [PLATFORMS.INSTAGRAM]: [
    /(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:p|reel)\/[\w-]+(?:\/.*)?(?:\?.*)?$/,
    /(?:https?:\/\/)?(?:www\.)?instagram\.com\/reels\/[\w-]+(?:\/.*)?(?:\?.*)?$/,
    /(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:stories|tv)\/[\w-]+(?:\/.*)?(?:\?.*)?$/,
    /(?:https?:\/\/)?(?:www\.)?instagram\.com\/[\w.-]+/,      // profile
  ],
  [PLATFORMS.FACEBOOK]: [
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/reel\/\d+/,
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/[\w.-]+\/videos\/\d+/,
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/watch\/\?v=\d+/,
    /(?:https?:\/\/)?(?:www\.)?fb\.watch\/[\w-]+/,
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/profile\.php\?id=\d+/,  // profile by ID
    /(?:https?:\/\/)?(?:www\.)?facebook\.com\/[\w.-]+/,               // profile by name
  ],
  [PLATFORMS.LINKEDIN]: [
    /(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[\w.-]+/,
    /(?:https?:\/\/)?(?:www\.)?linkedin\.com\/company\/[\w.-]+/,
    /(?:https?:\/\/)?(?:www\.)?linkedin\.com\/feed/,
  ],
  [PLATFORMS.X]: [
    /(?:https?:\/\/)?(?:www\.)?(?:twitter\.com|x\.com)\/[\w.-]+/,
  ],
};

const PLATFORM_LIST = Object.values(PLATFORMS);

module.exports = { PLATFORMS, PLATFORM_PATTERNS, PLATFORM_LIST };
