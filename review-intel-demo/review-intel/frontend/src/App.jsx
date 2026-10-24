import { useEffect } from 'react';
import { Navigate, Route, Routes, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { isAuthenticated } from './services/auth';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Reviews from './pages/Reviews';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Brands from './pages/Brands';
import Analytics from './pages/Analytics';
import Trends from './pages/Trends';
import Assistant from './pages/Assistant';
import Settings from './pages/Settings';

const LINKS = [['/', 'Dashboard'], ['/reviews', 'Reviews'], ['/products', 'Products'], ['/brands', 'Brands'],
  ['/analytics', 'Analytics'], ['/trends', 'Trends'], ['/assistant', 'AI Assistant'],
  ['/settings', 'Settings']];

function Layout() {
  const navigate = useNavigate();

  // 1) Ask before the user leaves the app (Back out of the app, refresh, close tab).
  //    No prompt once the user is logged out, so logout and expired-session
  //    redirects are not interrupted.
  useEffect(() => {
    const onBeforeUnload = (e) => {
      if (!isAuthenticated()) return;
      e.preventDefault();
      e.returnValue = '';
    };
    window.addEventListener('beforeunload', onBeforeUnload);
    return () => window.removeEventListener('beforeunload', onBeforeUnload);
  }, []);

  // 2) If the page is restored from the browser cache after logout, leave it.
  useEffect(() => {
    const onShow = (e) => {
      if (e.persisted && !isAuthenticated()) navigate('/login', { replace: true });
    };
    window.addEventListener('pageshow', onShow);
    return () => window.removeEventListener('pageshow', onShow);
  }, [navigate]);

  if (!isAuthenticated()) return <Navigate to='/login' replace />;
  return (
    <div className='shell'>
      <nav>{LINKS.map(([to, label]) => <NavLink key={to} to={to} end={to === '/'}>{label}</NavLink>)}</nav>
      <main><Outlet /></main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path='/login' element={<Login />} />
      <Route element={<Layout />}>
        <Route path='/' element={<Dashboard />} />
        <Route path='/reviews' element={<Reviews />} />
        <Route path='/products' element={<Products />} />
        <Route path='/products/:id' element={<ProductDetail />} />
        <Route path='/brands' element={<Brands />} />
        <Route path='/analytics' element={<Analytics />} />
        <Route path='/trends' element={<Trends />} />
        <Route path='/assistant' element={<Assistant />} />
        <Route path='/settings' element={<Settings />} />
      </Route>
    </Routes>
  );
}
