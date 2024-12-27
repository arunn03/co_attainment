import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

import { refreshToken } from "../api";
import { ACCESS_TOKEN, PRIVATE_KEY } from "../constant";

const PrivateKey = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [message, setMessage] = useState(null);
  const [prKey, setPrKey] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    var token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      const decoded = jwtDecode(token);
      const expirationTime = decoded.exp;
      const now = Date.now() / 1000;

      if (now > expirationTime) {
        refreshToken();
        token = localStorage.getItem(ACCESS_TOKEN);
      }
      setIsAuthenticated(true);
    }

    var pr_key = localStorage.getItem(PRIVATE_KEY);
    if (pr_key) {
      setPrKey(pr_key);
    }
  }, []);

  if (!isAuthenticated) {
    return navigate("/login");
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem(PRIVATE_KEY, prKey);
    setMessage("Private key saved successfully!!");
  };

  const handleClear = () => {
    localStorage.removeItem(PRIVATE_KEY);
    setPrKey("");
    setMessage("Private key cleared successfully!!");
  };

  return (
    <div className="container">
      <div className="center-div">
        <form onSubmit={handleSubmit} className="form">
          <h2>Private Key Details</h2>
          {message && (
            <p
              className="text-success m-0 text-left"
              style={{ fontSize: "10px" }}
            >
              {message}
            </p>
          )}
          <textarea
            placeholder="Private Key"
            onChange={(e) => setPrKey(e.target.value)}
            rows={10}
            value={prKey}
            required
          ></textarea>
          <button type="submit">Save</button>
          <button type="button" onClick={handleClear}>
            Clear
          </button>
        </form>
      </div>
    </div>
  );
};

export default PrivateKey;
