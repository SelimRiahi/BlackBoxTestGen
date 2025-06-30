async function scoreInteractiveElement(page, el) {
  return await el.evaluate(el => {
    const rect = el.getBoundingClientRect();
    const styles = window.getComputedStyle(el);

    // Check if element is visible and sizable
    const isVisible = rect.width > 10 && rect.height > 10 &&
      styles.display !== 'none' &&
      styles.visibility !== 'hidden' &&
      parseFloat(styles.opacity) > 0 &&
      styles.pointerEvents !== 'none';

    if (!isVisible) return { score: 0, tag: el.tagName.toLowerCase(), text: '[hidden]', x: rect.left, y: rect.top };

    let score = 0;

    // Size and visibility
    score += 30;

    // Cursor pointer indicates clickable
    if (styles.cursor === 'pointer') score += 25;

    // Focusable element (tabindex or natural)
    if (el.tabIndex >= 0) score += 15;

    // Accessibility role hints
    const role = el.getAttribute('role') || '';
    if (['button', 'link', 'menuitem', 'checkbox', 'tab', 'switch', 'option'].includes(role.toLowerCase())) {
      score += 30;
    }

    // Tag-based scoring for common interactive elements
    const tag = el.tagName.toLowerCase();
    if (['button', 'a', 'input', 'select', 'textarea', 'summary'].includes(tag)) {
      score += 25;
    }

    // Inside a form? Probably interactive
    if (el.closest('form')) {
      score += 20;
    }

    // Animated transition (may imply interactivity)
    if (styles.transitionDuration && styles.transitionDuration !== '0s') {
      score += 10;
    }

    // Text presence (could indicate button text, label, etc.)
    const text = (el.innerText || el.getAttribute('aria-label') || el.getAttribute('alt') || '').trim();
    if (text.length > 0) {
      score += Math.min(20, text.length); // up to 20 points for text length
    }

    return { score, tag, text: text || '[no-label]', x: rect.left, y: rect.top };
  });
}

async function tryAutoClick(page, visitedSet) {
  const elements = await page.$$('body *');
  const scored = [];

  for (const el of elements) {
    try {
      const data = await scoreInteractiveElement(page, el);

      // Create a unique key for the element to avoid repeated clicks
      // Use tag + text + position rounded to integers
      const uniqueKey = `${data.tag}::${data.text}::${Math.round(data.x)}::${Math.round(data.y)}`;

      if (data.score >= 50 && !visitedSet.has(uniqueKey)) {
        scored.push({ el, ...data, uniqueKey });
      }
    } catch (e) {
      // Ignore evaluation errors on some elements
    }
  }

  // Sort by score descending
  scored.sort((a, b) => b.score - a.score);

  for (const item of scored) {
    const { el, text, x, y, uniqueKey } = item;
    visitedSet.add(uniqueKey);
    console.log(`🧠 Trying "${text}" at (${x.toFixed(0)}, ${y.toFixed(0)}) with score ${item.score}`);

    const oldUrl = page.url();
    const oldHtml = await page.content();

    try {
      // Try native click, fallback to mouse click if fails
      await Promise.all([
        el.click().catch(() => page.mouse.click(x + 2, y + 2)),
        page.waitForTimeout(2500), // slightly longer wait for changes
      ]);
    } catch (err) {
      console.warn(`⚠️ Click failed on "${text}":`, err.message);
    }

    const newUrl = page.url();
    const newHtml = await page.content();

    if (newUrl !== oldUrl || oldHtml !== newHtml) {
      console.log('✅ Navigation or DOM changed.');
      return newUrl;
    }
  }

  console.log('⚠️ No interactive elements caused navigation or DOM change.');
  return null;
}

module.exports = { tryAutoClick };
