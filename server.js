const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

// Importing controllers
const researchPaperController = require('./researchPaperController');
const insightExtractionController = require('./insightExtractionController');
const ideaController = require('./ideaController');
const citationAnalysisController = require('./citationAnalysisController');
const textExtractionController = require('./textExtractionController');
const collaborationController = require('./collaborationController');
const dataHandler = require('./dataHandler');
const documentationController = require('./documentationController');
const influentialPapersController = require('./influentialPapersController');
const authorNetworkController = require('./authorNetworkController');
const suggestionController = require('./suggestionController');
const autocompleteController = require('./autocompleteController');
const uploadAnalysisController = require('./uploadAnalysisController');
const graphMapController = require('./graphMapController');
const mindMapController = require('./mindMapController');
const vectorSearchController = require('./vectorSearchController');
const documentController = require('./documentController');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Routes
app.use('/api/research', researchPaperController);
app.use('/api/insight', insightExtractionController);
app.use('/api/idea', ideaController);
app.use('/api/citation', citationAnalysisController);
app.use('/api/text', textExtractionController);
app.use('/api/collaboration', collaborationController);
app.use('/api/data', dataHandler);
app.use('/api/documentation', documentationController);
app.use('/api/influential', influentialPapersController);
app.use('/api/author', authorNetworkController);
app.use('/api/suggestion', suggestionController);
app.use('/api/autocomplete', autocompleteController);
app.use('/api/upload', uploadAnalysisController);
app.use('/api/graph', graphMapController);
app.use('/api/mindmap', mindMapController);
app.use('/api/vector', vectorSearchController);
app.use('/api/document', documentController);

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'client/build')));

// The "catchall" handler: for any request that doesn't
// match one above, send back React's index.html file.
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname+'/client/build/index.html'));
});

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Server is running on port ${port}`));

module.exports = app;
