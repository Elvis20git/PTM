function addMeetingSection() {
        const meetingForm = document.querySelector('.meeting-form');
        const newMeetingForm = meetingForm.cloneNode(true);
        meetingForm.parentNode.appendChild(newMeetingForm);
        newMeetingForm.removeEventListener('change', handleNoteTypeChange);
        meetingForm.parentNode.appendChild(newMeetingForm);
    }

    function saveMeetingRecord() {
        // Add your logic to save meeting records here
    }

    function addAttendee() {
        const table = document.getElementById('attendees-table');
        const row = table.insertRow();
        const cell1 = row.insertCell(0);
        const cell2 = row.insertCell(1);
        cell1.innerHTML = "<input type='text'>";
        cell2.innerHTML = "<input type='text'>";
    }

    function saveAttendees() {
        // Add your logic to save attendees here
    }

    document.getElementById('note-type').addEventListener('change', function() {
        const decisionInput = document.getElementById('decided-by');
        const assignToInput = document.getElementById('assigned-to')
        const actionDeadline = document.getElementById('action-deadline');
        if (this.value === 'action') {
            decisionInput.style.display = 'block';
            actionDeadline.style.display='block';
            assignToInput.style.display= 'block';
            // actionDeadline.style.display = 'none';
        } else {
            decisionInput.style.display = 'none';
            actionDeadline.style.display = 'none';
            assignToInput.style.display= 'none';
        }
    });