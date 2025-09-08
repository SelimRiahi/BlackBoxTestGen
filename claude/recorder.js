// ===== REFINED BLACK-BOX TEST GENERATOR =====
// Copy and paste this entire script into your browser's DevTools Console

(function() {
    'use strict';
    
    // Recording state
    let isRecording = false;
    let testSteps = [];
    let inputBuffers = new Map();
    let inputTimers = new Map();
    let messageHistory = new Set();
    let staticElementsCache = new Set();
    let lastSignificantContent = '';
    let messageCheckInterval = null;
    let domObserver = null;
    let recentActions = [];
    
    // Create floating control panel
    const panel = document.createElement('div');
    panel.id = 'test-recorder-panel';
    panel.style.cssText = `
        position: fixed !important;
        top: 10px !important;
        right: 10px !important;
        z-index: 2147483647 !important;
        background: linear-gradient(135deg, #2c3e50, #4a90e2) !important;
        color: white !important;
        padding: 12px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
        font-family: monospace !important;
        min-width: 300px !important;
        font-size: 11px !important;
    `;
    
    panel.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span id="recorder-status">🎯 Smart Test Recorder</span>
            <span id="step-counter" style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 12px; font-size: 9px;">0 steps</span>
        </div>
        <div style="display: flex; gap: 5px; margin-bottom: 6px;">
            <button id="start-recording" style="background: #27ae60; color: white; border: none; padding: 5px 8px; border-radius: 3px; cursor: pointer; flex: 1; font-size: 9px;">▶ Start</button>
            <button id="stop-recording" style="background: #e74c3c; color: white; border: none; padding: 5px 8px; border-radius: 3px; cursor: pointer; flex: 1; font-size: 9px;" disabled>⏹ Stop</button>
            <button id="download-steps" style="background: #3498db; color: white; border: none; padding: 5px 8px; border-radius: 3px; cursor: pointer; flex: 1; font-size: 9px;" disabled>💾 Export</button>
        </div>
        <div style="font-size: 9px; color: rgba(255,255,255,0.8); margin-bottom: 5px;">
            Delay: <input id="input-delay" type="number" value="1500" min="500" max="3000" 
            style="width: 40px; padding: 1px; border: none; border-radius: 2px; background: rgba(255,255,255,0.3); color: white; font-size: 9px;">ms
        </div>
        <div style="font-size: 8px; color: rgba(255,255,255,0.6);">
            <label style="display: block;"><input id="smart-messages" type="checkbox" checked> 🧠 Smart Messages</label>
            <label style="display: block;"><input id="capture-content" type="checkbox"> 📄 Page Content</label>
        </div>
    `;
    document.body.appendChild(panel);
    
    // Get control elements
    const statusElement = document.getElementById('recorder-status');
    const counterElement = document.getElementById('step-counter');
    const startBtn = document.getElementById('start-recording');
    const stopBtn = document.getElementById('stop-recording');
    const downloadBtn = document.getElementById('download-steps');
    const inputDelayElement = document.getElementById('input-delay');
    const smartMessagesCheckbox = document.getElementById('smart-messages');
    const captureContentCheckbox = document.getElementById('capture-content');
    
    // Utility functions
    function addTestStep(step) {
        if (testSteps.length > 0 && testSteps[testSteps.length - 1] === step) {
            return;
        }
        
        testSteps.push(step);
        counterElement.textContent = `${testSteps.length} steps`;
        console.log('📝 Step:', step);
    }
    
    function recordAction(type, element) {
        recentActions.push({
            type,
            element,
            timestamp: Date.now()
        });
        
        // Keep only recent actions (last 5 seconds)
        const cutoff = Date.now() - 5000;
        recentActions = recentActions.filter(action => action.timestamp > cutoff);
    }
    
    function getBestSelector(element) {
        if (element.id) return `#${element.id}`;
        if (element.name) return `[name="${element.name}"]`;
        
        if (element.className) {
            const classes = element.className.split(' ').filter(c => 
                c.length > 0 && 
                !c.includes('ng-') && 
                !c.includes('ui-') && 
                !c.includes('v-') &&
                !c.includes('_') &&
                c.length < 25
            );
            if (classes.length > 0) {
                return `.${classes[0]}`;
            }
        }
        
        const parent = element.parentElement;
        if (parent) {
            const siblings = Array.from(parent.children).filter(el => el.tagName === element.tagName);
            if (siblings.length > 1) {
                const index = siblings.indexOf(element) + 1;
                return `${element.tagName.toLowerCase()}:nth-child(${index})`;
            }
        }
        
        return element.tagName.toLowerCase();
    }
    
    // Cache static elements to avoid detecting them as new messages
    function cacheStaticElements() {
        const staticSelectors = [
            'nav *', 'header *', 'footer *', '.navbar *', '.menu *',
            '.sidebar *', '.navigation *', 'button', 'a[href]', 'label'
        ];
        
        staticSelectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    if (!el.closest('#test-recorder-panel')) {
                        const text = el.textContent?.trim();
                        if (text && text.length < 50) {
                            staticElementsCache.add(text.toLowerCase());
                        }
                    }
                });
            } catch (e) {
                // Continue if selector fails
            }
        });
    }
    
    // Smart message detection - filters out static UI elements
    function detectSmartMessages() {
        const messages = [];
        
        // Look for elements with dynamic content or message-like characteristics
        const allElements = document.querySelectorAll('*:not(script):not(style):not(noscript)');
        
        allElements.forEach(element => {
            if (element.closest('#test-recorder-panel')) return;
            
            // Check visibility
            const rect = element.getBoundingClientRect();
            const style = getComputedStyle(element);
            
            const isVisible = rect.width > 0 && rect.height > 0 && 
                            style.display !== 'none' && 
                            style.visibility !== 'hidden' && 
                            style.opacity !== '0';
            
            if (!isVisible) return;
            
            // Get direct text content only
            const directText = Array.from(element.childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE)
                .map(node => node.textContent.trim())
                .join(' ')
                .trim();
            
            if (!directText || directText.length < 4 || directText.length > 200) return;
            
            const lowerText = directText.toLowerCase();
            
            // Skip if this looks like a static UI element
            if (staticElementsCache.has(lowerText)) return;
            
            // Message indicators
            const strongMessageKeywords = [
                'successful', 'successfully', 'created successfully', 'deleted successfully',
                'completed successfully', 'saved successfully', 'updated successfully',
                'marked as completed', 'marked as', 'registration successful',
                'login successful', 'logout successful', 'logged out successfully',
                'task created', 'task deleted', 'task marked', 'task completed',
                'error occurred', 'failed to', 'invalid', 'required field',
                'please try again', 'not found', 'already exists',
                'welcome', 'thank you', 'congratulations'
            ];
            
            const hasStrongKeyword = strongMessageKeywords.some(keyword => 
                lowerText.includes(keyword)
            );
            
            const hasExclamation = directText.includes('!');
            const hasMessageStyling = element.className.toLowerCase().match(
                /(message|alert|success|error|warning|info|notice|toast|notification|flash|feedback|status|result|banner)/
            );
            
            // Enhanced detection for actual messages
            const looksLikeMessage = hasStrongKeyword || 
                (hasExclamation && hasMessageStyling) ||
                (hasMessageStyling && lowerText.includes('please'));
            
            // Additional filter: recently appeared elements are more likely to be messages
            const wasTriggeredByRecentAction = recentActions.some(action => 
                Date.now() - action.timestamp < 2000
            );
            
            if (looksLikeMessage && (hasStrongKeyword || hasMessageStyling || wasTriggeredByRecentAction)) {
                const isNew = !messageHistory.has(directText);
                messages.push({
                    text: directText,
                    element: element,
                    isNew: isNew,
                    priority: hasStrongKeyword ? 'high' : 'normal'
                });
            }
        });
        
        return messages;
    }
    
    // Smart message monitoring
    function startSmartMessageMonitoring() {
        if (messageCheckInterval) {
            clearInterval(messageCheckInterval);
        }
        
        const checkMessages = () => {
            if (!isRecording || !smartMessagesCheckbox.checked) return;
            
            try {
                const messages = detectSmartMessages();
                
                // Prioritize high-confidence messages
                const highPriorityMessages = messages.filter(m => m.priority === 'high' && m.isNew);
                const normalMessages = messages.filter(m => m.priority === 'normal' && m.isNew);
                
                [...highPriorityMessages, ...normalMessages].forEach(msg => {
                    if (msg.text.trim().length > 0) {
                        messageHistory.add(msg.text);
                        addTestStep(`await (page, 'should see message', \`${msg.text.replace(/`/g, '\\`')}\`);`);
                        
                        // Monitor for disappearance
                        setTimeout(() => {
                            try {
                                const rect = msg.element.getBoundingClientRect();
                                const style = getComputedStyle(msg.element);
                                
                                const isGone = rect.width === 0 || rect.height === 0 || 
                                              style.display === 'none' || 
                                              style.visibility === 'hidden' || 
                                              style.opacity === '0';
                                
                                if (isGone) {
                                    addTestStep(`await (page, 'message should disappear', \`${msg.text.replace(/`/g, '\\`')}\`);`);
                                }
                            } catch (e) {
                                addTestStep(`await (page, 'message should disappear', \`${msg.text.replace(/`/g, '\\`')}\`);`);
                            }
                        }, 3500);
                    }
                });
            } catch (e) {
                console.warn('Smart message detection error:', e);
            }
        };
        
        messageCheckInterval = setInterval(checkMessages, 400);
    }
    
    // Improved content capture with deduplication
    function capturePageContent() {
        if (!captureContentCheckbox.checked) return;
        
        const contentElements = [];
        
        // Focus on meaningful content changes
        const selectors = [
            'h1, h2, h3', // Main headings only
            'button:not(.btn-sm):not(.btn-xs)', // Significant buttons only
            'input[type="submit"]',
            '.task-item', '.item', '.card-title', // Common content patterns
            '[data-testid]' // Test-friendly elements
        ];
        
        selectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    if (el.closest('#test-recorder-panel')) return;
                    
                    const text = (el.textContent || el.value || '').trim();
                    if (text && text.length > 2 && text.length < 60 && 
                        !staticElementsCache.has(text.toLowerCase())) {
                        contentElements.push(text);
                    }
                });
            } catch (e) {
                // Continue if selector fails
            }
        });
        
        if (contentElements.length > 0) {
            const newContent = contentElements.slice(0, 5).join(' | '); // Limit to 5 items
            
            if (newContent !== lastSignificantContent) {
                addTestStep(`await (page, 'should see content', \`${newContent.replace(/`/g, '\\`')}\`);`);
                lastSignificantContent = newContent;
            }
        }
    }
    
    function handleInputComplete(element, finalValue) {
        const selector = getBestSelector(element);
        if (finalValue && finalValue.trim().length > 0) {
            addTestStep(`await (page, 'enter', '${selector}', \`${finalValue.replace(/`/g, '\\`')}\`);`);
            recordAction('input', element);
        }
    }
    
    function isClickableElement(element) {
        const clickableTypes = ['button', 'submit', 'reset'];
        const clickableTags = ['BUTTON', 'A'];
        
        return clickableTags.includes(element.tagName) || 
               (element.tagName === 'INPUT' && clickableTypes.includes(element.type)) ||
               element.type === 'checkbox' ||
               element.type === 'radio' ||
               element.hasAttribute('onclick') ||
               element.getAttribute('role') === 'button';
    }
    
    function handleClick(element) {
        if (isClickableElement(element)) {
            const selector = getBestSelector(element);
            
            // Special handling for checkboxes - avoid duplicate steps
            if (element.type === 'checkbox') {
                addTestStep(`await (page, 'click', '${selector}');`);
                recordAction('checkbox', element);
            } else {
                addTestStep(`await (page, 'click', '${selector}');`);
                recordAction('click', element);
            }
        }
    }
    
    function handleSelect(element, value) {
        const selector = getBestSelector(element);
        if (value) {
            addTestStep(`await (page, 'select', '${selector}', '${value}');`);
            recordAction('select', element);
        }
    }
    
    // Enhanced DOM observer
    function startDOMObserver() {
        if (domObserver) {
            domObserver.disconnect();
        }
        
        domObserver = new MutationObserver(function(mutations) {
            if (!isRecording) return;
            
            let hasSignificantChange = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === Node.ELEMENT_NODE && !node.closest('#test-recorder-panel')) {
                            const text = node.textContent?.trim() || '';
                            // Only consider significant new content
                            if (text.length > 10 && !staticElementsCache.has(text.toLowerCase())) {
                                hasSignificantChange = true;
                            }
                        }
                    });
                }
            });
            
            if (hasSignificantChange) {
                setTimeout(() => {
                    capturePageContent();
                }, 600);
            }
        });
        
        domObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Event listeners
    function attachListeners() {
        const inputDelay = parseInt(inputDelayElement.value) || 1500;
        
        // Input handling
        document.addEventListener('input', function(e) {
            if (!isRecording || e.target.closest('#test-recorder-panel')) return;
            
            const element = e.target;
            if (element.tagName.toLowerCase() === 'select') return;
            
            const elementKey = getBestSelector(element);
            
            if (inputTimers.has(elementKey)) {
                clearTimeout(inputTimers.get(elementKey));
            }
            
            const timer = setTimeout(() => {
                handleInputComplete(element, element.value);
                inputTimers.delete(elementKey);
            }, inputDelay);
            
            inputTimers.set(elementKey, timer);
        }, true);
        
        // Blur for immediate capture
        document.addEventListener('blur', function(e) {
            if (!isRecording || e.target.closest('#test-recorder-panel')) return;
            
            const element = e.target;
            const elementKey = getBestSelector(element);
            
            if (inputTimers.has(elementKey)) {
                clearTimeout(inputTimers.get(elementKey));
                inputTimers.delete(elementKey);
                handleInputComplete(element, element.value);
            }
        }, true);
        
        // Click handling with smart message detection
        document.addEventListener('click', function(e) {
            if (!isRecording || e.target.closest('#test-recorder-panel')) return;
            
            const element = e.target;
            
            if (isClickableElement(element)) {
                handleClick(element);
                
                // Enhanced message detection after meaningful interactions
                setTimeout(() => {
                    if (smartMessagesCheckbox.checked) {
                        const messages = detectSmartMessages();
                        messages.filter(m => m.isNew && m.priority === 'high').forEach(msg => {
                            messageHistory.add(msg.text);
                            addTestStep(`await (page, 'should see message', \`${msg.text.replace(/`/g, '\\`')}\`);`);
                        });
                    }
                }, 700);
                
                // Content update after interaction
                setTimeout(() => {
                    capturePageContent();
                }, 1000);
            }
        }, true);
        
        // Select changes
        document.addEventListener('change', function(e) {
            if (!isRecording || e.target.closest('#test-recorder-panel')) return;
            
            if (e.target.tagName.toLowerCase() === 'select') {
                handleSelect(e.target, e.target.value);
            }
        }, true);
        
        // Form submissions
        document.addEventListener('submit', function(e) {
            if (!isRecording) return;
            
            // Flush pending inputs
            inputTimers.forEach((timer, key) => {
                clearTimeout(timer);
                const element = document.querySelector(key);
                if (element && element.value) {
                    handleInputComplete(element, element.value);
                }
            });
            inputTimers.clear();
            
            recordAction('submit', e.target);
            
            setTimeout(() => {
                if (smartMessagesCheckbox.checked) {
                    const messages = detectSmartMessages();
                    messages.filter(m => m.isNew).forEach(msg => {
                        messageHistory.add(msg.text);
                        addTestStep(`await (page, 'should see message', \`${msg.text.replace(/`/g, '\\`')}\`);`);
                    });
                }
                capturePageContent();
            }, 1200);
        }, true);
        
        // Navigation monitoring
        let currentUrl = window.location.href;
        setInterval(() => {
            if (!isRecording) return;
            if (window.location.href !== currentUrl) {
                addTestStep(`await (page, 'navigate to', '${window.location.href}');`);
                currentUrl = window.location.href;
                messageHistory.clear();
                staticElementsCache.clear();
                lastSignificantContent = '';
                recentActions = [];
                
                setTimeout(() => {
                    cacheStaticElements();
                    capturePageContent();
                }, 1500);
            }
        }, 1000);
    }
    
    // Control functions
    function startRecording() {
        isRecording = true;
        testSteps = [];
        messageHistory.clear();
        staticElementsCache.clear();
        lastSignificantContent = '';
        recentActions = [];
        inputTimers.clear();
        
        statusElement.textContent = '🔴 Recording...';
        startBtn.disabled = true;
        stopBtn.disabled = false;
        downloadBtn.disabled = true;
        
        addTestStep(`await (page, 'navigate to', '${window.location.href}');`);
        
        // Cache static elements first
        setTimeout(() => {
            cacheStaticElements();
            attachListeners();
            startDOMObserver();
            startSmartMessageMonitoring();
            capturePageContent();
        }, 500);
        
        console.log('🎬 Smart test recording started!');
    }
    
    function stopRecording() {
        isRecording = false;
        
        // Cleanup
        inputTimers.forEach((timer, key) => {
            clearTimeout(timer);
            const element = document.querySelector(key);
            if (element && element.value) {
                handleInputComplete(element, element.value);
            }
        });
        inputTimers.clear();
        
        if (domObserver) domObserver.disconnect();
        if (messageCheckInterval) clearInterval(messageCheckInterval);
        
        statusElement.textContent = '⏹️ Stopped';
        startBtn.disabled = false;
        stopBtn.disabled = true;
        downloadBtn.disabled = false;
        
        console.log('⏹️ Recording stopped!', testSteps.length, 'smart steps captured');
    }
    
    function downloadSteps() {
        const testData = {
            metadata: {
                recordingDate: new Date().toISOString(),
                totalSteps: testSteps.length,
                startUrl: window.location.href,
                settings: {
                    smartMessages: smartMessagesCheckbox.checked,
                    captureContent: captureContentCheckbox.checked,
                    inputDelay: parseInt(inputDelayElement.value)
                }
            },
            testSteps: testSteps
        };
        
        const blob = new Blob([JSON.stringify(testData, null, 2)], { 
            type: 'application/json' 
        });
        
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `smart-test-steps-${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        console.log('💾 Smart test steps exported!');
        testSteps.forEach((step, i) => console.log(`${i + 1}:`, step));
    }
    
    // Attach event listeners
    startBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
    downloadBtn.addEventListener('click', downloadSteps);
    
    console.log('🎯 Smart Black-box Test Generator ready!');
    console.log('🧠 Features:');
    console.log('  ✅ Static element filtering');
    console.log('  ✅ Smart message detection');
    console.log('  ✅ Action-triggered monitoring');
    console.log('  ✅ Reduced false positives');
    console.log('  ✅ Clean checkbox handling');
    
    // Cleanup function
    window.cleanupTestRecorder = function() {
        if (domObserver) domObserver.disconnect();
        if (messageCheckInterval) clearInterval(messageCheckInterval);
        inputTimers.forEach(timer => clearTimeout(timer));
        inputTimers.clear();
        const panel = document.getElementById('test-recorder-panel');
        if (panel) panel.remove();
        console.log('🧹 Smart recorder cleaned up!');
    };
    
})();
"implemented in devtools console"