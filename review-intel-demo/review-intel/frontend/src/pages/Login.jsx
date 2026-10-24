import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../services/auth';
import { login } from '../services/api';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  if(isAuthenticated())
    return <Navigate to='/' replace/>;

  const submit = async (e) => {
    e.preventDefault();
    try {
      const { access_token } = await login(form.username, form.password);
      sessionStorage.setItem('token', access_token);
      navigate('/', {replace: true});
    } catch {
      setError('Wrong username or password');
    }
  };

  return (
    <form className='login panel' onSubmit={submit}>
      <h2>Admin login</h2>
      <input placeholder='Username' value={form.username}
        onChange={(e) => setForm({ ...form, username: e.target.value })} />
      <input type='password' placeholder='Password' value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })} />
      {error && <p className='note'>{error}</p>}
      <button type='submit'>Sign in</button>
    </form>
  );
}
