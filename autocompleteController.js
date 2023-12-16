const express = require('express');
const router = express.Router();

// Importing Gemini AI Model for autocomplete
const GeminiAI = require('../utils/GeminiAI');

// Autocomplete endpoint
router.post('/autocomplete', async (req, res) => {
    try {
        // Extracting the text from the request body
        const { text } = req.body;

        // If no text is provided, return an error
        if (!text) {
            return res.status(400).json({ error: 'No text provided for autocomplete.' });
        }

        // Use Gemini AI Model to get autocomplete suggestions
        const suggestions = await GeminiAI.autocomplete(text);

        // Return the suggestions
        return res.status(200).json({ suggestions });
    } catch (error) {
        // If there's an error, return it
        return res.status(500).json({ error: error.message });
    }
});

module.exports = router;
