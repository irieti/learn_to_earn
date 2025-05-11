import { useState, useEffect } from 'react';
import { Camera, Book, Award, Zap, ChevronRight, Check, User, Wallet, Gift } from 'lucide-react';

// Mock data to simulate backend responses
const MOCK_USER = {
  telegramId: "123456789",
  name: "Alex",
  level: 2,
  xp: 150,
  tokens: 75,
  walletAddress: "0x123...abc"
};

const MOCK_PATHS = [
  { id: 1, topic: "Smart Contracts Basics", status: "in_progress", progress: 0.6, createdAt: "2025-05-01" },
  { id: 2, topic: "DeFi Fundamentals", status: "completed", progress: 1.0, createdAt: "2025-04-15" }
];

const MOCK_CURRENT_TASK = {
  hasTask: true,
  taskId: 3,
  title: "Create Your First Smart Contract",
  description: "Learn how to write and deploy a basic smart contract on a test network.",
  type: "learning",
  xpReward: 50,
  tokenReward: 25,
  content: {
    lesson: "# Smart Contract Basics\n\nSmart contracts are self-executing contracts with the terms directly written into code...",
    quiz: [
      { question: "What language is commonly used for Ethereum smart contracts?", 
        options: ["JavaScript", "Python", "Solidity", "C++"],
        answer: 2 }
    ]
  }
};

const MOCK_QUESTS = [
  { id: 101, title: "Complete KYC on Binance", project: "Binance", xpReward: 100, tokenReward: 50 },
  { id: 102, title: "Create a Uniswap Liquidity Pool", project: "Uniswap", xpReward: 200, tokenReward: 100 }
];

export default function LearnEarnApp() {
  const [currentView, setCurrentView] = useState('home');
  const [user, setUser] = useState(MOCK_USER);
  const [paths, setPaths] = useState(MOCK_PATHS);
  const [currentTask, setCurrentTask] = useState(MOCK_CURRENT_TASK);
  const [quests, setQuests] = useState(MOCK_QUESTS);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [taskCompleted, setTaskCompleted] = useState(false);

  useEffect(() => {
    // This would normally fetch data from your backend
    console.log("App mounted - would fetch initial data");
  }, []);

  const submitTaskProof = () => {
    setIsSubmitting(true);
    // Simulate API call delay
    setTimeout(() => {
      setUser(prev => ({
        ...prev,
        xp: prev.xp + currentTask.xpReward,
        tokens: prev.tokens + currentTask.tokenReward
      }));
      setTaskCompleted(true);
      setIsSubmitting(false);
    }, 1500);
  };

  const startNewTask = () => {
    setTaskCompleted(false);
    // Would fetch next task
  };

  // Render different views based on current state
  const renderView = () => {
    switch(currentView) {
      case 'home':
        return (
          <div className="flex flex-col gap-6">
            <UserInfoCard user={user} />
            <CurrentTaskCard 
              task={currentTask} 
              onSubmit={submitTaskProof} 
              onStartNew={startNewTask}
              isSubmitting={isSubmitting}
              isCompleted={taskCompleted}
            />
            <NavigationButtons onNavigate={setCurrentView} />
          </div>
        );
      case 'paths':
        return (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-bold text-center">Your Learning Paths</h2>
            {paths.map(path => (
              <LearningPathCard key={path.id} path={path} />
            ))}
            <button 
              className="bg-blue-500 text-white p-3 rounded-lg font-medium"
              onClick={() => setCurrentView('home')}
            >
              Back to Home
            </button>
          </div>
        );
      case 'quests':
        return (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-bold text-center">Available Quests</h2>
            {quests.map(quest => (
              <QuestCard key={quest.id} quest={quest} />
            ))}
            <button 
              className="bg-blue-500 text-white p-3 rounded-lg font-medium"
              onClick={() => setCurrentView('home')}
            >
              Back to Home
            </button>
          </div>
        );
      case 'rewards':
        return (
          <div className="flex flex-col gap-6">
            <h2 className="text-xl font-bold text-center">Your Rewards</h2>
            <RewardsCard user={user} />
            <button 
              className="bg-blue-500 text-white p-3 rounded-lg font-medium"
              onClick={() => setCurrentView('home')}
            >
              Back to Home
            </button>
          </div>
        );
      default:
        return <div>Unknown view</div>;
    }
  };

  return (
    <div className="max-w-lg mx-auto p-4 bg-gray-50 min-h-screen">
      <header className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Learn & Earn</h1>
        {currentView !== 'home' && (
          <button onClick={() => setCurrentView('home')} className="text-blue-500">
            Home
          </button>
        )}
      </header>
      {renderView()}
    </div>
  );
}

