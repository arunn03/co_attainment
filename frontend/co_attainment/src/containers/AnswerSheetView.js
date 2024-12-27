import { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";

import client, { refreshToken } from "../api";
import { ACCESS_TOKEN, PRIVATE_KEY } from "../constant";
import { decryptContent } from "../modules/decrypt";

const AnswerSheetView = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [subject, setSubject] = useState(null);
  const [exam, setExam] = useState(null);
  const [year, setYear] = useState(null);
  const [semester, setSemester] = useState(null);
  const [answerSheets, setAnswerSheets] = useState(null);

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

  useEffect(() => {
    const fetchAnswerSheets = async () => {
      const pr_key = localStorage.getItem(PRIVATE_KEY);

      if (!pr_key) {
        return navigate("/private-key");
      }

      const body = new FormData();

      body.append("pr_key", pr_key);

      try {
        const response = await client.post("/answersheets/decrypt/", body, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        if (response.status === 200) {
          setAnswerSheets(response.data);
        } else {
          console.log(response.data);
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    fetchAnswerSheets();
  }, []);

  useEffect(() => {
    setAnswerSheets((prevAnswerSheets) =>
      prevAnswerSheets
        ? prevAnswerSheets.map((answerSheet) => {
            answerSheet.hide =
              (subject && answerSheet.subject.sub_code != subject) ||
              (exam && answerSheet.exam_type != exam) ||
              (year && answerSheet.year != year) ||
              (semester && answerSheet.semester != semester);

            return answerSheet;
          })
        : prevAnswerSheets
    );
  }, [subject, exam, year, semester]);

  if (!isAuthenticated) {
    return navigate("/login");
  }

  return (
    <div
      className="container"
      style={{
        marginTop: "100px",
      }}
    >
      <div className="row w-100 mx-auto">
        <div className="col-md-6 col-lg-3 px-1">
          <input
            type="text"
            placeholder="Subject Code"
            value={subject ? subject : ""}
            onChange={(e) =>
              setSubject(e.target.value !== "" ? e.target.value : null)
            }
            required
          />
        </div>
        <div className="col-md-6 col-lg-3 px-2">
          <input
            type="text"
            placeholder="Exam"
            value={exam ? exam : ""}
            onChange={(e) =>
              setExam(e.target.value !== "" ? e.target.value : null)
            }
            required
          />
        </div>
        <div className="col-md-6 col-lg-3 px-2">
          <input
            type="number"
            placeholder="Year"
            value={year ? year : ""}
            onChange={(e) =>
              setYear(e.target.value !== "" ? e.target.value : null)
            }
            required
          />
        </div>
        <div className="col-md-6 col-lg-3 px-2">
          <input
            type="number"
            placeholder="Semester"
            value={semester ? semester : ""}
            onChange={(e) =>
              setSemester(e.target.value !== "" ? e.target.value : null)
            }
            required
          />
        </div>
      </div>
      {answerSheets && (
        <div className="text-center">
          <span className="h1 mr-2">
            {answerSheets.filter((answerSheet) => !answerSheet.hide).length}
          </span>
          <span className="h4"> Answer sheets found</span>
        </div>
      )}
      <div className="row">
        {answerSheets &&
          answerSheets.map((answerSheet) => {
            if (answerSheet.hide) return;
            return (
              <div
                className="col-sm-12 col-md-4 col-lg-3 p-4"
                key={answerSheet.id}
              >
                <img
                  src={answerSheet.file_blob_url}
                  style={{
                    width: "100%",
                    maxHeight: "100%",
                  }}
                />
                <p className="my-2 text-center">
                  {answerSheet.student.roll} - {answerSheet.exam_type} -{" "}
                  {answerSheet.subject.sub_code}
                  <br />
                  {answerSheet.student.name}
                </p>
              </div>
            );
          })}
      </div>
    </div>
  );
};

export default AnswerSheetView;
