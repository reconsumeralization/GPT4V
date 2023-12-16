```javascript
const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const Citation = require('../models/Citation');

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Middleware to handle errors
const handleErrors = (res, err) => {
  console.error(err);
  res.status(500).send({ message: 'An error occurred while processing your request.' });
};

// Route to get all citations
router.get('/', async (req, res) => {
  try {
    const citations = await Citation.find();
    res.status(200).json(citations);
  } catch (err) {
    handleErrors(res, err);
  }
});

// Route to get a citation by ID
router.get('/:id', async (req, res) => {
  try {
    const citation = await Citation.findById(req.params.id);
    if (!citation) {
      return res.status(404).json({ message: 'Citation not found.' });
    }
    res.status(200).json(citation);
  } catch (err) {
    handleErrors(res, err);
  }
});

// Route to add a new citation
router.post('/', async (req, res) => {
  try {
    const newCitation = new Citation(req.body);
    const savedCitation = await newCitation.save();
    res.status(201).json(savedCitation);
  } catch (err) {
    handleErrors(res, err);
  }
});

// Route to update a citation
router.put('/:id', async (req, res) => {
  try {
    const updatedCitation = await Citation.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!updatedCitation) {
      return res.status(404).json({ message: 'Citation not found.' });
    }
    res.status(200).json(updatedCitation);
  } catch (err) {
    handleErrors(res, err);
  }
});

// Route to delete a citation
router.delete('/:id', async (req, res) => {
  try {
    const deletedCitation = await Citation.findByIdAndRemove(req.params.id);
    if (!deletedCitation) {
      return res.status(404).json({ message: 'Citation not found.' });
    }
    res.status(200).json({ message: 'Citation deleted successfully.' });
  } catch (err) {
    handleErrors(res, err);
  }
});

module.exports = router;
```
