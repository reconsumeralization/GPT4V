const express = require('express');
const router = express.Router();

// Importing services
const documentationService = require('../services/documentationService');

// Route to get documentation
router.get('/', async (req, res) => {
    try {
        const documentation = await documentationService.getDocumentation();
        res.json(documentation);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// Route to update documentation
router.put('/', async (req, res) => {
    try {
        const updatedDocumentation = await documentationService.updateDocumentation(req.body);
        res.json(updatedDocumentation);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// Route to delete documentation
router.delete('/', async (req, res) => {
    try {
        const deletedDocumentation = await documentationService.deleteDocumentation();
        res.json(deletedDocumentation);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

module.exports = router;
