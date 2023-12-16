const express = require('express');
const router = express.Router();
const GeminiAI = require('../utils/GeminiAI');

// AI-Powered Insight Extraction
router.post('/extractInsights', async (req, res) => {
    try {
        const { document } = req.body;
        if (!document) {
            return res.status(400).json({ error: 'Document is required.' });
        }

        // Extract key insights from the document using GeminiAI
        const insights = await GeminiAI.extractInsights(document);

        // Generate dynamic mind maps for deeper exploration
        const mindMap = await GeminiAI.generateMindMap(insights);

        return res.status(200).json({ insights, mindMap });
    } catch (error) {
        console.error(error);
        return res.status(500).json({ error: 'An error occurred while extracting insights.' });
    }
});

module.exports = router;
