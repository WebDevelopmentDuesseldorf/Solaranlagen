import './App.css';
import { BrowserRouter as Router, Switch, Route} from 'react-router-dom';
import PrivateRoute from './components/PrivateRoute'

import Home from './components/pages/Home'
import Overview from './components/pages/Overview'
import About from './components/pages/About'
import Contact from './components/pages/Contact'
import LogIn from './components/pages/LogIn'
import Dashboard from './components/pages/Dashboard'

import Navbar from './components/inc/Navbar'

import { AuthProvider } from "./components/contexts/AuthContext"



function App() {
  return (
    <Router>
    <AuthProvider>
      <Navbar />
      
      <Switch>
      <PrivateRoute exact path="/" component={Dashboard} />
        <Route path="/home" component={Home} exact={true}/>
        <Route path="/overview" component={Overview} />
        <Route path="/about" component={About} />
        <Route path="/contact" component={Contact} />
        <Route path="/login" component={LogIn} />
      </Switch>
      </AuthProvider>
    </Router>
  );
}

export default App;
