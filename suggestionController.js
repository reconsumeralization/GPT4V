const express = require('express');
const router = express.Router();

// Importing Suggestion model
const Suggestion = require('../models/Suggestion');

// Route to get all suggestions
router.get('/', async (req, res) => {
    try {
        const suggestions = await Suggestion.find();
        res.json(suggestions);
    } catch (err) {
        res.json({ message: err });
    }
});

// Route to submit a suggestion
router.post('/', async (req, res) => {
    const suggestion = new Suggestion({
        title: req.body.title,
        description: req.body.description,
        link: req.body.link,
        tags: req.body.tags
    });

    try {
        const savedSuggestion = await suggestion.save();
        res.json(savedSuggestion);
    } catch (err) {
        res.json({ message: err });
    }
});

// Route to get a specific suggestion
router.get('/:suggestionId', async (req, res) => {
    try {
        const suggestion = await Suggestion.findById(req.params.suggestionId);
        res.json(suggestion);
    } catch (err) {
        res.json({ message: err });
    }
});

// Route to delete a suggestion
router.delete('/:suggestionId', async (req, res) => {
    try {
        const removedSuggestion = await Suggestion.remove({ _id: req.params.suggestionId });
        res.json(removedSuggestion);
    } catch (err) {
        res.json({ message: err });
    }
});

// Route to update a suggestion
router.patch('/:suggestionId', async (req, res) => {
    try {
        const updatedSuggestion = await Suggestion.updateOne(
            { _id: req.params.suggestionId },
            { $set: { title: req.body.title, description: req.body.description, link: req.body.link, tags: req.body.tags } }
        );
        res.json(updatedSuggestion);
    } catch (err) {
        res.json({ message: err });
    }
});

module.exports = router;
