document.addEventListener('DOMContentLoaded', function () {
    const notificationDropdown = document.querySelector('.dropdown-toggle');
    const notificationsList = document.getElementById('notifications-list');

    notificationDropdown.addEventListener('click', function () {
        fetch('/get-notifications/')
            .then(response => response.json())
            .then(data => {
                notificationsList.innerHTML = '';
                if (data.notifications.length > 0) {
                    data.notifications.forEach(notification => {
                        const li = document.createElement('li');
                        li.classList.add('py-2', 'px-4', 'hover:bg-gray-50');
                        li.innerHTML = `
                            <div class="text-[13px] text-gray-600 font-medium">${notification.message}</div>
                            <div class="text-[11px] text-gray-400">${notification.created_at}</div>
                        `;
                        notificationsList.appendChild(li);
                    });
                } else {
                    const li = document.createElement('li');
                    li.classList.add('py-2', 'px-4');
                    li.innerHTML = 'No notifications';
                    notificationsList.appendChild(li);
                }
            })
            .catch(error => console.error('Error fetching notifications:', error));
    });
});