const connections = document.getElementById("connections");
const cpu = document.getElementById("cpu");
const ram = document.getElementById("ram");
const workers = document.getElementById("workers");

const form = document.querySelector("#getBalanceForm");

form.addEventListener("submit", function(e) {
    e.preventDefault();
    const address = form.querySelector("#address").value;
    const url = `/api/getBalance?address=${address}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const balance = data.result;
            document.querySelector("#balance").innerHTML = balance;
        });
});
/*
function fetch_statistics() {
    fetch("/statistics")
        .then(response => response.json())
        .then(data => {
            connections.innerHTML = data["connections"];
            cpu.innerHTML = data["cpu"].toFixed(2) + "%";
            ram.innerHTML = data["ram"].toFixed(2) + "%";
        });
}

fetch_statistics();
setInterval(() => {
    // run every 5s
    fetch_statistics(); 
}, 5000);
*/