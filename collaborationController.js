const express = require('express');
const router = express.Router();

// Importing services
const collaborationService = require('../services/collaborationService');

// Route to capture ideas
router.post('/capture', async (req, res) => {
    try {
        const idea = req.body;
        const result = await collaborationService.captureIdea(idea);
        res.status(200).json(result);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route for real-time collaboration
router.post('/collaborate', async (req, res) => {
    try {
        const collaborationData = req.body;
        const result = await collaborationService.collaborate(collaborationData);
        res.status(200).json(result);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to build a dynamic idea network
router.get('/idea-network', async (req, res) => {
    try {
        const result = await collaborationService.buildIdeaNetwork();
        res.status(200).json(result);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

module.exports = router;
