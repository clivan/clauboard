fetch("http://localhost:8000/")
    .then(response => response.json())
    .then(data => {

        document.getElementById("status").innerHTML =
            `<h3>${data.name}</h3>
             <p>${data.status}</p>`;

    });