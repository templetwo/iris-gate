// IRIS Gate Relay - Content Script
// Extracts AI responses and sends to relay server

const RELAY_URL = 'http://localhost:8765';

// Detect which AI platform we're on
function detectPlatform() {
  const hostname = window.location.hostname;
  
  if (hostname.includes('claude.ai')) return 'claude';
  if (hostname.includes('openai.com')) return 'openai';
  if (hostname.includes('x.ai')) return 'xai';
  if (hostname.includes('gemini.google.com')) return 'gemini';
  
  return 'unknown';
}

// Extract latest AI response based on platform
function extractResponse() {
  const platform = detectPlatform();
  
  const selectors = {
    claude: 'div[data-test-render-count] > div > div',
    openai: 'div.markdown',
    xai: 'div.message-content',
    gemini: 'message-content'
  };
  
  const selector = selectors[platform];
  if (!selector) return null;
  
  const elements = document.querySelectorAll(selector);
  if (elements.length === 0) return null;
  
  // Get the last response (most recent)
  const lastResponse = elements[elements.length - 1];
  return lastResponse ? lastResponse.innerText : null;
}

// Register this tab with relay server
async function registerTab() {
  const platform = detectPlatform();
  
  try {
    const response = await fetch(`${RELAY_URL}/register_tab`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tab_id: `${platform}_${Date.now()}`,
        platform: platform,
        url: window.location.href,
        timestamp: new Date().toISOString()
      })
    });
    
    const data = await response.json();
    console.log('†⟡∞ Tab registered with IRIS Gate Relay:', data);
    
  } catch (error) {
    console.error('Failed to register tab:', error);
  }
}

// Check for new prompts from relay server
async function checkQueue() {
  try {
    const response = await fetch(`${RELAY_URL}/tabs`);
    const data = await response.json();
    
    // Check if there are prompts for this tab
    // (Implementation would check queue and insert prompts)
    
  } catch (error) {
    console.error('Failed to check queue:', error);
  }
}

// Monitor for new responses and send to relay
const observer = new MutationObserver(() => {
  const response = extractResponse();
  if (response && response.length > 50) {
    // Store in extension storage for relay pickup
    chrome.storage.local.set({
      [`response_${Date.now()}`]: {
        platform: detectPlatform(),
        content: response,
        timestamp: new Date().toISOString()
      }
    });
  }
});

// Initialize
window.addEventListener('load', () => {
  console.log('†⟡∞ IRIS Gate Relay active');
  
  // Register this tab
  registerTab();
  
  // Start observing for changes
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Check queue periodically
  setInterval(checkQueue, 5000);
});

// Listen for messages from popup/background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'extract_response') {
    const response = extractResponse();
    sendResponse({ response: response });
  }
  
  if (message.action === 'inject_prompt') {
    // Find input field and insert prompt
    const platform = detectPlatform();
    const inputSelectors = {
      claude: 'div[contenteditable="true"]',
      openai: 'textarea',
      xai: 'textarea',
      gemini: 'textarea'
    };
    
    const input = document.querySelector(inputSelectors[platform]);
    if (input) {
      input.innerText = message.prompt;
      sendResponse({ success: true });
    } else {
      sendResponse({ success: false, error: 'Input not found' });
    }
  }
});
