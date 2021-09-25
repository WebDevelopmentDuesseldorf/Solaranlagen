import React from 'react';
import { Link } from 'react-router-dom';

function Navbar(){ 
    return (
        <nav className="navbar navbar-expand-lg navbar-dark sticky-top">
            <div className="container-fluid">
                <Link className="navbar-brand" to="#">Solarpanels<span> - A Project for </span>Tech<span>labs</span></Link>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNavDropdown">
                    <ul className="navbar-nav ms-auto">
                        <li className="nav-item">
                            <Link className="nav-link active" aria-current="page" to="/home">Home</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to="/overview">Overview</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to="/about">About</Link>
                        </li>
                        <li className="nav-item dropdown">
                            <Link className="nav-link dropdown-toggle" to="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                Sign/Up Area
                            </Link>
                            <ul className="dropdown-menu dropdown" aria-labelledby="navbarDropdownMenuLink">
                                <li><Link className="dropdown-item" to="/login">Login</Link></li>
                             
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    )
}

export default Navbar