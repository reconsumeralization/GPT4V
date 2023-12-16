const express = require('express');
const router = express.Router();
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });

// Importing services
const documentService = require('../services/documentService');

// Route to upload a document
router.post('/upload', upload.single('document'), async (req, res) => {
    try {
        const document = await documentService.uploadDocument(req.file);
        res.status(200).json(document);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to get a document
router.get('/:id', async (req, res) => {
    try {
        const document = await documentService.getDocument(req.params.id);
        res.status(200).json(document);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to delete a document
router.delete('/:id', async (req, res) => {
    try {
        const document = await documentService.deleteDocument(req.params.id);
        res.status(200).json(document);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to update a document
router.put('/:id', upload.single('document'), async (req, res) => {
    try {
        const document = await documentService.updateDocument(req.params.id, req.file);
        res.status(200).json(document);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

module.exports = router;
