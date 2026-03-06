/**
 * Company validators — input validation for company endpoints.
 */

function validateCreateCompany(body) {
    const errors = [];
    const { name } = body || {};

    if (!name || typeof name !== 'string' || !name.trim()) {
        errors.push({ field: 'name', message: 'Company name is required' });
    } else if (name.trim().length < 2) {
        errors.push({ field: 'name', message: 'Company name must be at least 2 characters' });
    } else if (name.trim().length > 255) {
        errors.push({ field: 'name', message: 'Company name must be 255 characters or fewer' });
    }

    return errors.length > 0 ? { valid: false, errors } : { valid: true, data: { name: name.trim() } };
}

function validateCreateFromMonday(body) {
    const errors = [];
    const required = ['api_token', 'board_id', 'source_column_id', 'views_column_id', 'likes_column_id', 'comments_column_id'];

    for (const field of required) {
        if (!body[field]) {
            errors.push({ field, message: `${field.replace(/_/g, ' ')} is required` });
        }
    }

    return errors.length > 0
        ? { valid: false, errors }
        : {
            valid: true,
            data: {
                api_token: body.api_token,
                workspace_id: body.workspace_id || null,
                workspace_name: body.workspace_name || '',
                board_id: body.board_id,
                board_name: body.board_name || '',
                source_column_id: body.source_column_id,
                views_column_id: body.views_column_id,
                likes_column_id: body.likes_column_id,
                comments_column_id: body.comments_column_id,
            },
        };
}

function validateCompanyId(params) {
    const id = parseInt(params.id, 10);
    if (isNaN(id) || id <= 0) {
        return { valid: false, errors: [{ field: 'id', message: 'Invalid company ID' }] };
    }
    return { valid: true, data: { id } };
}

module.exports = { validateCreateCompany, validateCreateFromMonday, validateCompanyId };
