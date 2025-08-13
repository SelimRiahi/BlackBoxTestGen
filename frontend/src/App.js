import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:3000';

function App() {
  const [auth, setAuth] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    title: '',
    description: '',
    priority: 'medium',
    categoryId: '',
    dueDate: ''
  });
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [updatingTasks, setUpdatingTasks] = useState({});

  const showSuccess = (msg) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setAuth(null);
    setTasks([]);
    setError('');
    showSuccess('Logged out successfully.');
  }, []);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const tasksRes = await axios.get(`${API_URL}/tasks`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      setTasks(tasksRes.data);
    } catch (err) {
      console.error('Data load error:', err);
      if (err.response?.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  }, [logout]);

  const fetchCategories = async () => {
    try {
      const res = await axios.get(`${API_URL}/categories`);
      setCategories(res.data);
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setAuth({ token });
      loadData();
      fetchCategories();
    }
  }, [loadData]);

  const register = async () => {
    try {
      setError('');
      await axios.post(`${API_URL}/register`, {
        username: formData.username,
        password: formData.password
      }, {
        headers: { 'Content-Type': 'application/json' },
        withCredentials: true
      });
      showSuccess('Registration successful! Please log in.');
      setFormData({ ...formData, username: '', password: '' });
    } catch (err) {
      setError(`Registration failed: ${err.response?.data?.error || err.message}`);
    }
  };

  const login = async () => {
    try {
      setError('');
      const res = await axios.post(`${API_URL}/login`, {
        username: formData.username,
        password: formData.password
      });
      localStorage.setItem('token', res.data.token);
      setAuth(res.data);
      setFormData({ ...formData, username: '', password: '' });
      await loadData();
      await fetchCategories();
      showSuccess('Login successful!');
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const createTask = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/tasks`, {
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        categoryId: formData.categoryId || undefined,
        dueDate: formData.dueDate || undefined
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      setFormData({
        ...formData,
        title: '',
        description: '',
        categoryId: '',
        dueDate: ''
      });
      await loadData();
      showSuccess('Task created successfully!');
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/tasks/${taskId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      await loadData();
      showSuccess('Task deleted successfully.');
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const toggleTaskCompletion = async (taskId, currentStatus) => {
    try {
      setUpdatingTasks(prev => ({ ...prev, [taskId]: true }));
      const token = localStorage.getItem('token');
      await axios.patch(
        `${API_URL}/tasks/${taskId}`,
        { completed: !currentStatus },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      await loadData();
      showSuccess(`Task marked as ${!currentStatus ? 'completed' : 'incomplete'}.`);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setUpdatingTasks(prev => ({ ...prev, [taskId]: false }));
    }
  };

  return (
    <div className="App" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }} id="app-container">
      {successMessage && (
        <div style={{ background: '#d4edda', padding: '10px', marginBottom: '10px', borderRadius: '5px', color: '#155724' }}>
          {successMessage}
        </div>
      )}
      {!auth ? (
        <div className="auth-section" style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }} id="auth-section">
          <h2 id="auth-heading">Login/Register</h2>
          {error && <p style={{ color: 'red' }} id="auth-error">{error}</p>}
          <input
            id="username-input"
            style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
            placeholder="Username"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          />
          <input
            id="password-input"
            style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          <button 
            id="login-button"
            style={{ marginRight: '10px', padding: '8px 15px' }} 
            onClick={login}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Login'}
          </button>
          <button 
            id="register-button"
            style={{ padding: '8px 15px' }} 
            onClick={register}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Register'}
          </button>
        </div>
      ) : (
        <>
          <button 
            id="logout-button"
            style={{ float: 'right', padding: '5px 10px' }} 
            onClick={logout}
          >
            Logout
          </button>
          <div className="task-form" style={{ margin: '20px 0', padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }} id="task-form">
            <h3 id="create-task-heading">Create Task</h3>
            {error && <p style={{ color: 'red' }} id="task-error">{error}</p>}
            <input
              id="task-title-input"
              style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
              placeholder="Title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />
            <textarea
              id="task-description-input"
              style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%', minHeight: '100px' }}
              placeholder="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
            <select
              id="task-priority-select"
              style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <select
              id="task-category-select"
              style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
              value={formData.categoryId}
              onChange={(e) => setFormData({ ...formData, categoryId: e.target.value })}
            >
              <option value="">Select Category</option>
              {categories.map((cat) => (
                <option key={cat._id} value={cat._id}>{cat.name}</option>
              ))}
            </select>
            <input
              id="task-due-date-input"
              type="date"
              style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
              value={formData.dueDate}
              onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
              min={new Date().toISOString().split('T')[0]}
            />
            <button 
              id="add-task-button"
              style={{ padding: '8px 15px' }} 
              onClick={createTask}
              disabled={loading || !formData.title}
            >
              {loading ? 'Adding...' : 'Add Task'}
            </button>
          </div>
          <div className="task-list" id="task-list">
            <h3 id="task-list-heading">Your Tasks</h3>
            {loading && tasks.length === 0 ? (
              <p id="loading-tasks-message">Loading tasks...</p>
            ) : tasks.length === 0 ? (
              <p id="no-tasks-message">No tasks found</p>
            ) : (
              tasks.map(task => (
                <div
                  key={task._id}
                  id={`task-${task._id}`}
                  style={{
                    margin: '10px 0',
                    padding: '15px',
                    border: '1px solid #eee',
                    borderRadius: '5px',
                    backgroundColor: task.completed ? '#e8f5e9' : '#f9f9f9',
                    position: 'relative'
                  }}
                >
                  <button 
                    id={`delete-task-${task._id}-button`}
                    style={{
                      position: 'absolute',
                      top: '10px',
                      right: '10px',
                      background: '#ff4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '3px',
                      padding: '3px 8px',
                      cursor: 'pointer'
                    }}
                    onClick={() => deleteTask(task._id)}
                  >
                    Delete
                  </button>
                  <input
                    id={`task-completion-${task._id}-checkbox`}
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => toggleTaskCompletion(task._id, task.completed)}
                    disabled={updatingTasks[task._id]}
                    style={{ 
                      marginRight: '10px', 
                      cursor: updatingTasks[task._id] ? 'wait' : 'pointer'
                    }}
                  />
                  <h4 
                    id={`task-title-${task._id}`}
                    style={{ 
                      marginTop: 0,
                      textDecoration: task.completed ? 'line-through' : 'none',
                      color: task.completed ? '#888' : 'inherit'
                    }}
                  >
                    {task.title}
                  </h4>
                  <p 
                    id={`task-description-${task._id}`}
                    style={{
                      textDecoration: task.completed ? 'line-through' : 'none',
                      color: task.completed ? '#888' : 'inherit'
                    }}
                  >
                    {task.description}
                  </p>
                  <span id={`task-priority-${task._id}`}>Priority: {task.priority}</span><br />
                  {task.dueDate && (
                    <p id={`task-due-date-${task._id}`}>
                      Due: {new Date(task.dueDate).toLocaleDateString()}
                      {new Date(task.dueDate) < new Date() && !task.completed && (
                        <span style={{ color: 'red', marginLeft: '5px' }}>(Overdue)</span>
                      )}
                    </p>
                  )}
                  {task.categoryId?.name && (
                    <span 
                      id={`task-category-${task._id}`}
                      style={{
                        color: task.categoryId.color || '#000',
                        fontWeight: 'bold'
                      }}
                    >
                      Category: {task.categoryId.name}
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default App;