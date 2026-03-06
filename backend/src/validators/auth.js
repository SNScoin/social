/**
 * Auth Validators — input validation functions for auth endpoints
 */

function validateLoginInput(body) {
    const errors = [];

    if (!body.email || typeof body.email !== 'string' || !body.email.trim()) {
        errors.push({ field: 'email', message: 'Email is required' });
    }

    if (!body.password || typeof body.password !== 'string' || !body.password.trim()) {
        errors.push({ field: 'password', message: 'Password is required' });
    }

    return {
        valid: errors.length === 0,
        errors,
        data: errors.length === 0 ? {
            email: body.email.trim().toLowerCase(),
            password: body.password,
        } : null,
    };
}

function validateRegisterInput(body) {
    const errors = [];

    if (!body.username || typeof body.username !== 'string' || body.username.trim().length < 3) {
        errors.push({ field: 'username', message: 'Username must be at least 3 characters' });
    }

    if (!body.email || typeof body.email !== 'string') {
        errors.push({ field: 'email', message: 'Email is required' });
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email)) {
        errors.push({ field: 'email', message: 'Invalid email format' });
    }

    if (!body.password || typeof body.password !== 'string' || body.password.length < 6) {
        errors.push({ field: 'password', message: 'Password must be at least 6 characters' });
    }

    return {
        valid: errors.length === 0,
        errors,
        data: errors.length === 0 ? {
            username: body.username.trim(),
            email: body.email.trim().toLowerCase(),
            password: body.password,
            displayName: body.display_name || body.username.trim(),
        } : null,
    };
}

module.exports = { validateLoginInput, validateRegisterInput };
