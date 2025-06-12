require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');

// Initialize Express
const app = express();
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

// Task Model
const Task = mongoose.model('Task', new mongoose.Schema({
  title: String,
  completed: {
    type: Boolean,
    default: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}));

// Routes
app.post('/tasks', async (req, res) => {
  if (!req.body.title || typeof req.body.title !== 'string' || req.body.title.trim() === '') {
    return res.status(400).json({ error: 'Title is required' });
  }
  try {
    const task = new Task({ title: req.body.title });
    await task.save();
    res.status(201).json(task);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.get('/tasks', async (req, res) => {
  try {
    const tasks = await Task.find();
    res.json(tasks);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Start Server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});