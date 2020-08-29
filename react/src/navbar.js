// /src/navbar.js

import React from 'react';
import { Link } from 'react-router-dom';
// import logo from './logo.svg';

const Navbar = () => {
  return (
    <ul className="navbar-nav">
      <li className="nav-item">
        <Link className="nav-link" to="/">
          Dashboard
        </Link>
      </li>
    </ul>
  );
};

export { Navbar };
