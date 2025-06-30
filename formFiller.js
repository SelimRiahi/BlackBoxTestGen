// formFiller.js

// Simple Dice coefficient for fuzzy string similarity
function diceCoefficient(a, b) {
  if (!a || !b) return 0;
  a = a.toLowerCase();
  b = b.toLowerCase();
  if (a === b) return 1;

  const bigrams = s => {
    const v = [];
    for (let i = 0; i < s.length - 1; i++) {
      v.push(s.slice(i, i + 2));
    }
    return v;
  };

  const aBigrams = bigrams(a);
  const bBigrams = bigrams(b);
  const set = new Set(bBigrams);

  let hits = 0;
  for (const bigram of aBigrams) {
    if (set.has(bigram)) {
      hits++;
      set.delete(bigram);
    }
  }

  return (2.0 * hits) / (aBigrams.length + bBigrams.length);
}

// Distance between OCR bbox and element bbox
function distanceBetween(bbox1, bbox2) {
  const x1 = (bbox1.x0 + bbox1.x1) / 2;
  const y1 = (bbox1.y0 + bbox1.y1) / 2;
  const x2 = bbox2.x + bbox2.width / 2;
  const y2 = bbox2.y + bbox2.height / 2;
  return Math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2);
}

// Combined scoring: text similarity + normalized distance
function combinedScore(labelText, element, labelBBox) {
  const sources = [element.placeholder, element.ariaLabel, element.name, element.id, element.linkedLabel].filter(Boolean);


  // Max text similarity between label and element attributes
  let maxTextSim = 0;
  for (const src of sources) {
    const sim = diceCoefficient(labelText, src);
    if (sim > maxTextSim) maxTextSim = sim;
  }

  // Normalize distance to 0-1 (1 = very close)
  const maxDist = 300; // pixels, tweak as needed
  const dist = distanceBetween(labelBBox, element.boundingBox);
  const distScore = dist > maxDist ? 0 : 1 - dist / maxDist;

  // Weighted sum (adjust weights if needed)
  return 0.7 * maxTextSim + 0.3 * distScore;
}

// Finds best input element for a label by scoring candidates
function findBestInputForLabel(label, words, inputs) {
  const labelWord = words.find(w => w.text.toLowerCase().includes(label.toLowerCase()));
  if (!labelWord) return null;

  const candidates = inputs
    .filter(el => ['input', 'textarea', 'select'].includes(el.tag))
    .map(el => {
      const score = combinedScore(labelWord.text.toLowerCase(), el, labelWord.bbox);
      return { el, score };
    })
    .filter(c => c.score > 0.4); // threshold to ignore weak matches

  if (candidates.length === 0) return null;

  candidates.sort((a, b) => b.score - a.score);

  console.log(`🎯 Best match for label "${label}" is "${candidates[0].el.name || candidates[0].el.id || candidates[0].el.placeholder}" with score ${candidates[0].score.toFixed(2)}`);

  return candidates[0].el;
}

async function fillFormSmart(page, fillData, elements, ocrWords) {
  for (const [label, value] of Object.entries(fillData)) {
    // First, try matching by exact attributes (placeholder, aria-label, name, id)
    let matched = elements.find(el => {
      if (!['input', 'textarea', 'select'].includes(el.tag)) return false;
      const source = el.placeholder || el.ariaLabel || el.name || el.id;
      return source && source.toLowerCase().includes(label.toLowerCase());
    });

    // If no exact attribute match, try fuzzy+proximity match
    if (!matched) {
      matched = findBestInputForLabel(label, ocrWords, elements);
    }

    if (!matched) {
      console.warn(`⚠️ No match found for "${label}"`);
      continue;
    }

    const { x, y, width, height } = matched.boundingBox;
    const clickX = x + width / 2;
    const clickY = y + height / 2;

    console.log(`🖊 Filling "${label}" with "${value}" at [${clickX}, ${clickY}]`);

    await page.mouse.click(clickX, clickY);
    await page.keyboard.type(value.toString(), { delay: 100 });
  }
}

module.exports = { fillFormSmart };
