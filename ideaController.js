const express = require('express');
const router = express.Router();

// Importing Idea model
const Idea = require('../models/Idea');

// Route to get all ideas
router.get('/', async (req, res) => {
    try {
        const ideas = await Idea.find();
        res.json(ideas);
    } catch (err) {
        res.json({ message: err });
    }
});

// Route to submit an idea
router.post('/', async (req, res) => {
    const idea = new Idea({
        title: req.body.title,
        description: req.body.description,
        tags: req.body.tags,
        connections: req.body.connections
    });

    try {
        const savedIdea = await idea.save();
        res.json(savedIdea);
    } catch (err) {
        res.json({ message: err });
    }
});

// Route to get a specific idea
router.get('/:ideaId', async (req, res) => {
    try {
        const idea = await Idea.findById(req.params.ideaId);
        res.json(idea);
    } catch (err) {
        res.json({ message: err });
    }
});

// Route to delete an idea
router.delete('/:ideaId', async (req, res) => {
    try {
        const removedIdea = await Idea.remove({ _id: req.params.ideaId });
        res.json(removedIdea);
    } catch (err) {
        res.json({ message: err });
    }
});

// Route to update an idea
router.patch('/:ideaId', async (req, res) => {
    try {
        const updatedIdea = await Idea.updateOne(
            { _id: req.params.ideaId },
            { $set: { title: req.body.title, description: req.body.description, tags: req.body.tags, connections: req.body.connections } }
        );
        res.json(updatedIdea);
    } catch (err) {
        res.json({ message: err });
    }
});

module.exports = router;
