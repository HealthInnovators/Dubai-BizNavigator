/**
 * API service and Server-Sent Events client for Dubai BizNavigator.
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
}

export async function createBusinessProfile(profileData) {
  const response = await fetch(`${API_BASE}/api/v1/business/profile`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profileData),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Failed to create profile: ${response.statusText}`);
  }

  return response.json();
}

export function subscribeToWorkflowStream(profileId, { onMessage, onError, onComplete }) {
  const url = `${API_BASE}/api/v1/business/stream/${profileId}`;
  const eventSource = new EventSource(url);

  eventSource.addEventListener('a2ui_surface', (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
      if (data.event && data.event.status === 'completed') {
        if (onComplete) onComplete(data);
        eventSource.close();
      }
    } catch (err) {
      console.error('Error parsing SSE event data:', err);
    }
  });

  eventSource.onerror = (err) => {
    if (onError) onError(err);
    eventSource.close();
  };

  return () => {
    eventSource.close();
  };
}
