import './App.css';
import { BrowserRouter as Router, Switch, Route} from 'react-router-dom';

import Home from './components/pages/Home'
import Overview from './components/pages/Overview'
import About from './components/pages/About'

import Navbar from './components/inc/Navbar'

function App() {
  return (
    <Router>
      <Navbar />
      <Switch>
        <Route path="/" component={Home} exact={true}/>
        <Route path="/overview" component={Overview} />
        <Route path="/about" component={About} />
      </Switch>
    </Router>
  );
}

export default App;
