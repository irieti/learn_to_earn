export default function TaskView() {
    const [task, setTask] = useState(null);
    const [input, setInput] = useState(''); // For proof submission
  
    useEffect(() => {
      const taskId = window.location.pathname.split('/').pop();
      fetch(`/api/tasks/get/${taskId}`)
        .then(res => res.json())
        .then(data => setTask(data));
    }, []);
  
    const submitProof = async () => {
      const response = await fetch(`/api/tasks/verify/${task.id}`, {
        method: 'POST',
        body: JSON.stringify({ proof: input })
      });
      
      if (response.ok) {
        Telegram.WebApp.showAlert('Task verified! Rewards granted 🎉');
        window.location.href = '/';
      }
    };
  
    return (
      <div style={styles.container}>
        {task?.verification_type === 'quiz' ? (
          <QuizComponent questions={task.quiz_questions} />
        ) : (
          <>
            <h1>{task?.title}</h1>
            <p>{task?.description}</p>
            
            <div style={styles.proofSection}>
              <h3>Submit Proof:</h3>
              {task?.verification_type === 'transaction' && (
                <p>Paste your transaction hash</p>
              )}
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                style={styles.input}
              />
              <button 
                style={styles.submitButton}
                onClick={submitProof}
              >
                Submit
              </button>
            </div>
          </>
        )}
      </div>
    );
  }