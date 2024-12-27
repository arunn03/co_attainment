import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

import client, { refreshToken } from "../api";
import { ACCESS_TOKEN, PRIVATE_KEY } from "../constant";

const COCompute = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [subject, setSubject] = useState(null);
  const [exam, setExam] = useState(null);
  const [dept, setDept] = useState(null);
  const [batch, setBatch] = useState(null);
  const [coMapping, setCoMapping] = useState({});
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

  if (!isAuthenticated) {
    return navigate("/login");
  }

  const pr_key = localStorage.getItem(PRIVATE_KEY);

  if (!pr_key) {
    return navigate("/private-key");
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    const body = new FormData();

    const json = {
      sub_code: subject,
      dept: dept,
      batch: batch,
      exam_type: exam,
      pr_key: pr_key,
      ...coMapping,
    };

    // Appending text fields to FormData
    for (const data of Object.entries(json)) {
      body.append(data[0], data[1]);
    }

    try {
      const response = await client.post("/co/compute/", body, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      if (response.status === 201 || response.status === 200) {
        console.log("Course outcome computed successfully");
        navigate("/");
      } else {
        console.log(response.data);
      }
    } catch (error) {
      console.error("Error:", error);
      setErrors(error);
    }
  };

  const handleCOChange = (co, data) => {
    setCoMapping((prevCoMapping) => {
      return {
        ...prevCoMapping,
        [co]: data,
      };
    });
  };

  return (
    <div className="center-div">
      <div className="container">
        <form onSubmit={handleSubmit}>
          <div className="row">
            <div className="col-md-6 col-lg-3 px-1">
              <input
                type="text"
                placeholder="Subject Code"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-3 px-1">
              <input
                type="text"
                placeholder="Exam"
                value={exam}
                onChange={(e) => setExam(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-3 px-1">
              <input
                type="text"
                placeholder="Department"
                value={dept}
                onChange={(e) => setDept(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-3 px-1">
              <input
                type="number"
                placeholder="Batch"
                value={batch}
                onChange={(e) => setBatch(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-4 px-1">
              <input
                type="text"
                placeholder="CO1 (eg: '1,2,5,11a:12')"
                onChange={(e) => handleCOChange("co1", e.target.value)}
                // value={coMapping ? coMapping['co1'] ? coMapping}
                required
              />
            </div>
            <div className="col-md-6 col-lg-4 px-1">
              <input
                type="text"
                placeholder="CO2 (eg: '1,2,5,11a:12')"
                onChange={(e) => handleCOChange("co2", e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-4 px-1">
              <input
                type="text"
                placeholder="CO3 (eg: '1,2,5,11a:12')"
                onChange={(e) => handleCOChange("co3", e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-4 px-1">
              <input
                type="text"
                placeholder="CO4 (eg: '1,2,5,11a:12')"
                onChange={(e) => handleCOChange("co4", e.target.value)}
              />
            </div>
            <div className="col-md-6 col-lg-4 px-1">
              <input
                type="text"
                placeholder="CO5 (eg: '1,2,5,11a:12')"
                onChange={(e) => handleCOChange("co5", e.target.value)}
              />
            </div>
            <div className="col-md-6 col-lg-4 px-1">
              <input
                type="text"
                placeholder="CO6 (eg: '1,2,5,11a:12')"
                onChange={(e) => handleCOChange("co6", e.target.value)}
              />
            </div>
          </div>
          {errors && errors.error && (
            <p
              className="text-danger m-0 text-left"
              style={{ fontSize: "10px" }}
            >
              {errors.error}
            </p>
          )}
          <button type="submit">Compute</button>
        </form>
      </div>
    </div>
  );
};

export default COCompute;
