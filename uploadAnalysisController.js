const express = require('express');
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });
const fs = require('fs');
const path = require('path');
const { analyzePaper } = require('../utils/analysis');

const router = express.Router();

// Route to upload and analyze research paper
router.post('/upload', upload.single('paper'), async (req, res) => {
    try {
        // Read the uploaded file
        const paperPath = path.join(__dirname, '../uploads/', req.file.filename);
        const paperData = fs.readFileSync(paperPath, 'utf8');

        // Delete the uploaded file after reading
        fs.unlinkSync(paperPath);

        // Analyze the paper
        const analysisResult = await analyzePaper(paperData);

        // Send the analysis result
        res.json(analysisResult);
    } catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Internal server error' });
    }
});

module.exports = router;
