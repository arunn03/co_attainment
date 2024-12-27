import { useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";

import DragNDrop from "../components/DragNDrop";
import client, { refreshToken } from "../api";
import { ACCESS_TOKEN, PRIVATE_KEY } from "../constant";

const AnswerSheetUpload = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [subject, setSubject] = useState(null);
  const [exam, setExam] = useState(null);
  const [year, setYear] = useState(null);
  const [semester, setSemester] = useState(null);
  const [answerSheets, setAnswerSheets] = useState([]);

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    const body = new FormData();

    const json = {
      subject: subject,
      year: year,
      semester: semester,
      exam_type: exam,
      pr_key: pr_key,
    };

    // Appending text fields to FormData
    for (const data of Object.entries(json)) {
      body.append(data[0], data[1]);
    }

    answerSheets.forEach((file, index) => {
      body.append("answer_sheets", file.file);
    });

    try {
      const response = await client.post("/answersheets/bulk-create/", body, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      if (response.status === 201) {
        console.log("Answer sheets created successfully");
        navigate("/");
      } else {
        console.log(response.data);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  if (!isAuthenticated) {
    return navigate("/login");
  }

  const pr_key = localStorage.getItem(PRIVATE_KEY);

  if (!pr_key) {
    return navigate("/private-key");
  }

  return (
    <div className="center-div">
      <div className="container">
        <form onSubmit={handleSubmit}>
          <div className="row w-100 mx-auto">
            <div className="col-md-6 col-lg-3 px-1">
              <input
                type="text"
                placeholder="Subject Code"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-3 px-2">
              <input
                type="text"
                placeholder="Exam"
                value={exam}
                onChange={(e) => setExam(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-3 px-2">
              <input
                type="number"
                placeholder="Year"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6 col-lg-3 px-2">
              <input
                type="number"
                placeholder="Semester"
                value={semester}
                onChange={(e) => setSemester(e.target.value)}
                required
              />
            </div>
          </div>
          <DragNDrop files={answerSheets} setFiles={setAnswerSheets} />
          <button type="submit">Submit</button>
        </form>
      </div>
    </div>
  );
};

export default AnswerSheetUpload;
