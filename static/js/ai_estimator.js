/**
 * ReWear AI: Live Machine Learning Valuation & Charting Engine
 */

let depreciationChartInstance = null;

// Estimate price from input parameters
async function requestAiEstimation(params) {
    try {
        const res = await fetch('/api/ai/estimate-price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        const json = await res.json();
        return json.success ? json.data : null;
    } catch (err) {
        console.error('AI Estimation request failed:', err);
        return null;
    }
}

// Render dynamic Depreciation Curve using Chart.js
function renderDepreciationChart(canvasId, timelineData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !window.Chart) return;

    if (depreciationChartInstance) {
        depreciationChartInstance.destroy();
    }

    const labels = timelineData.map(d => d.label);
    const resaleValues = timelineData.map(d => d.resale_value);
    const rentalRates = timelineData.map(d => d.rental_rate);

    depreciationChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Fair Resale Value ($)',
                    data: resaleValues,
                    borderColor: '#059669',
                    backgroundColor: 'rgba(5, 150, 105, 0.12)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3,
                    pointBackgroundColor: '#059669',
                    pointRadius: 4,
                    yAxisID: 'y'
                },
                {
                    label: 'Daily Rental Rate ($)',
                    data: rentalRates,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.08)',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.35,
                    borderWidth: 2,
                    pointBackgroundColor: '#2563eb',
                    pointRadius: 3,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: { family: 'Plus Jakarta Sans', weight: 600 }
                    }
                },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleFont: { family: 'Outfit', weight: 700 },
                    bodyFont: { family: 'Plus Jakarta Sans' },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return ` ${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Plus Jakarta Sans', weight: 500 } }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    ticks: {
                        callback: value => `$${value}`,
                        font: { family: 'Plus Jakarta Sans' }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: {
                        callback: value => `$${value}/d`,
                        font: { family: 'Plus Jakarta Sans' }
                    }
                }
            }
        }
    });
}
