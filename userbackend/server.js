// server.js for user authentication (Node.js/Express)
const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = 3000;
const USERS_FILE = path.join(__dirname, 'users.json');
const JWT_SECRET = 'hyflow_secret_key'; // Change this in production

app.use(cors());
app.use(bodyParser.json());

// Helper: Load users from file
function loadUsers() {
  if (!fs.existsSync(USERS_FILE)) return {};
  return JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));
}

// Helper: Save users to file
function saveUsers(users) {
  fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
}

// Add status endpoint to respond to frontend check
app.get('/status', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});

// Registration endpoint
app.post('/register', (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }
  const users = loadUsers();
  if (users[email]) {
    return res.status(409).json({ error: 'User already exists.' });
  }
  const hashedPassword = bcrypt.hashSync(password, 10);
  users[email] = { name, email, password: hashedPassword };
  saveUsers(users);
  const token = jwt.sign({ email, name }, JWT_SECRET, { expiresIn: '1d' });
  res.json({ token, name, email });
});

// Login endpoint
app.post('/login', (req, res) => {
  const { email, password } = req.body;
  console.log('Login attempt:', { email, password }); // Log password for debugging (remove in production)
  
  if (!email || !password) {
    console.log('Login failed: Missing email or password');
    return res.status(400).json({ error: 'Email and password are required.' });
  }
  
  const users = loadUsers();
  const user = users[email];
  
  console.log('User found:', !!user, user);
  
  if (!user) {
    console.log('Login failed: User not found');
    return res.status(401).json({ error: 'Invalid email or password.' });
  }
  
  // Log the stored hash and the password being checked
  console.log('Stored hash:', user.password);
  const isPasswordValid = bcrypt.compareSync(password, user.password);
  console.log('Password valid:', isPasswordValid);
  
  if (!isPasswordValid) {
    console.log('Login failed: Invalid password');
    return res.status(401).json({ error: 'Invalid email or password.' });
  }
  
  const token = jwt.sign({ email, name: user.name }, JWT_SECRET, { expiresIn: '1d' });
  console.log('Login successful, token generated');
  res.json({ token, name: user.name, email });
});

// Auth check endpoint (optional)
app.get('/me', (req, res) => {
  const auth = req.headers.authorization;
  if (!auth) return res.status(401).json({ error: 'No token.' });
  try {
    const decoded = jwt.verify(auth.replace('Bearer ', ''), JWT_SECRET);
    res.json(decoded);
  } catch {
    res.status(401).json({ error: 'Invalid token.' });
  }
});

app.listen(PORT, () => {
  console.log(`Auth server running on http://localhost:${PORT}`);
});
