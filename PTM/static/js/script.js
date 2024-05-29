// script.js
// script.js
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('addTemplate').addEventListener('click', addTemplate);
    document.querySelector('.actionSelect').addEventListener('change', handleSelectChange);
});

function handleSelectChange(event) {
    const nextElement = event.target.nextElementSibling;
    if (event.target.value === 'Action' && nextElement.classList.contains('datePicker')) {
        nextElement.style.display = 'inline-block';
    } else {
        nextElement.style.display = 'none';
    }
}

function addTemplate() {
    const container = document.getElementById('templateContainer');
    const template = document.createElement('div');
    template.classList.add('template');
    template.innerHTML = `
        <textarea class="noteInput" placeholder="Enter up to 2000 words..."></textarea>
        <select class="actionSelect">
            <option value="">Please Select</option>
            <option value="Decision">Decision</option>
            <option value="Note">Note</option>
            <option value="Action">Action</option>
        </select>
        <input type="date" class="datePicker" style="display: none;">
    `;
    container.appendChild(template);

    // Add event listener to the newly added select
    template.querySelector('.actionSelect').addEventListener('change', handleSelectChange);
}

