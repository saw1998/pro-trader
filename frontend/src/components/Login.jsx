import { useState } from "react";
import { useLogin } from "../hooks/useAuthQueries";
import {useNavigate, Link} from 'react-router-dom'

export default function Login(){
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const login = useLogin();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try{
      await login.mutateAsync({ email, password });
      navigate('/dashboard');
    } catch (err) {
      //error handled by mutation state
    }
  }

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Login</h2>
        {login.isError && (
          <div className="error">
            {login.error?.response?.data?.detail || 'Login failed'}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button disabled={login.isPending}>
          {login.isPending ? 'Loading...' : 'Login'}
        </button>
        <p>
          No account? <Link to="/signup">Signup</Link>
        </p>
      </form>
    </div>
  );
}
