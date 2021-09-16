import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

import Header from "../components/Header"
import Home from "../components/Home"
import AreaBochum from "../components/areas/AreaBochum";
import AreaCologne from "../components/areas/AreaCologne";
import AreaDortmund from "../components/areas/AreaDortmund";
import AreaDuesseldorf from "../components/areas/AreaDuesseldorf";
import AreaDuisburg from "../components/areas/AreaDuisburg";
import AreaEssen from "../components/areas/AreaEssen";

function AppRouter() {
    return (
    <Router>
        <Header />
            <nav>
                <Switch>
                    <Route path="/" component={Home} exact={true} />
                    <Route path="/area/cologne" component={AreaCologne} /> 
                    <Route path="/area/essen" component={AreaEssen} />
                    <Route path="/area/duisburg" component={AreaDuisburg} />
                    <Route path="/area/duesseldorf" component={AreaDuesseldorf} />
                    <Route path="/area/dortmund" component={AreaDortmund} />
                    <Route path="/area/bochum" component={AreaBochum} />
                </Switch>
            </nav>
    </Router>
);

}
export default AppRouter; 