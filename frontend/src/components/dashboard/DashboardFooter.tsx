import{

useEffect,

useState,

}from"react";

export default function DashboardFooter(){

const[

time,

setTime,

]=

useState(

new Date()

);

useEffect(()=>{

const id=

setInterval(()=>{

setTime(

new Date()

);

},1000);

return()=>

clearInterval(id);

},[]);

return(

<div className="text-sm text-slate-500">

Last Updated

{time.toLocaleString()}

</div>

);

}