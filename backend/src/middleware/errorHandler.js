const logger = require('../logger');

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, _next) {
    logger.error({ err, path: req.path, method: req.method }, 'Unhandled error');

    const statusCode = err.statusCode || 500;
    const message = err.expose ? err.message : 'Internal server error';

    res.status(statusCode).json({
        error: 'INTERNAL_ERROR',
        message,
    });
}

module.exports = errorHandler;
