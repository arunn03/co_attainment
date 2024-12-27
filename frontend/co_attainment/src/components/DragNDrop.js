// import { useRef, useState } from "react";

// import "./DragNDrop.css";

// const DragNDrop = () => {
//   const [files, setFiles] = useState(null);

//   const filesRef = useRef();

//   const handleDragOver = (e) => {
//     e.preventDefault();
//   };

//   const handleDrop = (e) => {
//     e.preventDefault();
//     setFiles(e.dataTransfer.files);
//   };

//   return (
//     <>
//       {files ? (
//         <div className="uploads">
//           <ul>
//             {Array.from(files).map((file, idx) => (
//               <li key={idx}>{file.name}</li>
//             ))}
//           </ul>
//         </div>
//       ) : (
//         <div
//           className="dropzone"
//           onDragOver={handleDragOver}
//           onDrop={handleDrop}
//         >
//           <h1>Drag and drop files to upload</h1>
//           <h1>Or</h1>
//           <input
//             type="file"
//             multiple
//             hidden
//             onChange={(e) => setFiles(e.target.files)}
//             ref={filesRef}
//           />
//           <button>Select Files</button>
//         </div>
//       )}
//     </>
//   );
// };

// export default DragNDrop;

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

function DragNDrop({ files, setFiles }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      acceptedFiles.forEach((file) => {
        const reader = new FileReader();
        reader.onload = () => {
          const base64String = reader.result;
          setFiles((prevFiles) => [
            ...prevFiles,
            {
              file: file,
              preview: base64String,
              progress: 100, // Assuming complete for simplicity
              type: "image",
            },
          ]);
        };
        reader.readAsDataURL(file);
      });
    },
    [setFiles]
  );

  const handleDelete = (fileToRemove) => (event) => {
    event.stopPropagation();
    setFiles((currentFiles) =>
      currentFiles.filter((file) => file !== fileToRemove)
    );
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: "image/*",
  });

  const ProgressBar = ({ progress }) => (
    <div style={{ width: "100%", backgroundColor: "#ccc" }}>
      <div
        style={{
          height: "10px",
          width: `${progress}%`,
          backgroundColor: "green",
        }}
      ></div>
    </div>
  );

  return (
    <div {...getRootProps()} style={dropzoneStyle}>
      <input {...getInputProps()} />
      <div style={messageStyle(files.length)}>
        {isDragActive ? (
          <p>Drop the files here...</p>
        ) : (
          <p>Drag 'n' drop some files here, or click to select files</p>
        )}
      </div>
      <div style={thumbsContainer}>
        {files.map((file, index) => (
          <div key={index} style={thumb}>
            <div style={fileTypeIconContainer}>
              <div style={fileTypeIconStyle}>
                <i class="fa-solid fa-image"></i>
              </div>
            </div>
            <div style={thumbInner}>
              <img
                src={file.preview}
                style={img}
                alt={`Preview ${file.file.name}`}
              />
              <ProgressBar progress={file.progress} />
              <button
                type="button"
                style={deleteButton}
                onClick={handleDelete(file)}
              >
                <i className="fa-solid fa-xmark"></i>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const dropzoneStyle = {
  flex: 1,
  display: "flex",
  flexDirection: "column",
  padding: "20px",
  borderWidth: 2,
  borderRadius: 5,
  borderColor: "#fcb603",
  borderStyle: "dashed",
  backgroundColor: "#fafafa",
  color: "#bdbdbd",
  outline: "none",
  transition: "border .24s ease-in-out",
  width: "100%",
  position: "relative",
  height: "90%",
  minHeight: "300px",
  overflow: "scroll",
  scrollbarWidth: "none",
  msOverflowStyle: "none",
};

dropzoneStyle["::-webkit-scrollbar"] = {
  display: "none",
};

const messageStyle = (fileCount) => ({
  textAlign: "center",
  width: "100%",
});

const fileTypeIconContainer = {
  position: "absolute",
  width: "100%",
  height: "100%",
  zIndex: "10",
};

const fileTypeIconStyle = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  color: "white",
  fontSize: "24px",
};

const thumbsContainer = {
  display: "flex",
  flexDirection: "row",
  flexWrap: "wrap",
  marginTop: 16,
  position: "relative",
  justifyContent: "center",
};

const thumb = {
  display: "inline-flex",
  flexDirection: "column",
  borderRadius: 2,
  border: "1px solid #eaeaea",
  marginRight: 8,
  width: 102,
  height: 168,
  boxSizing: "border-box",
  position: "relative",
};

const thumbInner = {
  position: "relative",
  minWidth: 0,
  overflow: "hidden",
};

const img = {
  display: "block",
  width: "auto",
  height: "100%",
};

const deleteButton = {
  position: "absolute",
  top: 5,
  right: 5,
  width: "20px",
  height: "20px",
  backgroundColor: "rgba(63, 63, 63, 0.5)",
  border: "none",
  borderRadius: "50%",
  fontSize: "16px",
  fontWeight: "bold",
  lineHeight: "20px",
  textAlign: "center",
  cursor: "pointer",
  padding: "0",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 11,
};

export default DragNDrop;
