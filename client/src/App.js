import './App.css';
import React from 'react'
import FileUpload from './components/FileUpload'
function App() {
  return (
    <div className="container mt-4">
      <h4 className="display-4 text-center mb-4">
        <i className="fab fa-react"></i>
        Table Extraction
      </h4>
      <FileUpload/>
    </div>
  );
}

export default App;
