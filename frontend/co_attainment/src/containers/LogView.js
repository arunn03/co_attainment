import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import {
  VerticalTimeline,
  VerticalTimelineElement,
} from "react-vertical-timeline-component";
import "react-vertical-timeline-component/style.min.css";

import client, { refreshToken } from "../api";
import { ACCESS_TOKEN } from "../constant";

const LogView = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [logs, setLogs] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const getLogs = async () => {
      try {
        const response = await client.get("/logs/");
        if (response.status === 200) {
          setLogs(response.data);
        } else {
          console.log(response.data);
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

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

      getLogs();
    }
  }, []);

  if (!isAuthenticated) {
    return navigate("/login");
  }

  const formatter = new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <div
      className="container"
      style={{
        marginTop: "100px",
      }}
    >
      {logs && (
        <VerticalTimeline lineColor="#d4d4d4">
          {logs.map((log) => {
            let background;
            if (log.activity_type === "created") background = "#4ea43d";
            else if (log.activity_type === "updated") background = "#fad496";
            else background = "#be4747";
            return (
              <VerticalTimelineElement
                key={log.id}
                iconStyle={{ background: background, color: "#fff" }}
                contentStyle={{
                  borderTop: `5px solid ${background}`,
                }}
                date={formatter.format(new Date(log.timestamp))}
              >
                <h2>
                  {log.answer_sheet.student.roll}
                  <span className="ml-2 text-secondary h6 font-italic">
                    {log.answer_sheet.student.name},{" "}
                    {log.answer_sheet.student.dept.alias}
                  </span>
                </h2>
                <h6>
                  {log.answer_sheet.subject.name}, {log.answer_sheet.exam_type}
                </h6>
                <h6 className="text-secondary">
                  {log.activity_type} by{" "}
                  <span className="font-weight-bold font-italic">
                    {log.staff.user.first_name} {log.staff.user.last_name},{" "}
                    {log.staff.dept.alias}
                  </span>
                </h6>
              </VerticalTimelineElement>
            );
          })}
        </VerticalTimeline>
      )}
    </div>
  );
};

export default LogView;
