import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

import client, { refreshToken } from "../api";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constant";

const Login = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState(null);

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
      // Send email for OTP generation
      const response = await client.post("/auth/token/", { email, password });
      if (response.status === 200) {
        localStorage.setItem(ACCESS_TOKEN, response.data.access);
        localStorage.setItem(REFRESH_TOKEN, response.data.refresh);
        navigate("/");
        // history.push('/otp');  // Redirect to OTP verification page
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
          <h2>Login</h2>
          {/* {error && <div className="error">{error}</div>} */}
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
          {errors &&
            errors.password &&
            errors.password.map((error) => (
              <p
                className="text-danger m-0 text-left"
                style={{ fontSize: "10px" }}
              >
                {error}
              </p>
            ))}
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
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
            {loading ? "Loading..." : "Login"}
          </button>
          <button
            className="resend-link my-3"
            type="button"
            disabled={loading}
            onClick={() => navigate("/forgot-password")}
          >
            Forgot password?
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
