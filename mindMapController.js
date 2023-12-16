const express = require('express');
const router = express.Router();

// Importing services
const mindMapService = require('../services/mindMapService');

// Route to generate a mind map from a research paper
router.post('/generate', async (req, res) => {
    try {
        const { paperId } = req.body;
        const mindMap = await mindMapService.generateMindMap(paperId);
        res.json(mindMap);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to refine a mind map
router.put('/refine/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const { updates } = req.body;
        const updatedMindMap = await mindMapService.refineMindMap(id, updates);
        res.json(updatedMindMap);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to expand a mind map
router.put('/expand/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const { newNodes } = req.body;
        const expandedMindMap = await mindMapService.expandMindMap(id, newNodes);
        res.json(expandedMindMap);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

module.exports = router;
