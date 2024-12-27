// import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Login from "./components/Login";
import Home from "./containers/Home";
import PrivateRoute from "./components/PrivateRoute";
import ForgotPassword from "./components/ForgotPassword";
import PrivateKey from "./components/PrivateKey";
import AnswerSheetUpload from "./containers/AnswerSheetUpload";
import AnswerSheetView from "./containers/AnswerSheetView";
import COCompute from "./containers/COCompute";
import LogView from "./containers/LogView";
import Navbar from "./components/Navbar";

function Logout() {
  localStorage.clear();
  return <Navigate to="/login" />;
}

const App = () => {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Home />
              </PrivateRoute>
            }
          />
          <Route
            path="/private-key"
            element={
              <PrivateRoute>
                <PrivateKey />
              </PrivateRoute>
            }
          />
          <Route
            path="/answer-sheets"
            element={
              <PrivateRoute>
                <AnswerSheetUpload />
              </PrivateRoute>
            }
          />
          <Route
            path="/answer-sheets/view"
            element={
              <PrivateRoute>
                <AnswerSheetView />
              </PrivateRoute>
            }
          />
          <Route
            path="/co/compute"
            element={
              <PrivateRoute>
                <COCompute />
              </PrivateRoute>
            }
          />
          <Route
            path="/logs"
            element={
              <PrivateRoute>
                <LogView />
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
