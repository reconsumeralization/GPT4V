```javascript
const mongoose = require('mongoose');

// Replace with your MongoDB connection string
const dbURI = process.env.MONGODB_URI;

const options = {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  useCreateIndex: true,
  useFindAndModify: false,
};

mongoose.connect(dbURI, options).then(
  () => {
    console.log('Database connection established!');
  },
  err => {
    console.log('Error connecting Database instance due to: ', err);
  }
);

// Require your models here
// For example:
// require('./models/ResearchPaper');
// require('./models/Idea');
// ...

module.exports = mongoose;
```
