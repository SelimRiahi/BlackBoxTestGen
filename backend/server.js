require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const app = express();
console.log("MONGODB_URI value:", process.env.MONGODB_URI);

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001'], // Allow both ports
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.options('*', cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/taskdb', {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => {
  console.error('MongoDB connection error:', err);
  process.exit(1);
});

// Models
const userSchema = new mongoose.Schema({
  username: { 
    type: String, 
    required: true, 
    unique: true, 
    minlength: 3, 
    maxlength: 30,
    trim: true
  },
  password: { 
    type: String, 
    required: true, 
    minlength: 8 
  },
  role: { 
    type: String, 
    enum: ['user', 'admin'], 
    default: 'user' 
  }
});

const categorySchema = new mongoose.Schema({
  name: { 
    type: String, 
    required: true, 
    unique: true, 
    minlength: 3, 
    maxlength: 50,
    trim: true
  },
  color: { 
    type: String, 
    default: '#000000',
    match: /^#[0-9A-Fa-f]{6}$/
  }
});

const taskSchema = new mongoose.Schema({
  title: { 
    type: String, 
    required: true, 
    minlength: 3, 
    maxlength: 100,
    trim: true
  },
  description: { 
    type: String, 
    maxlength: 500,
    trim: true
  },
  priority: { 
    type: String, 
    enum: ['low', 'medium', 'high'], 
    default: 'medium' 
  },
  completed: { 
    type: Boolean, 
    default: false 
  },
  dueDate: { 
    type: Date,
    validate: {
      validator: function(v) {
        return !v || v > new Date();
      },
      message: 'Due date must be in the future'
    }
  },
  createdAt: { 
    type: Date, 
    default: Date.now 
  },
  userId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'User', 
    required: true 
  },
  categoryId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Category' 
  }
});

const User = mongoose.model('User', userSchema);
const Category = mongoose.model('Category', categorySchema);
const Task = mongoose.model('Task', taskSchema);

// Middleware
const authenticate = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    if (!token) {
      return res.status(401).json({ error: 'Authorization token required' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');
    const user = await User.findById(decoded.userId);
    
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }

    req.user = user;
    req.token = token;
    next();
  } catch (err) {
    console.error('Authentication error:', err);
    res.status(401).json({ error: 'Please authenticate' });
  }
};

// Auth Routes
app.post('/register', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }

    const existingUser = await User.findOne({ username });
    if (existingUser) {
      return res.status(409).json({ error: 'Username already exists' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = new User({ username, password: hashedPassword });
    
    await user.save();
    
    const token = jwt.sign(
      { userId: user._id },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '1h' }
    );

    res.status(201).json({
      _id: user._id,
      username: user.username,
      role: user.role,
      token
    });
  } catch (err) {
    console.error('Registration error:', err);
    res.status(400).json({ error: err.message });
  }
});

app.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }

    const user = await User.findOne({ username });
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const token = jwt.sign(
      { userId: user._id },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '1h' }
    );

    res.json({
      token,
      userId: user._id,
      username: user.username,
      role: user.role
    });
  } catch (err) {
    console.error('Login error:', err);
    res.status(400).json({ error: err.message });
  }
});

// User Routes
app.get('/users/me', authenticate, async (req, res) => {
  res.json({
    _id: req.user._id,
    username: req.user.username,
    role: req.user.role
  });
});

// Category Routes
app.post('/categories', authenticate, async (req, res) => {
  try {
    const category = new Category(req.body);
    await category.save();
    res.status(201).json(category);
  } catch (err) {
    console.error('Category creation error:', err);
    res.status(400).json({ error: err.message });
  }
});

app.get('/categories', async (req, res) => {
  try {
    const categories = await Category.find();
    res.json(categories);
  } catch (err) {
    console.error('Categories fetch error:', err);
    res.status(500).json({ error: 'Failed to fetch categories' });
  }
});

// Task Routes
app.post('/tasks', authenticate, async (req, res) => {
  try {
    const task = new Task({
      ...req.body,
      userId: req.user._id
    });
    
    await task.save();
    res.status(201).json(task);
  } catch (err) {
    console.error('Task creation error:', err);
    res.status(400).json({ error: err.message });
  }
});

app.get('/tasks', authenticate, async (req, res) => {
  try {
    const tasks = await Task.find({ userId: req.user._id })
      .populate('categoryId', 'name color')
      .sort({ createdAt: -1 });
      
    res.json(tasks);
  } catch (err) {
    console.error('Tasks fetch error:', err);
    res.status(500).json({ error: 'Failed to fetch tasks' });
  }
});

app.get('/tasks/:id', authenticate, async (req, res) => {
  try {
    const task = await Task.findOne({
      _id: req.params.id,
      userId: req.user._id
    }).populate('categoryId', 'name color');

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    res.json(task);
  } catch (err) {
    console.error('Task fetch error:', err);
    res.status(400).json({ error: err.message });
  }
});

app.patch('/tasks/:id', authenticate, async (req, res) => {
  try {
    const task = await Task.findOneAndUpdate(
      { _id: req.params.id, userId: req.user._id },
      req.body,
      { new: true, runValidators: true }
    );

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    res.json(task);
  } catch (err) {
    console.error('Task update error:', err);
    res.status(400).json({ error: err.message });
  }
});

app.delete('/tasks/:id', authenticate, async (req, res) => {
  try {
    const task = await Task.findOneAndDelete({
      _id: req.params.id,
      userId: req.user._id
    });

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    res.status(204).end();
  } catch (err) {
    console.error('Task deletion error:', err);
    res.status(400).json({ error: err.message });
  }
});

app.get('/tasks/search', authenticate, async (req, res) => {
  try {
    const { q } = req.query;
    
    if (!q) {
      return res.status(400).json({ error: 'Search query required' });
    }

    const tasks = await Task.find({
      userId: req.user._id,
      title: { $regex: q, $options: 'i' }
    }).populate('categoryId', 'name color');

    res.json(tasks);
  } catch (err) {
    console.error('Task search error:', err);
    res.status(400).json({ error: err.message });
  }
});

// Error Handling Middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

// Start Server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});