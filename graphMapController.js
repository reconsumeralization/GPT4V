```javascript
const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const GraphMap = require('../models/GraphMap');

// Get all graph maps
router.get('/', async (req, res) => {
  try {
    const graphMaps = await GraphMap.find();
    res.json(graphMaps);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get one graph map
router.get('/:id', getGraphMap, (req, res) => {
  res.json(res.graphMap);
});

// Create one graph map
router.post('/', async (req, res) => {
  const graphMap = new GraphMap({
    title: req.body.title,
    description: req.body.description,
    nodes: req.body.nodes,
    edges: req.body.edges
  });

  try {
    const newGraphMap = await graphMap.save();
    res.status(201).json(newGraphMap);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Update one graph map
router.patch('/:id', getGraphMap, async (req, res) => {
  if (req.body.title != null) {
    res.graphMap.title = req.body.title;
  }
  if (req.body.description != null) {
    res.graphMap.description = req.body.description;
  }
  if (req.body.nodes != null) {
    res.graphMap.nodes = req.body.nodes;
  }
  if (req.body.edges != null) {
    res.graphMap.edges = req.body.edges;
  }
  try {
    const updatedGraphMap = await res.graphMap.save();
    res.json(updatedGraphMap);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Delete one graph map
router.delete('/:id', getGraphMap, async (req, res) => {
  try {
    await res.graphMap.remove();
    res.json({ message: 'Deleted Graph Map' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Middleware function for get by ID
async function getGraphMap(req, res, next) {
  let graphMap;
  try {
    graphMap = await GraphMap.findById(req.params.id);
    if (graphMap == null) {
      return res.status(404).json({ message: 'Cannot find graph map' });
    }
  } catch (err) {
    return res.status(500).json({ message: err.message });
  }

  res.graphMap = graphMap;
  next();
}

module.exports = router;
```
