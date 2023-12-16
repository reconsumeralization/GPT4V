```javascript
const mongoose = require('mongoose');
const ResearchPaper = require('./models/ResearchPaper');
const Idea = require('./models/Idea');
const Author = require('./models/Author');

class DataHandler {
  constructor() {
    this.db = mongoose.connection;
  }

  // Function to handle uploading and saving of research papers
  async saveResearchPaper(paperData) {
    const paper = new ResearchPaper(paperData);
    await paper.save();
  }

  // Function to handle saving of ideas
  async saveIdea(ideaData) {
    const idea = new Idea(ideaData);
    await idea.save();
  }

  // Function to handle saving of authors
  async saveAuthor(authorData) {
    const author = new Author(authorData);
    await author.save();
  }

  // Function to handle retrieval of research papers
  async getResearchPapers() {
    return await ResearchPaper.find({});
  }

  // Function to handle retrieval of ideas
  async getIdeas() {
    return await Idea.find({});
  }

  // Function to handle retrieval of authors
  async getAuthors() {
    return await Author.find({});
  }

  // Function to handle retrieval of a specific research paper
  async getResearchPaperById(id) {
    return await ResearchPaper.findById(id);
  }

  // Function to handle retrieval of a specific idea
  async getIdeaById(id) {
    return await Idea.findById(id);
  }

  // Function to handle retrieval of a specific author
  async getAuthorById(id) {
    return await Author.findById(id);
  }

  // Function to handle deletion of a specific research paper
  async deleteResearchPaperById(id) {
    return await ResearchPaper.findByIdAndDelete(id);
  }

  // Function to handle deletion of a specific idea
  async deleteIdeaById(id) {
    return await Idea.findByIdAndDelete(id);
  }

  // Function to handle deletion of a specific author
  async deleteAuthorById(id) {
    return await Author.findByIdAndDelete(id);
  }
}

module.exports = new DataHandler();
```
