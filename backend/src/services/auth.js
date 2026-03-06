/**
 * Auth Service — business logic for authentication.
 * All DB queries and bcrypt/JWT operations live here.
 * The route/controller layer stays thin.
 */

const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('../db/pool');
const config = require('../config/env');
const logger = require('../logger');

const SALT_ROUNDS = 10;

class AuthService {
    /**
     * Authenticate a user by email/username and password.
     * @returns {{ user, token }} on success
     * @throws {Object} { status, error, message } on failure
     */
    async login({ email, password }) {
        const result = await pool.query(
            `SELECT id, username, email, hashed_password, display_name, profile_picture
             FROM users
             WHERE email = $1 OR username = $1`,
            [email]
        );

        if (result.rows.length === 0) {
            throw { status: 401, error: 'INVALID_CREDENTIALS', message: 'Incorrect email or password' };
        }

        const user = result.rows[0];
        const valid = await bcrypt.compare(password, user.hashed_password);
        if (!valid) {
            throw { status: 401, error: 'INVALID_CREDENTIALS', message: 'Incorrect email or password' };
        }

        // Update last_login timestamp
        await pool.query('UPDATE users SET last_login = NOW() WHERE id = $1', [user.id]);

        const token = this._signToken(user);

        logger.info({ userId: user.id }, 'User logged in');

        return {
            user: this._sanitizeUser(user),
            token,
        };
    }

    /**
     * Register a new user.
     * @returns {{ user, token }}
     * @throws {Object} { status, error, message } on failure
     */
    async register({ username, email, password, displayName }) {
        // Check for existing user
        const existing = await pool.query(
            'SELECT id FROM users WHERE email = $1 OR username = $2',
            [email, username]
        );
        if (existing.rows.length > 0) {
            throw { status: 409, error: 'CONFLICT', message: 'User with this email or username already exists' };
        }

        const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
        const result = await pool.query(
            `INSERT INTO users (username, email, hashed_password, display_name)
             VALUES ($1, $2, $3, $4)
             RETURNING id, username, email, display_name, profile_picture`,
            [username, email, hashedPassword, displayName]
        );

        const user = result.rows[0];
        const token = this._signToken(user);

        logger.info({ userId: user.id }, 'User registered');

        return {
            user: this._sanitizeUser(user),
            token,
        };
    }

    /**
     * Get current user profile by id.
     * @returns {Object} user
     */
    async getProfile(userId) {
        const result = await pool.query(
            `SELECT id, username, email, display_name, profile_picture, bio, timezone, created_at, last_login
             FROM users WHERE id = $1`,
            [userId]
        );

        if (result.rows.length === 0) {
            throw { status: 404, error: 'USER_NOT_FOUND', message: 'User not found' };
        }

        return result.rows[0];
    }

    // ── Private helpers ──

    _signToken(user) {
        return jwt.sign(
            { sub: user.id, email: user.email },
            config.jwtSecret,
            { expiresIn: `${config.accessTokenExpireMinutes}m` }
        );
    }

    _sanitizeUser(user) {
        return {
            id: user.id,
            username: user.username,
            email: user.email,
            display_name: user.display_name,
            profile_picture: user.profile_picture || null,
        };
    }
}

module.exports = new AuthService();
