document.addEventListener("DOMContentLoaded",()=>{console.log("Luxury Stay Hotel Loaded");initializeSidebar();initializeSearch();initializeButtons();initializeAnimations();initializeCharts();initializeBookingCalculator();});

function initializeSidebar(){const links=document.querySelectorAll(".sidebar a");links.forEach(link=>{link.addEventListener("click",()=>{links.forEach(item=>item.parentElement.classList.remove("active"));link.parentElement.classList.add("active");});});}

function initializeSearch(){const search=document.querySelector(".search-box input");if(!search)return;search.addEventListener("keyup",function(){const value=this.value.toLowerCase();document.querySelectorAll("tbody tr").forEach(row=>{row.style.display=row.innerText.toLowerCase().includes(value)?"":"none";});});}

function initializeButtons(){document.querySelectorAll(".delete-btn").forEach(button=>{button.onclick=()=>{if(confirm("Delete this record?"))button.closest("tr").remove();};});document.querySelectorAll(".edit-btn").forEach(button=>{button.onclick=()=>showToast("Edit feature handled by Flask Backend.","success");});document.querySelectorAll(".view-btn").forEach(button=>{button.onclick=()=>showToast("View details feature coming soon.","success");});}

function initializeAnimations(){document.querySelectorAll(".card").forEach((card,index)=>{card.style.opacity="0";card.style.transform="translateY(20px)";setTimeout(()=>{card.style.transition=".5s";card.style.opacity="1";card.style.transform="translateY(0)";},index*120);});}

function initializeCharts(){if(typeof Chart==="undefined")return;const revenueCanvas=document.getElementById("revenueChart");if(revenueCanvas){new Chart(revenueCanvas,{type:"line",data:{labels:["Jan","Feb","Mar","Apr","May","Jun"],datasets:[{label:"Revenue",data:[12000,18000,22000,26000,31000,37000],borderColor:"#D4AF37",backgroundColor:"rgba(212,175,55,.2)",fill:true,tension:.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true}}}});}const roomCanvas=document.getElementById("roomChart");if(roomCanvas){new Chart(roomCanvas,{type:"doughnut",data:{labels:["Available","Booked","Maintenance"],datasets:[{data:[40,75,5],backgroundColor:["#22c55e","#ef4444","#f59e0b"]}]},options:{responsive:true,maintainAspectRatio:false}});}}

function initializeBookingCalculator(){const selects=document.querySelectorAll("select");if(selects.length<2)return;const room=selects[1];const amount=document.querySelector("input[readonly]");if(!amount)return;const prices={"Single Room":45,"Double Room":75,"Luxury Suite":150,"Deluxe Room":95};room.addEventListener("change",()=>{amount.value="$"+(prices[room.value]||0);});}

function showToast(message,type="success"){const toast=document.createElement("div");toast.className="toast";toast.innerHTML=`<i class="fa-solid ${type==="success"?"fa-circle-check":"fa-circle-exclamation"}"></i> ${message}`;toast.style.cssText="position:fixed;top:20px;right:20px;padding:15px 20px;background:"+(type==="success"?"#22c55e":"#ef4444")+";color:#fff;border-radius:10px;z-index:9999;box-shadow:0 10px 25px rgba(0,0,0,.2);font-weight:600;";document.body.appendChild(toast);setTimeout(()=>{toast.style.opacity="0";setTimeout(()=>toast.remove(),300);},3000);}
const guestForm=document.querySelector(".form-card form");
if(guestForm){
guestForm.addEventListener("submit",function(e){
e.preventDefault();
const inputs=this.querySelectorAll("input");
if(inputs.length<3)return;
const name=inputs[0].value.trim();
const email=inputs[1].value.trim();
const phone=inputs[2].value.trim();
if(name===""||email===""||phone===""){showToast("Please fill all required fields.","error");return;}
const tbody=document.querySelector("tbody");
if(!tbody)return;
const row=document.createElement("tr");
row.innerHTML=`<td>${tbody.rows.length+1}</td><td>${name}</td><td>${email}</td><td>${phone}</td><td><button type="button" class="view-btn"><i class="fa-solid fa-eye"></i></button><button type="button" class="edit-btn"><i class="fa-solid fa-pen"></i></button><button type="button" class="delete-btn"><i class="fa-solid fa-trash"></i></button></td>`;
tbody.appendChild(row);
localStorage.setItem("guestTable",tbody.innerHTML);
this.reset();
initializeButtons();
showToast("Guest added successfully!");
});
}

const guestTable=document.querySelector("tbody");
if(guestTable&&localStorage.getItem("guestTable")){
guestTable.innerHTML=localStorage.getItem("guestTable");
initializeButtons();
}

const exportButton=document.querySelector(".table-header button");
if(exportButton){
exportButton.addEventListener("click",exportTable);
}

