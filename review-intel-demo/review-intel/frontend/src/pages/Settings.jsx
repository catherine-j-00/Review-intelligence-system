import { useNavigate } from 'react-router-dom';

export default function Settings() {
  const navigate = useNavigate();
  const logout = () => { sessionStorage.removeItem('token'); navigate('/login',{replace:true}); };
  return (
    <>
      <h1>Settings</h1>
      <p className='note'>Sample data is hidden from all charts unless you pick it in the Data filter.</p>
      <button onClick={logout}>Log out</button>
    </>
  );
}
