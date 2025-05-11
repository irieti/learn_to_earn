export default function RewardBadge({ type, value }) {
    const icons = {
      xp: '🪙',
      token: '✨',
      nft: '🖼️'
    };
  
    return (
      <div style={{
        ...styles.badge,
        backgroundColor: type === 'nft' ? '#8b5cf6' : '#f59e0b'
      }}>
        <span style={styles.icon}>{icons[type]}</span>
        <span style={styles.value}>
          {type === 'nft' ? 'NFT Badge' : value}
        </span>
      </div>
    );
  }
  
  const styles = {
    badge: {
      display: 'inline-flex',
      alignItems: 'center',
      padding: '4px 8px',
      borderRadius: '12px',
      color: 'white',
      fontSize: '12px',
      marginRight: '6px'
    },
    icon: {
      marginRight: '4px'
    },
    value: {
      fontWeight: 'bold'
    }
  };