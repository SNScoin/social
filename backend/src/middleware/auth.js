const jwt = require('jsonwebtoken');
const config = require('../config/env');
const { ERROR_CODES } = require('social-common');

function auth(req, res, next) {
    const header = req.headers.authorization;

    if (!header || !header.startsWith('Bearer ')) {
        return res.status(401).json({ error: ERROR_CODES.UNAUTHORIZED, message: 'Missing or invalid token' });
    }

    const token = header.split(' ')[1];

    try {
        const decoded = jwt.verify(token, config.jwtSecret);
        req.user = { id: decoded.sub, email: decoded.email };
        next();
    } catch (err) {
        return res.status(401).json({ error: ERROR_CODES.TOKEN_EXPIRED, message: 'Token expired or invalid' });
    }
}

module.exports = auth;
