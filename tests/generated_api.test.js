const request = require('supertest');
const api = request('http://localhost:3000');

describe('API Black-box Tests', () => {
  it('POST /tasks success', async () => {
    const res = await api.post('/tasks').send({ "title": "Test Task" });
    expect(res.statusCode).toBe(201);
  });
  it('POST /tasks error 400', async () => {
    const res = await api.post('/tasks').send({});
    expect(res.statusCode).toBe(400);
  });
  it('GET /tasks success', async () => {
    const res = await api.get('/tasks');
    expect(res.statusCode).toBe(200);
  });
});
