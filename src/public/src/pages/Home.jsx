import { useEffect, useState } from 'react';
import TaskCard from '../components/TaskCard';

export default function Home() {
  const [tasks, setTasks] = useState([]);
  const [user, setUser] = useState(null);

  // Load data on init
  useEffect(() => {
    Telegram.WebApp.expand();
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    const tgUser = Telegram.WebApp.initDataUnsafe.user;
    const response = await fetch(`/api/user/profile/${tgUser.id}`);
    const data = await response.json();
    setUser(data.profile);
    loadTasks(data.profile.telegram_id);
  };

  const loadTasks = async (userId) => {
    const res = await fetch(`/api/tasks/current/${userId}`);
    setTasks(await res.json());
  };

  const startTask = (taskId) => {
    Telegram.WebApp.showPopup({
      title: 'Confirm',
      message: 'Start this task?',
      buttons: [{
        id: 'start',
        type: 'default',
        text: 'Let\'s go!'
      }]
    }, (btnId) => {
      if (btnId === 'start') {
        window.location.href = `/task/${taskId}`;
      }
    });
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.greeting}>👋 Hello, {user?.first_name || 'Web3 Explorer'}!</h1>
      
      <div style={styles.progressSection}>
        <h3>Level {user?.level || 1} Adventurer</h3>
        <ProgressBar xp={user?.xp_points || 0} />
      </div>

      <h2 style={styles.sectionTitle}>Your Tasks</h2>
      {tasks.map(task => (
        <TaskCard 
          key={task.id} 
          task={task} 
          onStart={startTask}
        />
      ))}
    </div>
  );
}