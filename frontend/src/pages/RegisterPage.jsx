// src/pages/RegisterPage.jsx
import { RegisterForm } from '../components/Auth/RegisterForm';
import '../components/Auth/Auth.css';

export function RegisterPage() {
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-title">📈 Trading System</h1>
          <p className="auth-subtitle">Create your account to start trading.</p>
        </div>
        <div className="card">
          <RegisterForm />
        </div>
      </div>
    </div>
  );
}