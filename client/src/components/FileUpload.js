import React,{Fragment, useState} from 'react'
import axios from 'axios'
import * as FileSaver from 'file-saver';
import * as XLSX from 'xlsx';
import './FileUploade.css'
const FileUpload = () => {
    const [file, setFile ] = useState("")
    const [filename, setFileName] = useState("Choose File")
    const [content, setContent] = useState("")
    const [header, setHeader] = useState('')
    const [sheets, setSheets] = useState('')
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
        if (formData.get('file').name.split('.')[1] === 'pdf'){
            const sheetsRes = res['data']['sheets']
            setSheets(sheetsRes)
        }else{
            const res2 = res['data']['file_name']
            const res3 = res2.join("\n")
            const header = res['data']['header_data']
            setContent(res3)
            setHeader(header)
        }
                 

    }
    const convertExcelFile = () =>{
        const fileType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
        const fileExtension = '.xlsx';
        if (filename.split('.')[1]==='pdf'){
            console.log(sheets)
            let i = 0
            const wb = XLSX.utils.book_new();
            for (let sheet of sheets){
                const excelData = sheet[0]
                excelData.shift()
                const headerData = sheet[1]
        
                const res = []
                excelData.map(item => {
                    res.push({
                        STT : item[0],
                        MSV : item[1],
                        HoVaTen: item[2],
                        LopSV : item[3],
                        Diem: item[4] 
                    })
                    return res
                })
                const ws = XLSX.utils.json_to_sheet(res,{origin: "A2"});
                console.log(headerData)
                if(headerData.length !== 0){
                    headerData[1] = headerData[1][0] + '/' + headerData[1][2]
                }
                XLSX.utils.sheet_add_aoa(ws,[headerData] ,{origin: 'A1'})
                i = i +1
                XLSX.utils.book_append_sheet(wb, ws, "sheet"+i)
            }
            const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
            const data4 = new Blob([excelBuffer], {type: fileType});
            const fileName = filename.split('.')[0]
            FileSaver.saveAs(data4, fileName + fileExtension);
            
        }else{
            const fileType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
            const fileExtension = '.xlsx';
            const excelData = content
            const headerData = header
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
                return res
            })
            console.log(res)
            const ws = XLSX.utils.json_to_sheet(res,{origin: "A2"});
            if (headerData.length !==0){
                headerData[1] = headerData[1][0] + '/' + headerData[1][2]
            }
            XLSX.utils.sheet_add_aoa(ws,[headerData] ,{origin: 'A1'})
            const wb = { Sheets: { 'data': ws }, SheetNames: ['data'] };
            // XLSX.utils.book_append_sheet(wb, ws, "sheet2")
            const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
            const data4 = new Blob([excelBuffer], {type: fileType});
            const fileName = filename.split('.')[0]
        
            FileSaver.saveAs(data4, fileName + fileExtension);
        }

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