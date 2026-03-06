/**
 * Auth Controller — handles HTTP req/res for auth endpoints.
 * Delegates business logic to authService and validation to validators.
 */

const authService = require('../services/auth');
const { validateLoginInput, validateRegisterInput } = require('../validators/auth');

const authController = {
    /**
     * POST /api/v1/auth/login
     */
    async login(req, res, next) {
        try {
            const validation = validateLoginInput(req.body);
            if (!validation.valid) {
                return res.status(400).json({
                    error: 'VALIDATION_ERROR',
                    message: 'Invalid input',
                    details: validation.errors,
                });
            }

            const { user, token } = await authService.login(validation.data);

            res.json({
                token,
                token_type: 'Bearer',
                user,
            });
        } catch (err) {
            if (err.status) {
                return res.status(err.status).json({ error: err.error, message: err.message });
            }
            next(err);
        }
    },

    /**
     * POST /api/v1/auth/register
     */
    async register(req, res, next) {
        try {
            const validation = validateRegisterInput(req.body);
            if (!validation.valid) {
                return res.status(400).json({
                    error: 'VALIDATION_ERROR',
                    message: 'Invalid input',
                    details: validation.errors,
                });
            }

            const { user, token } = await authService.register(validation.data);

            res.status(201).json({
                token,
                token_type: 'Bearer',
                user,
            });
        } catch (err) {
            if (err.status) {
                return res.status(err.status).json({ error: err.error, message: err.message });
            }
            next(err);
        }
    },

    /**
     * GET /api/v1/auth/me
     */
    async me(req, res, next) {
        try {
            const user = await authService.getProfile(req.user.id);
            res.json(user);
        } catch (err) {
            if (err.status) {
                return res.status(err.status).json({ error: err.error, message: err.message });
            }
            next(err);
        }
    },
};

module.exports = authController;
