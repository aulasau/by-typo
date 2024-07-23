loadPythonAndSources();

document.addEventListener('DOMContentLoaded', function() {
    const outputDiv = document.getElementById('output');
    const inputDiv = document.getElementById('input');

    const copyButton = document.getElementById('copyButton');
    // Store the original button HTML
    const originalButtonHTML = copyButton.innerHTML;

    let isScrolling = false;

    const toggleDetails = document.querySelector('.toggle-details');
    const detailsContent = document.querySelector('.details-content');
    const toggleIcon = document.querySelector('.toggle-icon');

    // Create a debounced version of updateOutput
    const debouncedUpdateOutput = debounce(() => {
        updateOutput(inputDiv, outputDiv).catch(error => {
            console.error('Debounced update error:', error);
        });
    }, 300);

    copyButton.addEventListener('click', function() {
        const textToCopy = outputDiv.innerText;
        navigator.clipboard.writeText(textToCopy).then(function() {
            // Visual feedback
            copyButton.innerHTML = `<img src="img/done_icon.png" alt="Copy" class="copy-icon">Скапіравана`;
            setTimeout(() => {
                // Reset to the original HTML
                copyButton.innerHTML = originalButtonHTML;
            }, 2000);
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
            // Ensure the button resets even if copying fails
            copyButton.innerHTML = originalButtonHTML;
        });
    });

    toggleDetails.addEventListener('click', () => {
        detailsContent.style.display = detailsContent.style.display === 'none' ? 'block' : 'none';
        toggleIcon.style.transform = detailsContent.style.display === 'none' ? 'rotate(0deg)' : 'rotate(180deg)';
    });


    inputDiv.addEventListener('paste', handlePaste);
    outputDiv.addEventListener('copy', handleCopy);

    inputDiv.addEventListener('input', debouncedUpdateOutput);

    // Add scroll event listeners to both textareas
    inputDiv.addEventListener('scroll', () => synchronizeScroll(inputDiv, outputDiv, isScrolling));
    outputDiv.addEventListener('scroll', () => synchronizeScroll(outputDiv, inputDiv, isScrolling));

});