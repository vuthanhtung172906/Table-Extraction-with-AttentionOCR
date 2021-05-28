import React,{Fragment, useState} from 'react'
import axios from 'axios'
const FileUpload = () => {
    const [file, setFile ] = useState("")
    const [filename, setFileName] = useState("Choose File")
    const [uploadedFile, setUploadedFile] = useState({})
    const onChange2 = (e)=>{
        setFile(e.target.files[0])
        setFileName(e.target.files[0].name)
    }
    const onSubmit = async e =>{
        e.preventDefault();
        const formData = new FormData()
        formData.append("file", file)
        const res = await axios({
                method: 'post',
                url: 'http://127.0.0.1:8000/upload',
                data: formData,
                config: { headers: { 'Content-Type': 'multipart/form-data' } }
                 })
        console.log(res)
    }

    return (
        <Fragment>
            <form action="" onSubmit={onSubmit}>
                <div className="custom-file">
                <input type="file" className="custom-file-input" id="customFile" onChange={onChange2}/>
                <label className="custom-file-label" htmlFor="customFile">{filename}</label>
                </div>
                <input type="submit" className="btn btn-primary btn-block mt-4" placeholder="Upload"/>
            </form>
        </Fragment>
    )
}
export default FileUpload