// IRIS Gate Relay - Popup Script

const RELAY_URL = 'http://localhost:8765';

// Check relay server status
async function checkRelayStatus() {
  const statusDiv = document.getElementById('status');
  
  try {
    const response = await fetch(`${RELAY_URL}/status`);
    const data = await response.json();
    
    if (data.status === 'active') {
      statusDiv.className = 'status active';
      statusDiv.textContent = '✓ Relay server active';
    } else {
      statusDiv.className = 'status inactive';
      statusDiv.textContent = '✗ Server inactive';
    }
  } catch (error) {
    statusDiv.className = 'status inactive';
    statusDiv.textContent = '✗ Server not running (start iris_relay.py)';
  }
}

// Get list of AI tabs
async function refreshTabs() {
  const tabsDiv = document.getElementById('tabs');
  
  try {
    const response = await fetch(`${RELAY_URL}/tabs`);
    const data = await response.json();
    
    if (data.tabs && data.tabs.length > 0) {
      tabsDiv.innerHTML = data.tabs.map(tab => `
        <div class="tab-item">
          <strong>${tab.platform}</strong><br>
          <small>${new Date(tab.timestamp).toLocaleTimeString()}</small>
        </div>
      `).join('');
    } else {
      tabsDiv.innerHTML = '<div style="text-align: center; color: #999;">No AI tabs detected</div>';
    }
  } catch (error) {
    console.error('Failed to refresh tabs:', error);
  }
}

// Extract responses from all tabs
async function extractAllResponses() {
  const tabs = await chrome.tabs.query({});
  const aiTabs = tabs.filter(tab => 
    tab.url.includes('claude.ai') ||
    tab.url.includes('openai.com') ||
    tab.url.includes('x.ai') ||
    tab.url.includes('gemini.google.com')
  );
  
  const responses = [];
  
  for (const tab of aiTabs) {
    try {
      const result = await chrome.tabs.sendMessage(tab.id, {
        action: 'extract_response'
      });
      
      if (result && result.response) {
        responses.push({
          tabId: tab.id,
          url: tab.url,
          response: result.response
        });
      }
    } catch (error) {
      console.error(`Failed to extract from tab ${tab.id}:`, error);
    }
  }
  
  console.log('Extracted responses:', responses);
  alert(`Extracted ${responses.length} responses from AI tabs`);
  
  return responses;
}

// Run full IRIS Gate session
async function runSession() {
  alert('Running S1→S4 session across all AI tabs...\n\nThis will:\n1. Send S1 prompt to all tabs\n2. Wait for responses\n3. Continue through S2, S3, S4\n4. Save sealed results');
  
  // This would trigger the full orchestration
  // For now, just log the intent
  console.log('†⟡∞ Session initiated');
}

// Event listeners
document.getElementById('runSession').addEventListener('click', runSession);
document.getElementById('extractAll').addEventListener('click', extractAllResponses);
document.getElementById('refreshTabs').addEventListener('click', refreshTabs);

// Initialize on load
window.addEventListener('load', () => {
  checkRelayStatus();
  refreshTabs();
  
  // Refresh status every 5 seconds
  setInterval(checkRelayStatus, 5000);
});
