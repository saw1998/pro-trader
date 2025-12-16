import logo from './logo.svg';
import './App.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Route, Navigate, Routes } from 'react-router-dom';
import { getToken } from './services/api';
import Login from './components/Login'
import Signup from './components/Signup';
import Dashboard from './components/Dashboard';
import { useUser } from './hooks/useAuthQueries';

const queryClient = new QueryClient({
    defaultOptions:{
        queries: {retry: false, staleTime: 5 * 60 * 1000},
    },
});

function ProtectedRoute({children}){
    const {data, isLoading, isError} = useUser();

    if(isLoading) return <div className='loading'>Loading...</div>
    if(!getToken() || isError || !data){
        return <Navigate to="/login"/>
    }
    return children;
}

function AuthRoute({children}){
    const {data, isLoading} = useUser();

    if(isLoading && getToken()){
        return <div className="loading">Loading...</div>
    }

    if(data){
        return <Navigate to="/dashboard"/>
    }

    return children;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
        <BrowserRouter>
            <Routes>
                <Route path='/login' element={<AuthRoute> <Login/> </AuthRoute>} />
                <Route path='/signup' element={<AuthRoute> <Signup/> </AuthRoute>} />
                <Route path='/dashboard' element={<ProtectedRoute> <Dashboard/> </ProtectedRoute>} />
                <Route path='*' element={<Navigate to="/dashboard"/>} />
            </Routes>
        </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
