import React from 'react'
import { useNavigate } from 'react-router-dom';
import { useLogout, useUser } from '../hooks/useAuthQueries';

export default function Dashboard() {
  const {data: user, isLoading} = useUser();
  const logout = useLogout();
  const navigate = useNavigate();
  
  if(isLoading) {
    return <div className="loading">Loading...</div>
  }

  const handleLogout = async (e) => {
    e.preventDefault();
    await logout.mutateAsync();
    navigate('/login');
  }

  return (
    <div className='dashboard'>
      <h1>Dashboard</h1>
      <div className="user-info">
        <p> <strong>Email: </strong> {user?.email} </p>
      </div>
      <button onClick={handleLogout} disabled={logout.isPending}>
        {logout.isPending ? 'Logging out...' : 'Logout'}
      </button>

    </div>
  )
}
