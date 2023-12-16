const express = require('express');
const router = express.Router();
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });

// Importing services
const researchPaperService = require('../services/researchPaperService');

// Route to upload a research paper
router.post('/upload', upload.single('paper'), async (req, res) => {
    try {
        const paper = req.file;
        const metadata = await researchPaperService.extractMetadata(paper);
        res.status(200).json(metadata);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to get all research papers
router.get('/', async (req, res) => {
    try {
        const papers = await researchPaperService.getAllPapers();
        res.status(200).json(papers);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to get a specific research paper by id
router.get('/:id', async (req, res) => {
    try {
        const paper = await researchPaperService.getPaperById(req.params.id);
        res.status(200).json(paper);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Route to delete a specific research paper by id
router.delete('/:id', async (req, res) => {
    try {
        await researchPaperService.deletePaperById(req.params.id);
        res.status(200).json({ message: 'Research paper deleted successfully.' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

module.exports = router;
