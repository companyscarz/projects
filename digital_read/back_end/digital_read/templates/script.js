
// Path to your PDF file (ensure document.pdf exists in the same directory)
const url = 'document.pdf';

const pdfjsLib = window['pdfjs-dist/build/pdf'];
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

let pdfDoc = null,
    pageNum = 1,
    canvas = document.getElementById('pdf-canvas'),
    ctx = canvas.getContext('2d');

// Function to render the PDF page
function renderPage(num) {
    pdfDoc.getPage(num).then(page => {
        const viewport = page.getViewport({ scale: 1.5 });
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: ctx,
            viewport: viewport
        };
        page.render(renderContext);
    });
}

// Load the PDF document
pdfjsLib.getDocument(url).promise.then(pdfDoc_ => {
    pdfDoc = pdfDoc_;
    renderPage(pageNum);
}).catch(err => {
    console.error('Error loading PDF:', err);
    alert('Please ensure document.pdf exists in the same directory.');
});

// Security: Disable common keyboard shortcuts for saving, printing, and inspecting
window.addEventListener('keydown', (e) => {
    // Check for Ctrl/Cmd key
    if (e.ctrlKey || e.metaKey) {
        // Disable 's' (Save), 'p' (Print), 'u' (View Source), 'c' (Copy)
        if (e.key === 's' || e.key === 'p' || e.key === 'u' || e.key === 'c') {
            e.preventDefault();
            alert("This action is disabled for security reasons.");
        }
    }
    // Disable F12 (Developer Tools)
    if (e.keyCode === 123) {
        e.preventDefault();
        alert("Developer tools are disabled.");
    }
});

// Security: Disable right-click context menu
document.addEventListener('contextmenu', event => event.preventDefault());
