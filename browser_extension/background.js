// IRIS Gate Relay - Background Service Worker

const RELAY_URL = 'http://localhost:8765';

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('†⟡∞ IRIS Gate Relay Extension installed');
  
  // Initialize storage
  chrome.storage.local.set({
    sessions: [],
    responses: {}
  });
});

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    const isAITab = 
      tab.url.includes('claude.ai') ||
      tab.url.includes('openai.com') ||
      tab.url.includes('x.ai') ||
      tab.url.includes('gemini.google.com');
    
    if (isAITab) {
      console.log('†⟡∞ AI tab detected:', tab.url);
    }
  }
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'store_response') {
    // Store response in local storage
    chrome.storage.local.get(['responses'], (result) => {
      const responses = result.responses || {};
      responses[`${sender.tab.id}_${Date.now()}`] = message.data;
      
      chrome.storage.local.set({ responses }, () => {
        sendResponse({ success: true });
      });
    });
    
    return true; // Keep message channel open for async response
  }
  
  if (message.action === 'get_all_responses') {
    chrome.storage.local.get(['responses'], (result) => {
      sendResponse({ responses: result.responses || {} });
    });
    
    return true;
  }
});

// Periodic sync with relay server
setInterval(async () => {
  try {
    // Check if relay server is running
    const response = await fetch(`${RELAY_URL}/status`);
    const data = await response.json();
    
    if (data.status === 'active') {
      // Sync local storage with relay server
      chrome.storage.local.get(['responses'], async (result) => {
        if (Object.keys(result.responses || {}).length > 0) {
          console.log('†⟡∞ Syncing responses with relay server');
          // Implementation would send responses to relay
        }
      });
    }
  } catch (error) {
    // Relay server not running, that's okay
  }
}, 10000); // Every 10 seconds
