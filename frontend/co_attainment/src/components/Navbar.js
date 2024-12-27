import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light fixed-top">
      <div className="container">
        <Link className="navbar-brand" to="/">
          CO Attainment
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav">
            <li className={`nav-item ${isActive("/") ? "active" : ""}`}>
              <Link className="nav-link" to="/">
                Home
              </Link>
            </li>
            <li
              className={`nav-item ${isActive("/private-key") ? "active" : ""}`}
            >
              <Link className="nav-link" to="/private-key">
                Private Key
              </Link>
            </li>
            <li
              className={`nav-item ${
                isActive("/answer-sheets") ? "active" : ""
              }`}
            >
              <Link className="nav-link" to="/answer-sheets">
                Answer Sheets Upload
              </Link>
            </li>
            <li
              className={`nav-item ${
                isActive("/answer-sheets/view") ? "active" : ""
              }`}
            >
              <Link className="nav-link" to="/answer-sheets/view">
                View Answer Sheets
              </Link>
            </li>
            <li
              className={`nav-item ${isActive("/co/compute") ? "active" : ""}`}
            >
              <Link className="nav-link" to="/co/compute">
                Compute CO
              </Link>
            </li>
            <li className={`nav-item ${isActive("/logs") ? "active" : ""}`}>
              <Link className="nav-link" to="/logs">
                Logs
              </Link>
            </li>
            <li className={`nav-item ${isActive("/logout") ? "active" : ""}`}>
              <Link className="nav-link" to="/logout">
                Logout
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
