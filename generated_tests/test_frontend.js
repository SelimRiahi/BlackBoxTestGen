const { test, expect } = require("@playwright/test")

BASE_URL = "http://localhost:3001"

// Test User Authentication (Registration and Login)
const registrationData = { username: 'testUser', password: 'testPassword' }
const loginData = { username: 'testUser', password: 'testPassword' }

test('Register user and auto-login', async ({ request }) => {
  const response = await request.post(`${BASE_URL}/register`, { data: registrationData })
  expect(response.status()).toBe(201)

  // Auto-login after registration
  const token = JSON.parse(await response.text()).token
  await globalThis.setToken(token)

  // Test protected routes (Task Dashboard)
  const taskDashboardResponse = await request.get(`${BASE_URL}/tasks`)
  expect(taskDashboardResponse.status()).toBe(200)
})

test('Login with valid credentials', async ({ request }) => {
  await globalThis.setToken(null) // Logout the user

  const response = await request.post(`${BASE_URL}/login`, { data: loginData })
  expect(response.status()).toBe(200)

  const token = JSON.parse(await response.text()).token
  await globalThis.setToken(token) // Set the new token

  // Test protected routes (Task Dashboard)
  const taskDashboardResponse = await request.get(`${BASE_URL}/tasks`)
  expect(taskDashboardResponse.status()).toBe(200)
})

test('Login with invalid credentials', async ({ request }) => {
  await globalThis.setToken(null) // Logout the user

  const invalidCredentialsData = { username: 'invalidUser', password: 'wrongPassword' }
  const response = await request.post(`${BASE_URL}/login`, { data: invalidCredentialsData })
  expect(response.status()).toBe(401)
})

// Test Task Management (CRUD)
const taskData = { title: 'Test Task', description: 'This is a test task.', priority: 'medium' }

test('Create a new task', async ({ request }) => {
  await globalThis.setToken(await getTestUserToken()) // Use the token of the test user

  const response = await request.post(`${BASE_URL}/tasks`, { data: taskData })
  expect(response.status()).toBe(201)
})

test('View a task', async ({ request }) => {
  const createdTaskResponse = await createTaskAndGetResponse() // Create and get the response of the new task
  const taskId = JSON.parse(await createdTaskResponse.text())._id

  const viewTaskResponse = await request.get(`${BASE_URL}/tasks/${taskId}`)
  expect(viewTaskResponse.status()).toBe(200)
})

test('Edit a task', async ({ request }) => {
  const createdTaskResponse = await createTaskAndGetResponse() // Create and get the response of the new task
  const taskId = JSON.parse(await createdTaskResponse.text())._id

  const updatedTaskData = { title: 'Updated Test Task' }
  const response = await request.patch(`${BASE_URL}/tasks/${taskId}`, { data: updatedTaskData })
  expect(response.status()).toBe(200)
})

test('Delete a task', async ({ request }) => {
  const createdTaskResponse = await createTaskAndGetResponse() // Create and get the response of the new task
  const taskId = JSON.parse(await createdTaskResponse.text())._id

  const response = await request.delete(`${BASE_URL}/tasks/${taskId}`)
  expect(response.status()).toBe(204)
})

// Test Error Cases (Validation, Unauthorized, Not Found, etc.)
test('Create a task with invalid data', async ({ request }) => {
  await globalThis.setToken(await getTestUserToken()) // Use the token of the test user

  const response = await request.post(`${BASE_URL}/tasks`, { data: { title: '' } })
  expect(response.status()).toBe(400)
})

test('View a non-existent task', async ({ request }) => {
  const response = await request.get(`${BASE_URL}/tasks/non-existent-id`)
  expect(response.status()).toBe(404)
})

test('Edit a non-existent task', async ({ request }) => {
  const response = await request.patch(`${BASE_URL}/tasks/non-existent-id`, { data: {} })
  expect(response.status()).toBe(404)
})

test('Delete a non-existent task', async ({ request }) => {
  const response = await request.delete(`${BASE_URL}/tasks/non-existent-id`)
  expect(response.status()).toBe(404)
})

// Test Search Functionality
test('Search tasks by title', async ({ request }) => {
  await globalThis.setToken(await getTestUserToken()) // Use the token of the test user

  const createdTaskResponse1 = await createTaskAndGetResponse() // Create and get the response of the first task
  const createdTaskResponse2 = await createTaskAndGetResponse() // Create and get the response of the second task

  const searchResponse = await request.get(`${BASE_URL}/tasks/search?q=Test`)
  expect(searchResponse.status()).toBe(200)

  const [firstResult] = JSON.parse(await searchResponse.text()).results
  expect(firstResult._id).toEqual(createdTaskResponse1._id)
})