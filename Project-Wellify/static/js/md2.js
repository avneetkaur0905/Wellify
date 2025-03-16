// Dropdown toggle for "Today" button
document.addEventListener('DOMContentLoaded', () => {
    const dropdownBtn = document.querySelector('.dropdown-btn');
    const notification = document.querySelector('.notification');

    // Simulate dropdown toggle (you can expand this for actual dropdown content)
    dropdownBtn.addEventListener('click', () => {
        alert('Dropdown toggled! Add your dropdown content here.');
    });

    // Add hover effect to metric cards
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });

    // Add click event to "View history" link
    const viewHistory = document.querySelector('.view-history');
    viewHistory.addEventListener('click', (e) => {
        e.preventDefault();
        alert('View health history details here.');
    });

    // Add click event to "Add Event" button
    const addEventBtn = document.querySelector('.add-event-btn');
    addEventBtn.addEventListener('click', () => {
        alert('Add event to calendar!');
    });

    // Add click event to "Sign Out" button
    const signOutBtn = document.querySelector('.sign-out-btn');
    signOutBtn.addEventListener('click', () => {
        alert('Signed out successfully!');
    });
});