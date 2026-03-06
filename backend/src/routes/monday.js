const { Router } = require('express');
const axios = require('axios');
const auth = require('../middleware/auth');

const router = Router();

const MONDAY_API_URL = 'https://api.monday.com/v2';

/**
 * Helper: make a GraphQL call to Monday.com
 */
async function mondayQuery(apiToken, query, variables = {}) {
    const response = await axios.post(
        MONDAY_API_URL,
        { query, variables },
        { headers: { Authorization: apiToken, 'Content-Type': 'application/json' } }
    );
    return response.data;
}

// POST /api/v1/monday/workspaces
router.post('/workspaces', auth, async (req, res, next) => {
    try {
        const { api_token } = req.body;
        if (!api_token) {
            return res.status(400).json({ error: 'MISSING_REQUIRED_FIELD', message: 'api_token is required' });
        }

        const data = await mondayQuery(api_token, `{ workspaces { id name } }`);
        res.json({ workspaces: data.data?.workspaces || [] });
    } catch (err) {
        next(err);
    }
});

// POST /api/v1/monday/boards
router.post('/boards', auth, async (req, res, next) => {
    try {
        const { api_token, workspace_id } = req.body;
        if (!api_token || !workspace_id) {
            return res.status(400).json({ error: 'MISSING_REQUIRED_FIELD', message: 'api_token and workspace_id are required' });
        }

        const data = await mondayQuery(
            api_token,
            `query ($wsIds: [ID!]) { boards(workspace_ids: $wsIds) { id name } }`,
            { wsIds: [parseInt(workspace_id)] }
        );
        res.json({ boards: data.data?.boards || [] });
    } catch (err) {
        next(err);
    }
});

// POST /api/v1/monday/columns
router.post('/columns', auth, async (req, res, next) => {
    try {
        const { api_token, board_id } = req.body;
        if (!api_token || !board_id) {
            return res.status(400).json({ error: 'MISSING_REQUIRED_FIELD', message: 'api_token and board_id are required' });
        }

        const data = await mondayQuery(
            api_token,
            `query ($boardIds: [ID!]) { boards(ids: $boardIds) { columns { id title type } } }`,
            { boardIds: [parseInt(board_id)] }
        );
        const columns = data.data?.boards?.[0]?.columns || [];
        res.json({ columns });
    } catch (err) {
        next(err);
    }
});

module.exports = router;
