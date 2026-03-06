import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Layout from './components/Layout';
import Companies from './pages/Companies';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import CompanyStats from './pages/CompanyStats';
<<<<<<< HEAD
import UserSettings from './pages/UserSettings';
=======
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
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
<<<<<<< HEAD
          <Route path="/user-settings" element={<UserSettings />} />
=======
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
          <Route index element={<Companies />} />
        </Route>
        <Route path="*" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
