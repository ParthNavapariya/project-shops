/**
 * ReWear AI: Rental Booking & Date Math Engine
 */

function setupRentalCalculator(dailyRate, securityDeposit, shippingFee = 4.99) {
    const startInput = document.getElementById('rental_start_date');
    const endInput = document.getElementById('rental_end_date');
    const daysDisplay = document.getElementById('calc_total_days');
    const subtotalDisplay = document.getElementById('calc_subtotal');
    const depositDisplay = document.getElementById('calc_deposit');
    const totalDisplay = document.getElementById('calc_total');

    if (!startInput || !endInput) return;

    // Set minimum start date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];
    startInput.min = tomorrowStr;
    if (!startInput.value) startInput.value = tomorrowStr;

    // Default end date 3 days later
    const defaultEnd = new Date(tomorrow);
    defaultEnd.setDate(defaultEnd.getDate() + 3);
    const endStr = defaultEnd.toISOString().split('T')[0];
    endInput.min = tomorrowStr;
    if (!endInput.value) endInput.value = endStr;

    function recalculate() {
        const d1 = new Date(startInput.value);
        const d2 = new Date(endInput.value);

        if (d2 <= d1) {
            d2.setDate(d1.getDate() + 1);
            endInput.value = d2.toISOString().split('T')[0];
        }

        const diffTime = Math.abs(d2 - d1);
        const days = Math.max(1, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
        const subtotal = days * dailyRate;
        const grandTotal = subtotal + securityDeposit + shippingFee;

        if (daysDisplay) daysDisplay.textContent = `${days} day${days > 1 ? 's' : ''}`;
        if (subtotalDisplay) subtotalDisplay.textContent = `$${subtotal.toFixed(2)}`;
        if (depositDisplay) depositDisplay.textContent = `$${securityDeposit.toFixed(2)}`;
        if (totalDisplay) totalDisplay.textContent = `$${grandTotal.toFixed(2)}`;
    }

    startInput.addEventListener('change', () => {
        endInput.min = startInput.value;
        recalculate();
    });
    endInput.addEventListener('change', recalculate);

    recalculate();
}
