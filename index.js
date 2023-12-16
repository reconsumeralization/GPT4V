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
app.use('/api/research-papers', researchPaperController);
app.use('/api/insight-extraction', insightExtractionController);
app.use('/api/ideas', ideaController);
app.use('/api/citation-analysis', citationAnalysisController);
app.use('/api/text-extraction', textExtractionController);
app.use('/api/collaboration', collaborationController);
app.use('/api/data-handler', dataHandler);
app.use('/api/documentation', documentationController);
app.use('/api/influential-papers', influentialPapersController);
app.use('/api/author-network', authorNetworkController);
app.use('/api/suggestions', suggestionController);
app.use('/api/autocomplete', autocompleteController);
app.use('/api/upload-analysis', uploadAnalysisController);
app.use('/api/graph-map', graphMapController);
app.use('/api/mind-map', mindMapController);
app.use('/api/vector-search', vectorSearchController);
app.use('/api/documents', documentController);

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'client/build')));

// The "catchall" handler: for any request that doesn't
// match one above, send back React's index.html file.
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname+'/client/build/index.html'));
});

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Server is running on port ${port}`));
