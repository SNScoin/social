/**
 * Auth Routes — thin routing layer.
 * Maps HTTP verbs to controller methods + applies middleware.
 */

const { Router } = require('express');
const authController = require('../controllers/auth');
const auth = require('../middleware/auth');
const { authLimiter } = require('../middleware/rateLimiter');

const router = Router();

// Public
router.post('/login', authLimiter, authController.login);
router.post('/register', authLimiter, authController.register);

// Protected
router.get('/me', auth, authController.me);

module.exports = router;
