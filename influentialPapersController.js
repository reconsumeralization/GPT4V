```javascript
const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const ResearchPaper = require('../models/ResearchPaper');

// Get all influential papers
router.get('/', async (req, res) => {
    try {
        const papers = await ResearchPaper.find().sort({citations: -1}).limit(10);
        res.json(papers);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// Get a single influential paper
router.get('/:id', getPaper, (req, res) => {
    res.json(res.paper);
});

// Middleware function for get by ID
async function getPaper(req, res, next) {
    let paper;
    try {
        paper = await ResearchPaper.findById(req.params.id);
        if (paper == null) {
            return res.status(404).json({ message: 'Cannot find paper' });
        }
    } catch (err) {
        return res.status(500).json({ message: err.message });
    }

    res.paper = paper;
    next();
}

module.exports = router;
```
