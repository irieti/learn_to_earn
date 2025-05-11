import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import TaskView from './pages/TaskView';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/task/:id" element={<TaskView />} />
      </Routes>
    </BrowserRouter>
  );
}