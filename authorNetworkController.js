```javascript
const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const AuthorNetwork = require('../models/AuthorNetwork');

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Middleware to handle errors
const handleErrors = (res, err) => {
  console.error(err);
  res.status(500).send({ error: 'An error occurred while processing your request.' });
};

// Route to get all author networks
router.get('/', async (req, res) => {
  try {
    const authorNetworks = await AuthorNetwork.find();
    res.json(authorNetworks);
  } catch (err) {
    handleErrors(res, err);
  }
});

// Route to get a specific author network
router.get('/:id', async (req, res) => {
  try {
    const authorNetwork = await AuthorNetwork.findById(req.params.id);
    if (!authorNetwork) {
      res.status(404).send({ error: 'Author network not found.' });
    } else {
      res.json(authorNetwork);
    }
  } catch (err) {
    handleErrors(res, err);
  }
});

// Route to create a new author network
router.post('/', async (req, res) => {
  try {
    const authorNetwork = new AuthorNetwork(req.body);
    const result = await authorNetwork.save();
    res.json(result);
  } catch (err) {
    handleErrors(res, err);
  }
});

// Route to update an existing author network
router.put('/:id', async (req, res) => {
  try {
    const authorNetwork = await AuthorNetwork.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!authorNetwork) {
      res.status(404).send({ error: 'Author network not found.' });
    } else {
      res.json(authorNetwork);
    }
  } catch (err) {
    handleErrors(res, err);
  }
});

// Route to delete an author network
router.delete('/:id', async (req, res) => {
  try {
    const authorNetwork = await AuthorNetwork.findByIdAndRemove(req.params.id);
    if (!authorNetwork) {
      res.status(404).send({ error: 'Author network not found.' });
    } else {
      res.json({ message: 'Author network deleted successfully.' });
    }
  } catch (err) {
    handleErrors(res, err);
  }
});

module.exports = router;
```
