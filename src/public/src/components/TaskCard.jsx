import RewardBadge from './RewardBadge';



export default function TaskCard({ task, onStart }) {
    return (
      <div style={styles.card}>
        <div style={styles.header}>
          <span style={styles.typeBadge}>{task.type.toUpperCase()}</span>
          {task.nftReward && <span style={styles.nftBadge}>NFT</span>}
        </div>
        
        <h3 style={styles.title}>{task.title}</h3>
        <p style={styles.desc}>{task.description}</p>
        
        <div style={styles.footer}>
          <div style={styles.rewards}>
            <span>🪙 {task.xp} XP</span>
            {task.tokens > 0 && <span> + {task.tokens} LEARN</span>}
          </div>
          <button 
            style={styles.startButton}
            onClick={() => onStart(task.id)}
          >
            {task.status === 'started' ? 'Continue' : 'Start'}
          </button>
          <div style={styles.rewards}>
        <RewardBadge type="xp" value={task.xp_reward} />
        {task.token_reward > 0 && (
          <RewardBadge type="token" value={task.token_reward} />
        )}
        {task.nft_reward && (
          <RewardBadge type="nft" />
        )}
      </div>
        </div>
      </div>
    );
  }
  
  const styles = {
    card: {
      border: '1px solid #e5e7eb',
      borderRadius: '12px',
      padding: '16px',
      marginBottom: '16px'
    },
    nftBadge: {
      backgroundColor: '#8b5cf6',
      color: 'white',
      padding: '2px 8px',
      borderRadius: '4px',
      fontSize: '12px'
    }
  };