const express = require('express');
const router = express.Router();

// Importing the Vector Search Service
const VectorSearchService = require('../services/VectorSearchService');

// Route to perform vector search
router.post('/search', async (req, res) => {
    try {
        const { query, options } = req.body;
        const results = await VectorSearchService.search(query, options);
        res.json(results);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to add a document to the vector search index
router.post('/index', async (req, res) => {
    try {
        const { document } = req.body;
        const result = await VectorSearchService.index(document);
        res.json(result);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

module.exports = router;
