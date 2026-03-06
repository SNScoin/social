/**
 * Company controller — HTTP request/response handling.
 * Validates input, delegates to companyService, returns JSON.
 */

const companyService = require('../services/companies');
const { validateCreateCompany, validateCreateFromMonday, validateCompanyId } = require('../validators/companies');

async function list(req, res, next) {
    try {
        const companies = await companyService.listCompanies(req.user.id);
        res.json(companies);
    } catch (err) {
        next(err);
    }
}

async function getById(req, res, next) {
    try {
        const v = validateCompanyId(req.params);
        if (!v.valid) return res.status(400).json({ error: 'VALIDATION_ERROR', errors: v.errors });

        const company = await companyService.getCompanyById(v.data.id, req.user.id);
        res.json(company);
    } catch (err) {
        if (err.status) return res.status(err.status).json({ error: err.code, message: err.message });
        next(err);
    }
}

async function create(req, res, next) {
    try {
        const v = validateCreateCompany(req.body);
        if (!v.valid) return res.status(400).json({ error: 'VALIDATION_ERROR', errors: v.errors });

        const company = await companyService.createManualCompany(v.data.name, req.user.id);
        res.status(201).json(company);
    } catch (err) {
        next(err);
    }
}

async function createFromMonday(req, res, next) {
    try {
        const v = validateCreateFromMonday(req.body);
        if (!v.valid) return res.status(400).json({ error: 'VALIDATION_ERROR', errors: v.errors });

        const company = await companyService.createFromMonday(v.data, req.user.id);
        res.status(201).json(company);
    } catch (err) {
        next(err);
    }
}

async function sync(req, res, next, io) {
    try {
        const v = validateCompanyId(req.params);
        if (!v.valid) return res.status(400).json({ error: 'VALIDATION_ERROR', errors: v.errors });

        const result = await companyService.syncCompany(v.data.id, req.user.id, io);
        res.json(result);
    } catch (err) {
        if (err.status) return res.status(err.status).json({ error: err.code, message: err.message });
        next(err);
    }
}

async function stats(req, res, next) {
    try {
        const v = validateCompanyId(req.params);
        if (!v.valid) return res.status(400).json({ error: 'VALIDATION_ERROR', errors: v.errors });

        // Verify ownership first
        await companyService.getCompanyById(v.data.id, req.user.id);
        const result = await companyService.getCompanyStats(v.data.id);
        res.json(result);
    } catch (err) {
        if (err.status) return res.status(err.status).json({ error: err.code, message: err.message });
        next(err);
    }
}

async function update(req, res, next) {
    try {
        const v = validateCompanyId(req.params);
        if (!v.valid) return res.status(400).json({ error: 'VALIDATION_ERROR', errors: v.errors });

        const company = await companyService.updateCompany(v.data.id, req.user.id, req.body);
        res.json(company);
    } catch (err) {
        if (err.status) return res.status(err.status).json({ error: err.code, message: err.message });
        next(err);
    }
}

async function remove(req, res, next) {
    try {
        const v = validateCompanyId(req.params);
        if (!v.valid) return res.status(400).json({ error: 'VALIDATION_ERROR', errors: v.errors });

        const result = await companyService.deleteCompany(v.data.id, req.user.id);
        res.json(result);
    } catch (err) {
        if (err.status) return res.status(err.status).json({ error: err.code, message: err.message });
        next(err);
    }
}

module.exports = { list, getById, create, createFromMonday, sync, stats, update, remove };
