import React,{Fragment, useState} from 'react'
import axios from 'axios'
import * as FileSaver from 'file-saver';
import * as XLSX from 'xlsx';
import './FileUploade.css'
const FileUpload = () => {
    const [file, setFile ] = useState("")
    const [filename, setFileName] = useState("Choose File")
    const [content, setContent] = useState("")
    const [image , setImage] = useState(null)
    const onChange2 = (e)=>{
        setFile(e.target.files[0])
        setFileName(e.target.files[0].name)
        setImage(URL.createObjectURL(e.target.files[0]))
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
        //return result after processing at the server
        const res2 = res['data']['file_name']
        const res3 = res2.join("\n")
        console.log((res3.type))
        setContent(res3)
    }
    const convertExcelFile = () =>{
        const fileType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
        const fileExtension = '.xlsx';
        const excelData = content
        const data = excelData.split("\n")
        data.shift()
        const res = []
        data.map(item => {
            let data3 = item.split(",")
            res.push({
                STT : data3[0],
                MSV : data3[1],
                HoVaTen: data3[2],
                LopSV : data3[3],
                Diem: data3[4] 
            })
        })
        console.log(res)
        const ws = XLSX.utils.json_to_sheet(res);
        const wb = { Sheets: { 'data': ws }, SheetNames: ['data'] };
        const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
        const data4 = new Blob([excelBuffer], {type: fileType});
        const fileName = filename.split('.')[0]
    
        FileSaver.saveAs(data4, fileName + fileExtension);
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
            <div className="container">
                <div className="row">
                    <div className="col">
                     <img className="context__image" id="target" src={image} alt=""/>
                    </div>
                    <div className="col">
                     <textarea value={content} className="content__textbox"/>
                    </div>
                </div>
            </div>
            <button onClick = {convertExcelFile}>Export Excel</button>
        </Fragment>
    )
}
export default FileUpload