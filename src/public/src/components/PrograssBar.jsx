export default function ProgressBar({ xp, level }) {
    // Calculate progress to next level (every 100 XP = 1 level)
    const currentLevelXp = xp % 100;
    const progress = (currentLevelXp / 100) * 100;
  
    return (
      <div style={styles.container}>
        <div style={styles.levelBadge}>Level {level}</div>
        
        <div style={styles.barBackground}>
          <div 
            style={{
              ...styles.barFill,
              width: `${progress}%`
            }}
          />
        </div>
        
        <div style={styles.xpText}>
          {currentLevelXp}/100 XP to next level
        </div>
      </div>
    );
  }
  
  const styles = {
    container: {
      margin: '12px 0'
    },
    barBackground: {
      height: '8px',
      backgroundColor: '#e5e7eb',
      borderRadius: '4px',
      margin: '4px 0'
    },
    barFill: {
      height: '100%',
      backgroundColor: '#10b981', // Emerald green
      borderRadius: '4px',
      transition: 'width 0.3s ease'
    },
    levelBadge: {
      fontWeight: 'bold',
      fontSize: '14px'
    },
    xpText: {
      fontSize: '12px',
      color: '#6b7280'
    }
  };