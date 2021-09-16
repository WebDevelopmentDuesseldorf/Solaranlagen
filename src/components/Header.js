import React from 'react';
import { NavLink } from "react-router-dom";

function Header() {
    return (
        <div>
            <header>
                <h1>Overview</h1>
                <NavLink to="/" exact={true} activeClassName="is-active">Home </NavLink>
                <NavLink to="/area" exact={true} activeClassName="is-active">Area </NavLink>
                <NavLink to="/area/cologne" activeClassName="is-active">Cologne </NavLink>
                <NavLink to="/area/essen" activeClassName="is-active">Essen </NavLink>
                <NavLink to="/area/duisburg" activeClassName="is-active">Duisburg </NavLink>
                <NavLink to="/area/duesseldorf" activeClassName="is-active">Duesseldorf </NavLink>
                <NavLink to="/area/dortmund" activeClassName="is-active">Dortmund </NavLink>
                <NavLink to="/area/bochum" activeClassName="is-active">Bochum </NavLink> 
            </header>
        </div>
);
}
export default Header;