function exportTable(){
const rows=document.querySelectorAll("table tr");
let csv=[];
rows.forEach(row=>{
let cols=row.querySelectorAll("th,td");
let data=[];
cols.forEach(col=>data.push('"'+col.innerText.replace(/\n/g," ").replace(/"/g,'""')+'"'));
csv.push(data.join(","));
});
const blob=new Blob([csv.join("\n")],{type:"text/csv;charset=utf-8;"});
const url=URL.createObjectURL(blob);
const a=document.createElement("a");
a.href=url;
a.download="hotel_report.csv";
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
URL.revokeObjectURL(url);
showToast("CSV exported successfully!");
}

const bell=document.querySelector(".fa-bell");
if(bell){
bell.addEventListener("click",()=>{showToast("No new notifications.");});
}

const darkButton=document.createElement("button");
darkButton.innerHTML='<i class="fa-solid fa-moon"></i>';
darkButton.className="dark-mode-toggle";
darkButton.style.cssText="position:fixed;bottom:20px;right:20px;width:55px;height:55px;border:none;border-radius:50%;background:#0f172a;color:#fff;font-size:20px;cursor:pointer;z-index:9999;box-shadow:0 8px 20px rgba(0,0,0,.3);";
document.body.appendChild(darkButton);

if(localStorage.getItem("darkMode")==="true"){
document.body.classList.add("dark-mode");
darkButton.innerHTML='<i class="fa-solid fa-sun"></i>';
}

darkButton.addEventListener("click",()=>{
document.body.classList.toggle("dark-mode");
const enabled=document.body.classList.contains("dark-mode");
localStorage.setItem("darkMode",enabled);
darkButton.innerHTML=enabled?'<i class="fa-solid fa-sun"></i>':'<i class="fa-solid fa-moon"></i>';
});

window.addEventListener("load",()=>{
document.body.style.opacity="0";
setTimeout(()=>{
document.body.style.transition="opacity .4s";
document.body.style.opacity="1";
},100);
});
document.querySelectorAll(".room-content button").forEach(button=>{if(button.disabled)return;button.addEventListener("click",function(){if(confirm("Do you want to book this room?")){this.innerHTML="Booked";this.disabled=true;const badge=this.parentElement.querySelector(".available");if(badge){badge.classList.remove("available");badge.classList.add("booked");badge.innerHTML="Booked";}showToast("Room booked successfully!");updateDashboardStats();}});});

document.querySelectorAll(".pending").forEach(status=>{status.addEventListener("click",function(){this.classList.remove("pending");this.classList.add("confirmed");this.innerHTML="Paid";showToast("Payment received successfully!");});});

function updateDashboardStats(){const cards=document.querySelectorAll(".card h2");if(cards.length<4)return;let booked=parseInt(cards[2].innerText.replace(/\D/g,""));if(!isNaN(booked))cards[2].innerText=booked+1;}

document.addEventListener("keydown",function(e){if(e.ctrlKey&&e.key.toLowerCase()==="f"){e.preventDefault();const search=document.querySelector(".search-box input");if(search){search.focus();showToast("Search Activated");}}});

setTimeout(()=>{if(!sessionStorage.getItem("welcomeShown")){showToast("Welcome to Luxury Stay Hotel!");sessionStorage.setItem("welcomeShown","true");}},800);

document.querySelectorAll("button").forEach(button=>{button.addEventListener("click",function(e){const ripple=document.createElement("span");ripple.className="ripple";const rect=this.getBoundingClientRect();ripple.style.left=e.clientX-rect.left+"px";ripple.style.top=e.clientY-rect.top+"px";this.appendChild(ripple);setTimeout(()=>ripple.remove(),600);});});

const today=document.getElementById("todayDate");
if(today){
today.textContent=new Date().toLocaleDateString("en-US",{weekday:"long",year:"numeric",month:"long",day:"numeric"});
}

const clock=document.getElementById("liveClock");
if(clock){
const updateClock=()=>{clock.textContent=new Date().toLocaleTimeString("en-US");};
updateClock();
setInterval(updateClock,1000);
}

document.querySelectorAll(".modal").forEach(modal=>{modal.addEventListener("click",function(e){if(e.target===this)this.style.display="none";});});

const logout=document.querySelector('a[href*="logout"]');
if(logout){
logout.addEventListener("click",()=>{localStorage.removeItem("loggedIn");sessionStorage.clear();showToast("Logged Out Successfully");});
}

window.addEventListener("online",()=>showToast("Internet Connected"));
window.addEventListener("offline",()=>showToast("Internet Disconnected","error"));

document.querySelectorAll("table tbody tr").forEach(row=>{row.addEventListener("mouseenter",()=>row.style.transition=".2s");});

document.querySelectorAll("form").forEach(form=>{form.addEventListener("submit",()=>{const btn=form.querySelector('button[type="submit"],input[type="submit"]');if(btn){btn.disabled=true;btn.innerHTML='<i class="fa-solid fa-spinner fa-spin"></i> Processing...';}});});

console.log("%cLuxury Stay Hotel Management System Loaded Successfully","color:#16a34a;font-size:16px;font-weight:bold;");