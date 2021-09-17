import React, { useState } from 'react'
import { NavLink } from "react-router-dom";
import '../styles/Navigation.scss'



const Navigation = () => {
    const [state, setState] = useState("");

    const open3dNavigation = () => {
        setState(state === "" ? "active" : "");
    }

    return (
        <div className={`container ${state}`}>
            <div className="navbar">
                <div className="menu">
                    <h3 className="logo"><span>Ein </span>Tech<span>Labs Project</span></h3>
                    <div className="hamburger-menu" onClick={open3dNavigation}>
                        <div className="bar" onClick={open3dNavigation}></div>
                    </div>
                </div>
            </div>

            <div className="main-container">
                <div className="main">
                    <header>
                        <div className="overlay">
                            <div className="inner">
                                <h2 className="title">Solaranlagen</h2>
                                <p>
                                    Lorem ipsum dolor sit amet consectetur adipisicing elit.
                                    Laudantium illum tenetur consequatur veritatis?
                                </p>
                                <button className="btn" >Weitere Informationen</button>
                            </div>
                        </div>
                    </header>
                </div>

                <div className="shadow one">
                <div className="main">
                </div>
                
                </div>
                <div className="shadow two"></div>
            </div>

            <div className="links">
                <ul>
                    <li>
                        <NavLink to="/"   exact={true} activeClassName="is-active" style={{ '--i': '0.05s' }}><span >Home </span> </NavLink>
                    </li>
                    <li>
                        <NavLink to="/area" exact={true} activeClassName="is-active" style={{ '--i': '0.1s' }}>Area </NavLink>
                    </li>
                    <li>
                        <NavLink to="/area/cologne" activeClassName="is-active" style={{ '--i': '0.15s' }}>Cologne </NavLink>
                    </li>
                    <li>
                        <NavLink to="/area/essen" activeClassName="is-active" style={{ '--i': '0.2s' }}>Essen </NavLink>
                    </li>
                    <li>
                        <NavLink to="/area/duisburg" activeClassName="is-active" style={{ '--i': '0.25s' }}>Duisburg </NavLink>
                    </li>
                    <li>
                        <NavLink to="/area/duesseldorf" activeClassName="is-active" style={{ '--i': '0.3s' }}>Duesseldorf </NavLink>
                    </li>
                    <li>
                        <NavLink to="/area/dortmund" activeClassName="is-active" style={{ '--i': '0.35s' }}>Dortmund </NavLink>
                    </li>
                    <li>
                        <NavLink to="/area/bochum" activeClassName="is-active" style={{ '--i': '0.4s' }}>Bochum </NavLink>
                    </li>
                </ul>
            </div>
        </div>


    );
}

export default Navigation;