// Component for user info display
function UserInfoCard({ user }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-blue-100 p-2 rounded-full">
            <User size={24} className="text-blue-500" />
          </div>
          <div>
            <h3 className="font-medium">{user.name}</h3>
            <p className="text-sm text-gray-500">Level {user.level}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <div className="flex items-center gap-1">
            <Zap size={16} className="text-yellow-500" />
            <span className="text-sm font-medium">{user.xp} XP</span>
          </div>
          <div className="flex items-center gap-1">
            <Gift size={16} className="text-green-500" />
            <span className="text-sm font-medium">{user.tokens} LEARN</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Component for current task
function CurrentTaskCard({ task, onSubmit, onStartNew, isSubmitting, isCompleted }) {
  if (!task.hasTask) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md text-center">
        <p>No active tasks. Start a new learning path!</p>
      </div>
    );
  }
  
  if (isCompleted) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md">
        <div className="text-center mb-4">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 mb-3">
            <Check size={24} className="text-green-500" />
          </div>
          <h3 className="text-lg font-medium">Task Completed!</h3>
        </div>
        <div className="flex justify-between mb-4 text-center">
          <div className="flex-1">
            <p className="text-sm text-gray-500">XP Earned</p>
            <p className="font-medium">{task.xpReward}</p>
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-500">Tokens Earned</p>
            <p className="font-medium">{task.tokenReward}</p>
          </div>
        </div>
        <button 
          className="w-full bg-blue-500 text-white p-3 rounded-lg font-medium"
          onClick={onStartNew}
        >
          Next Task
        </button>
      </div>
    );
  }
  
  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <div className="flex items-start gap-3 mb-4">
        <div className="bg-blue-100 p-2 rounded-full">
          <Book size={20} className="text-blue-500" />
        </div>
        <div>
          <h3 className="font-medium">{task.title}</h3>
          <p className="text-sm text-gray-500">{task.description}</p>
        </div>
      </div>
      
      <div className="border-t border-b border-gray-100 py-3 my-3">
        <div className="flex justify-between text-sm mb-2">
          <span>Rewards:</span>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1">
              <Zap size={14} className="text-yellow-500" />
              {task.xpReward} XP
            </span>
            <span className="flex items-center gap-1">
              <Gift size={14} className="text-green-500" />
              {task.tokenReward} LEARN
            </span>
          </div>
        </div>
      </div>
      
      <button 
        className={`w-full ${isSubmitting ? 'bg-gray-300' : 'bg-blue-500'} text-white p-3 rounded-lg font-medium flex justify-center items-center`}
        onClick={onSubmit}
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Verifying...' : 'Submit Proof of Completion'}
      </button>
    </div>
  );
}

// Navigation buttons
function NavigationButtons({ onNavigate }) {
  const buttons = [
    { label: 'Learning Paths', icon: <Book size={20} />, view: 'paths' },
    { label: 'Quests', icon: <Camera size={20} />, view: 'quests' },
    { label: 'Rewards', icon: <Award size={20} />, view: 'rewards' }
  ];
  
  return (
    <div className="grid grid-cols-3 gap-3">
      {buttons.map(button => (
        <button
          key={button.view}
          className="bg-white p-4 rounded-lg shadow-md flex flex-col items-center gap-2"
          onClick={() => onNavigate(button.view)}
        >
          <div className="bg-blue-50 p-2 rounded-full">
            {button.icon}
          </div>
          <span className="text-sm font-medium">{button.label}</span>
        </button>
      ))}
    </div>
  );
}

// Learning path card
function LearningPathCard({ path }) {
  const progressPercent = Math.round(path.progress * 100);
  
  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-medium">{path.topic}</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${
          path.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
        }`}>
          {path.status === 'completed' ? 'Completed' : 'In Progress'}
        </span>
      </div>
      
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span>Progress</span>
          <span>{progressPercent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full" 
            style={{ width: `${progressPercent}%` }}
          ></div>
        </div>
      </div>
      
      <button className="w-full text-blue-500 text-sm flex items-center justify-center gap-1">
        <span>Continue Learning</span>
        <ChevronRight size={16} />
      </button>
    </div>
  );
}

// Quest card
function QuestCard({ quest }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <div className="flex items-start gap-3 mb-3">
        <div className="bg-purple-100 p-2 rounded-full">
          <Camera size={20} className="text-purple-500" />
        </div>
        <div>
          <h3 className="font-medium">{quest.title}</h3>
          <p className="text-xs text-gray-500">Project: {quest.project}</p>
        </div>
      </div>
      
      <div className="border-t border-gray-100 pt-3 mt-2">
        <div className="flex justify-between text-sm">
          <span>Rewards:</span>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1">
              <Zap size={14} className="text-yellow-500" />
              {quest.xpReward} XP
            </span>
            <span className="flex items-center gap-1">
              <Gift size={14} className="text-green-500" />
              {quest.tokenReward} LEARN
            </span>
          </div>
        </div>
      </div>
      
      <button className="w-full bg-purple-500 text-white p-2 rounded-lg font-medium mt-3 text-sm">
        Start Quest
      </button>
    </div>
  );
}

// Rewards card
function RewardsCard({ user }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3">Token Balance</h3>
        <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="bg-green-100 p-2 rounded-full">
              <Gift size={20} className="text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">LEARN Tokens</p>
              <p className="font-medium text-xl">{user.tokens}</p>
            </div>
          </div>
          <button className="bg-green-500 text-white px-3 py-2 rounded-lg text-sm">
            Claim
          </button>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-medium mb-3">Connected Wallet</h3>
        <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="bg-blue-100 p-2 rounded-full">
              <Wallet size={20} className="text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Wallet Address</p>
              <p className="font-medium">{user.walletAddress}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-6">
        <h3 className="text-lg font-medium mb-3">NFT Badges</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-100 p-4 rounded-lg flex flex-col items-center">
            <div className="bg-yellow-100 p-3 rounded-full mb-2">
              <Award size={24} className="text-yellow-500" />
            </div>
            <p className="text-sm font-medium">Level 2 Badge</p>
            <p className="text-xs text-gray-500">Earned</p>
          </div>
          <div className="bg-gray-100 p-4 rounded-lg flex flex-col items-center opacity-50">
            <div className="bg-gray-200 p-3 rounded-full mb-2">
              <Award size={24} className="text-gray-400" />
            </div>
            <p className="text-sm font-medium">Level 3 Badge</p>
            <p className="text-xs text-gray-500">Locked</p>
          </div>
        </div>
      </div>
    </div>
  );
}