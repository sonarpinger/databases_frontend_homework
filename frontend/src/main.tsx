import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

// components are held in components folder in src folder
import LoginPage from './components/LoginPage'
import Dashboard from './components/Dashboard'
import SubmitEntry from './components/SubmitEntry'

import './output.css' // output of tailwind css render

const domNode = document.getElementById('root');
if (!domNode) {
  throw new Error('No root element found');
}
const root = createRoot(domNode);
root.render(
  <BrowserRouter>
    <Routes>
      <Route index element={<LoginPage />} />
      <Route path="/" element={<LoginPage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/submit-entry" element={<SubmitEntry />} />
    </Routes>
  </BrowserRouter>
);