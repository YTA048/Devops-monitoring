import { useEffect,useState } from 'react';
import axios from 'axios';

export default function Dashboard(){

  const [data,setData]=useState([]);

  useEffect(()=>{
    const token = localStorage.getItem('auth');

    axios.get('http://localhost:8080/monitor',{
      headers:{ Authorization: 'Basic ' + token }
    })
    .then(res => setData(res.data.services))
    .catch(err => console.log(err));
  },[]);

  return (
    <div style={{color:'white',padding:20}}>
      <h1>?? Dashboard</h1>

      {data.map(s=>(
        <div key={s.url}>
          {s.url} ? {s.status} ({s.latency}s)
        </div>
      ))}

    </div>
  );
}
