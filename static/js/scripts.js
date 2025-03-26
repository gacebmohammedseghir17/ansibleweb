document.addEventListener("DOMContentLoaded", function () {
    fetchPlaybooks();
});

function fetchPlaybooks() {
    let server = document.getElementById("server-select").value;
    fetch(`/get_playbooks?server=${server}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#playbooks-table tbody');
            tableBody.innerHTML = '';
            data.playbooks.forEach(playbook => {
                let row = `<tr>
                    <td>${playbook.name}</td>
                    <td>${playbook.server}</td>
                    <td><button class="run-button" onclick="runPlaybook('${playbook.name}')">Run</button></td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => console.error('Error fetching playbooks:', error));
}

function runPlaybook(playbookName) {
    fetch('/execute_playbook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playbook: playbookName })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        alert('Error running playbook: ' + error);
    });
}

// Sidebar Highlight Active Link
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', function() {
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});
