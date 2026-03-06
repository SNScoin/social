/**
 * Company routes — thin wiring layer.
 * All logic lives in controllers/companies.js → services/companies.js
 */

const { Router } = require('express');
const auth = require('../middleware/auth');
const ctrl = require('../controllers/companies');

function createCompanyRoutes(io) {
    const router = Router();

    // Collection routes (no :id param)
    router.get('/', auth, ctrl.list);
    router.post('/', auth, ctrl.create);
    router.post('/from-monday', auth, ctrl.createFromMonday);

    // Resource routes (with :id param) — specific paths before :id catch-all
    router.get('/:id/stats', auth, ctrl.stats);
    router.post('/:id/sync', auth, (req, res, next) => ctrl.sync(req, res, next, io));
    router.get('/:id', auth, ctrl.getById);
    router.put('/:id', auth, ctrl.update);
    router.delete('/:id', auth, ctrl.remove);

    return router;
}

module.exports = createCompanyRoutes;
