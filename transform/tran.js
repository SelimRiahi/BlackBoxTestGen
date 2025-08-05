const fs = require('fs');
const path = require('path');

const FEATURE_FILE_PATH = 'C:\\Users\\Selim\\OneDrive\\Bureau\\ai test\\model\\generated_tests.feature';

function parseFeatureFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    
    const result = {
      scenarios: [],
      metadata: {
        source_feature: path.basename(filePath),
        generated_at: new Date().toISOString()
      }
    };

    let currentScenario = null;
    let stepCounter = 0;

    lines.forEach(line => {
      line = line.trim();
      
      if (line.startsWith('Scenario:')) {
        if (currentScenario) result.scenarios.push(currentScenario);
        
        currentScenario = {
          scenario_id: `SC-${result.scenarios.length + 1}`,
          name: line.replace('Scenario:', '').trim(),
          steps: []
        };
        stepCounter = 0;
      }
      else if (line.match(/^(Given|When|Then|And|But)\s/i) && currentScenario) {
        currentScenario.steps.push({
          step_id: `${currentScenario.scenario_id}-${(++stepCounter).toString().padStart(2, '0')}`,
          gherkin_text: line.trim(),
          type: "",  // Empty (not removed)
          data: ""   // Empty (not removed)
        });
      }
    });

    if (currentScenario) result.scenarios.push(currentScenario);
    return result;
  } catch (error) {
    console.error('Error parsing feature file:', error);
    return null;
  }
}

const blueprint = parseFeatureFile(FEATURE_FILE_PATH);

if (blueprint) {
  const outputPath = 'C:\\Users\\Selim\\OneDrive\\Bureau\\ai test\\transform\\test_blueprint.json';
  fs.writeFileSync(outputPath, JSON.stringify(blueprint, null, 2));
  console.log(`Blueprint generated: ${outputPath}`);
} else {
  console.error('Failed to generate blueprint');
}