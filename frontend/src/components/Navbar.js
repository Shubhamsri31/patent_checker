import React from 'react';
import { BoltIcon } from '@heroicons/react/24/solid';
import './Navbar.css';

const Navbar = ({ onInfoClick }) => (
    <nav className="navbar">
        <div className="navbar-logo">
            <img src="/logo.svg" alt="PatentAI Logo" className="logo-icon" />
            <span>Patent Analyser</span>
        </div>
        <button onClick={onInfoClick} className="info-button-nav">
            <i className="bi bi-info-circle"></i>
            <span>How it Works</span>
        </button>
    </nav>
);
export default Navbar;  