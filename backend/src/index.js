const express = require('express');
const cors = require('cors');
const http = require('http');
const { Server: SocketServer } = require('socket.io');
const config = require('./config/env');
const logger = require('./logger');
const { globalLimiter } = require('./middleware/rateLimiter');
const errorHandler = require('./middleware/errorHandler');
const { refreshAllQueue } = require('./jobs/queue');
const { createParseLinkWorker } = require('./jobs/parseLink');
const { createRefreshAllWorker } = require('./jobs/refreshAll');

// Prevent Redis version errors from crashing the process
process.on('unhandledRejection', (reason) => {
    if (reason && reason.message && reason.message.includes('Redis version')) {
        logger.warn({ err: reason.message }, 'Suppressed Redis version error');
        return;
    }
    logger.error({ err: reason }, 'Unhandled promise rejection');
});

process.on('uncaughtException', (err) => {
    if (err.message && err.message.includes('Redis version')) {
        logger.warn({ err: err.message }, 'Suppressed Redis version error');
        return;
    }
    logger.error({ err }, 'Uncaught exception — shutting down');
    process.exit(1);
});

// Routes
const authRoutes = require('./routes/auth');
const companiesRoutes = require('./routes/companies');
const linksRoutes = require('./routes/links');
const mondayRoutes = require('./routes/monday');

const app = express();
const server = http.createServer(app);

// Socket.IO
const io = new SocketServer(server, {
    cors: { origin: '*', methods: ['GET', 'POST'] },
});

io.on('connection', (socket) => {
    logger.debug({ socketId: socket.id }, 'Client connected');
    socket.on('disconnect', () => {
        logger.debug({ socketId: socket.id }, 'Client disconnected');
    });
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(globalLimiter);

// Health check
app.get('/api/v1/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API v1 routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/companies', companiesRoutes(io));
app.use('/api/v1/links', linksRoutes);
app.use('/api/v1/monday', mondayRoutes);

// Error handler (must be last)
app.use(errorHandler);

// Start workers (non-fatal if Redis is unavailable)
try {
    createParseLinkWorker(io);
    createRefreshAllWorker();
    logger.info('BullMQ workers started');
} catch (err) {
    logger.warn({ err: err.message }, 'BullMQ workers not started (Redis may not be available or version too old)');
}

// Schedule refresh-all every 6 hours (non-fatal)
if (refreshAllQueue) {
    refreshAllQueue.add('refresh', {}, {
        repeat: { pattern: '0 */6 * * *' },
    }).catch((err) => {
        logger.warn({ err: err.message }, 'Could not schedule refresh-all cron');
    });
}

// Start server
server.listen(config.port, () => {
    logger.info({ port: config.port }, `Backend server running on http://localhost:${config.port}`);
});

module.exports = { app, server, io };
