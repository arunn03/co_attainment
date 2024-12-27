import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js/auto";
// import "chart.js/auto";

import client, { refreshToken } from "../api";
import { ACCESS_TOKEN } from "../constant";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Home = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [co, setCO] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const getCourseOutcomes = async () => {
      try {
        const response = await client.get("/co/list/");
        if (response.status === 200) {
          setCO(response.data);
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

      getCourseOutcomes();
    }
  }, []);

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
      <h1 className="text-uppercase mb-4">Dashboard</h1>
      <div className="row">
        {co &&
          co.map((course_outcome) => {
            const values = Object.values(course_outcome.course_outcomes).filter(
              (obj) => obj.total
            );
            const keys = Object.keys(course_outcome.course_outcomes).slice(
              0,
              values.length
            );
            const sample_answer_sheet = course_outcome.answer_sheets[0];
            const data = {
              labels: keys,
              datasets: [
                {
                  label: `${sample_answer_sheet.subject.sub_code} - ${sample_answer_sheet.exam_type} - Year ${sample_answer_sheet.year} - Sem ${sample_answer_sheet.semester}`,
                  data: values.map((obj) => (obj.attained / obj.total) * 100),
                  backgroundColor: [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(255, 159, 64, 0.2)",
                    "rgba(255, 205, 86, 0.2)",
                    "rgba(75, 192, 192, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(153, 102, 255, 0.2)",
                    "rgba(201, 203, 207, 0.2)",
                  ].slice(0, values.length),
                  borderColor: [
                    "rgb(255, 99, 132)",
                    "rgb(255, 159, 64)",
                    "rgb(255, 205, 86)",
                    "rgb(75, 192, 192)",
                    "rgb(54, 162, 235)",
                    "rgb(153, 102, 255)",
                    "rgb(201, 203, 207)",
                  ].slice(0, values.length),
                  borderWidth: 1,
                },
              ],
            };

            const options = {
              responsive: true,
              plugins: {
                // legend: {
                //   display: false, // Hide legend
                // },
                tooltip: {
                  callbacks: {
                    label: function (tooltipItem) {
                      // Return only the value, without a label
                      return `${tooltipItem.raw.toFixed(2)}%`;
                    },
                  },
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: "Percentage (%)",
                  },
                },
                x: {
                  title: {
                    display: true,
                    text: "Course Outcomes",
                  },
                },
              },
            };
            return (
              // <div className="col-md-6">
              <Bar
                className="col-md-6"
                key={course_outcome.id}
                data={data}
                options={options}
              />
              // </div>
            );
          })}
      </div>
    </div>
  );
};

export default Home;
