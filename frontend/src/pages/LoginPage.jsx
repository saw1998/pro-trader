// src/pages/LoginPage.jsx
import { LoginForm } from '../components/Auth/LoginForm';
import '../components/Auth/Auth.css';

export function LoginPage() {
  console.log("in login page");
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-title">📈 Trading System</h1>
          <p className="auth-subtitle">Welcome back! Please login to continue.</p>
        </div>
        <div className="card">
          <LoginForm />
        </div>
      </div>
    </div>
  );
}