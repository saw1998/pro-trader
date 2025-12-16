import { useState } from "react";
import {Link, useNavigate} from 'react-router-dom'
import { useLogin, useRegister } from "../hooks/useAuthQueries";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const register = useRegister();
  const login = useLogin();

  const isLoading = register.isPending || login.isPending;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try{
      await register.mutateAsync({email, password});
      await login.mutateAsync({email, password});
      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail: detail?.reason || 'Registration failed');
    }
  };

  return(
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>Sign up</h2>
        {error && <div className="error">{error}</div> }

        <input
          type="email"
          placeholder="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={3}
        />
        <button disabled={isLoading}>{isLoading ? 'Loading...' : 'Signup'}</button>
        <p>
          Have account? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  );


}
