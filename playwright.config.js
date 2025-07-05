// playwright.config.js
module.exports = {
  projects: [
    {
      name: 'generated',
      testDir: './generated_tests',
      testMatch: '**/*.js',
    },
    {
      name: 'root-tests',
      testDir: './tests',
      testMatch: '**/*.js',
    },
  ],
};