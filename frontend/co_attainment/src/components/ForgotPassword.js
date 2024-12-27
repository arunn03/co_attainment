import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

import client, { refreshToken } from "../api";
import { ACCESS_TOKEN } from "../constant";

const ForgotPassword = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState(null);
  const [message, setMessage] = useState(null);

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
  }, []);

  if (isAuthenticated) {
    return navigate("/");
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await client.post("/auth/password-reset/", { email });
      if (response.status === 200) {
        setMessage("Password reset mail sent successfully!");
      }
    } catch (err) {
      console.error("Error:", err);
      setErrors(err.response.data);
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <div className="center-div">
        <form onSubmit={handleSubmit} className="form">
          <h2>Reset Password</h2>
          {errors &&
            errors.email &&
            errors.email.map((error) => (
              <p
                className="text-danger m-0 text-left"
                style={{ fontSize: "10px" }}
              >
                {error}
              </p>
            ))}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          {errors && errors.detail && (
            <p
              className="text-danger m-0 text-left"
              style={{ fontSize: "10px" }}
            >
              {errors.detail}
            </p>
          )}
          <button type="submit" disabled={loading}>
            {loading ? "Loading..." : "Reset"}
          </button>
          {message && (
            <p
              className="text-success m-0 text-left"
              style={{ fontSize: "10px" }}
            >
              {message}
            </p>
          )}
          <button
            className="resend-link mb-3"
            type="button"
            disabled={loading}
            onClick={() => navigate("/login")}
          >
            Go to login page
          </button>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword;
