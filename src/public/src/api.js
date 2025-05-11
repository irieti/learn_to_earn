export const fetchTasks = async (userId) => {
    const response = await fetch(`${API_URL}/tasks/user-tasks/${userId}`);
    return response.json();
  };
  
  export const verifyTask = async (taskId, proof) => {
    return fetch(`${API_URL}/tasks/verify/${taskId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proof })
    });
  };