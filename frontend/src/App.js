import React, { useState, useEffect } from 'react';
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
    priority: 'medium'
  });
  const [error, setError] = useState('');

  // Check for existing token on load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setAuth({ token });
      loadData();
    }
  }, []);

  // Auth functions
 const register = async () => {
  try {
    const res = await axios.post('http://localhost:3000/register', {
      username: formData.username,
      password: formData.password
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      withCredentials: true
    });
    console.log('Registration success!', res.data);
    login();
  } catch (err) {
    console.error('Full error:', {
      message: err.message,
      response: err.response?.data,
      config: err.config
    });
    alert(`Registration failed: ${err.response?.data?.error || err.message}`);
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
      setFormData({...formData, username: '', password: ''});
      loadData();
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      console.error('Login error:', err);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setAuth(null);
    setTasks([]);
  };

  // Task functions
  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [tasksRes, categoriesRes] = await Promise.all([
        axios.get(`${API_URL}/tasks`, {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }),
        axios.get(`${API_URL}/categories`, {
          headers: { 
            'Content-Type': 'application/json'
          }
        })
      ]);
      setTasks(tasksRes.data);
      setCategories(categoriesRes.data);
    } catch (err) {
      console.error('Data load error:', err);
      if (err.response?.status === 401) {
        logout();
      }
    }
  };

  const createTask = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/tasks`, {
        title: formData.title,
        description: formData.description,
        priority: formData.priority
      }, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      setFormData({...formData, title: '', description: ''});
      loadData();
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      console.error('Task creation error:', err);
    }
  };

  return (
    <div className="App" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      {!auth ? (
        <div className="auth-section" style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
          <h2>Login/Register</h2>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <input
            style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
            placeholder="Username"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
          />
          <input
            style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
          />
          <button 
            style={{ marginRight: '10px', padding: '8px 15px' }}
            onClick={login}
          >
            Login
          </button>
          <button 
            style={{ padding: '8px 15px' }}
            onClick={register}
          >
            Register
          </button>
        </div>
      ) : (
        <>
          <button 
            style={{ float: 'right', padding: '5px 10px' }}
            onClick={logout}
          >
            Logout
          </button>
          <div className="task-form" style={{ margin: '20px 0', padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
            <h3>Create Task</h3>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <input
              style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
              placeholder="Title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
            />
            <textarea
              style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%', minHeight: '100px' }}
              placeholder="Description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
            <select
              style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
              value={formData.priority}
              onChange={(e) => setFormData({...formData, priority: e.target.value})}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <button 
              style={{ padding: '8px 15px' }}
              onClick={createTask}
            >
              Add Task
            </button>
          </div>
          <div className="task-list">
            <h3>Your Tasks</h3>
            {tasks.length === 0 ? (
              <p>No tasks found</p>
            ) : (
              tasks.map(task => (
                <div 
                  key={task._id} 
                  className="task-card" 
                  style={{ 
                    margin: '10px 0', 
                    padding: '15px', 
                    border: '1px solid #eee', 
                    borderRadius: '5px',
                    backgroundColor: '#f9f9f9'
                  }}
                >
                  <h4 style={{ marginTop: 0 }}>{task.title}</h4>
                  <p>{task.description}</p>
                  <span>Priority: {task.priority}</span>
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