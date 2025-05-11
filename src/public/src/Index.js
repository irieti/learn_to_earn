import ReactDOM from 'react-dom';
import App from './App';

// Init Telegram WebApp
window.Telegram = window.Telegram || {};
window.Telegram.WebApp ||= {
  expand: () => console.log('Expanded'),
  showPopup: (_, cb) => cb('start') // Mock for dev
};

ReactDOM.render(<App />, document.getElementById('root'));