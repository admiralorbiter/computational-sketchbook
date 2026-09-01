import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import NetworkGraph from './components/NetworkGraph';
import Timeline from './components/Timeline';
import EntityNetwork from './components/EntityNetwork';
import ArticleExplorer from './components/ArticleExplorer';
import Sequences from './components/Sequences';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <h1 className="nav-title">News Dashboard</h1>
            <ul className="nav-links">
              <li><Link to="/">Dashboard</Link></li>
              <li><Link to="/network">Network</Link></li>
              <li><Link to="/timeline">Timeline</Link></li>
              <li><Link to="/sequences">Sequences</Link></li>
              <li><Link to="/entities">Entities</Link></li>
              <li><Link to="/articles">Articles</Link></li>
            </ul>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/network" element={<NetworkGraph />} />
            <Route path="/timeline" element={<Timeline />} />
            <Route path="/sequences" element={<Sequences />} />
            <Route path="/entities" element={<EntityNetwork />} />
            <Route path="/articles" element={<ArticleExplorer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
