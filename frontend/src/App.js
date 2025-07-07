import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Layout from './components/Layout';
import Companies from './pages/Companies';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import CompanyStats from './pages/CompanyStats';
import UserSettings from './pages/UserSettings';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <BrowserRouter>
      <ToastContainer position="top-right" autoClose={3500} hideProgressBar={false} newestOnTop closeOnClick pauseOnFocusLoss draggable pauseOnHover />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Layout />}>
          <Route path="/companies" element={<Companies />} />
          <Route path="/companies/:companyId/stats" element={<CompanyStats />} />
          <Route path="/statistics" element={<Dashboard />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/user-settings" element={<UserSettings />} />
          <Route index element={<Companies />} />
        </Route>
        <Route path="*" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
