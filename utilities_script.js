let pyodide;
let fileContent; // Declare the global variable

async function formatText(input) {
//    console.log(input)
//    console.log("*****END of INPUT TO FORMAT TEXT")

    const result = await pyodide.runPythonAsync(`
        # print(${JSON.stringify(input)})
        result = default_typo.run_typographical_enhancement(${JSON.stringify(input)})
        result
    `);

//    console.log(result.toString())
//    console.log("*****END OF FORMATTING RESULT")

    return result.toString();
}

async function highlightDiff(old_text, new_text) {
    const diff = Diff.diffChars(old_text, new_text);
    let result = "";

    for (const part of diff) {
        if (part.added) {
            result += `<span class="highlighted">${part.value}</span>`;
        } else if (!part.removed) {
            result += part.value;
        }
    }
//    console.log(result)
    return result;
}


async function updateOutput(input, output, isScrolling) {
    // in case of invisible html symbols
    if (input.textContent.trim() === '') {
        input.innerHTML = '';
        output.innerHTML = '';
        return
    }
    const inputText = input.innerText;
    // console.log(input.innerText)
    // console.log("****END OF InnerTEXT before updating**")

    try {
        const formattedText = await formatText(inputText);
        let highlightedText = await highlightDiff(inputText, formattedText)
        // highlightedText = highlightedText.replace(/\n/g, '<br>');

        // console.log(highlightedText)
        // console.log("********END of HIGHLIGHTING****")

        output.innerHTML = highlightedText;
        // console.log(output.innerHTML)
        // console.log("********END of INNER HTML****")


        synchronizeScroll(input, output, isScrolling);
    } catch (error) {
        console.error('Formatting error:', error);
        outputDiv.value = 'Error occurred during formatting.';
    }
}

function debounce(func, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

function synchronizeScroll(primary, secondary, isScrolling) {
    if (!isScrolling) {
        requestAnimationFrame(() => {
            const percentage = primary.scrollTop / (primary.scrollHeight - primary.clientHeight);
            secondary.scrollTop = percentage * (secondary.scrollHeight - secondary.clientHeight);
            secondary.scrollLeft = primary.scrollLeft;
            isScrolling = false;
        });
        isScrolling = true;
    }
}

function handleFocus(event) {
  const obj = event.target;
  if (obj.textContent.trim() === '') {
    obj.innerHTML = '';
  }
  // Add focus-specific behavior here
}


function handleBlur(event) {
  const obj = event.target;
  if (obj.textContent.trim() === '') {
    obj.innerHTML = '';
  }
  // Add blur-specific behavior here
}


function handleCopy(e){
    // for copyButton we have separate event listener
    if (e.target.id !== 'copyButton') {
        const selection = window.getSelection();
        const text = selection.toString().replace('&nbsp;', '\u00A0');
        e.clipboardData.setData('text/plain', text);
        e.preventDefault();
    }
}


function handlePaste(e) {
    // Prevent the default paste behavior
    e.preventDefault();

    // Get plain text from the clipboard
    let text = (e.originalEvent || e).clipboardData.getData('text/plain');

    // Create a text node with the pasted content
    const textNode = document.createTextNode(text);

    // Get the current selection
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        // Get the first range of the selection
        const range = selection.getRangeAt(0);
        // Delete the current selection content
        range.deleteContents();
        // Insert the new text node
        range.insertNode(textNode);

        // Move the cursor to the end of the inserted text
        range.setStartAfter(textNode);
        range.setEndAfter(textNode);
        selection.removeAllRanges();
        selection.addRange(range);
    }

    // Trigger the input event to update the output
    e.target.dispatchEvent(new Event('input', { bubbles: true }));
}


async function loadPythonAndSources() {
    pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    await pyodide.runPythonAsync(`
        import micropip
        await micropip.install('regex')
    `);

    // Loading placeholders
    fetch('resources/placeholders/raw_text.txt')
      .then(response => response.text())
      .then(data => {
        document.getElementById('input').dataset.placeholder = data;
      })
      .catch(error => console.error('Error loading placeholder:', error));

    fetch('resources/placeholders/clean_text.txt')
      .then(response => response.text())
      .then(data => {
        document.getElementById('output').dataset.placeholder = data;
      })
      .catch(error => console.error('Error loading placeholder:', error));

    // File names to be loaded
    const codeFileName = 'typography_utils.py'
    const resourceFileNames = [
        'month_weekdays.txt',
        'nbsp_after_words.txt',
        'nbsp_before_words.txt',
        'nbsp_multiple_words.txt'
    ];

    // Function to load a file
    async function loadFile(filePath) {
        try {
            const response = await fetch(filePath);
            return await response.text();
        } catch (error) {
            console.error('Error loading file:', error);
            throw error;
        }
    }

    // Function to load files and write to Pyodide filesystem
    async function loadAndWriteFiles() {
        try {
            // Create the 'resources' directory in Pyodide filesystem
            pyodide.FS.createPath('.', 'resources', true, true);

            for (const fileName of resourceFileNames) {
                const filePath = `resources/${fileName}`;
                const content = await loadFile(filePath);

                // Write the file to Pyodide filesystem
                pyodide.FS.writeFile(filePath, content, { encoding: "utf8" });
                console.log(`File ${fileName} loaded and written successfully`);
            }

            const pythonCode = await loadFile(codeFileName);
            pyodide.FS.writeFile(codeFileName, pythonCode, { encoding: "utf8" });
            console.log(`File ${codeFileName} loaded and written successfully`);

            // Example: Read and print contents of a file using Python
            // await pyodide.runPythonAsync(`
            //     with open("typography_utils.py") as f:
            //         print(f.readlines())


            //     with open("resources/nbsp_after_words.txt") as f:
            //         print(f.readlines())
            // `);

        } catch (error) {
            console.error('Error in loadAndWriteFiles:', error);
        }
    }

    async function load_typograph() {
        await pyodide.runPythonAsync(`
            from typography_utils import default_typo
            #print('HELLO')
        `)
    }
    // Call the function to load and write files
    await loadAndWriteFiles();
    // Load python module
    await load_typograph()

    // Hide the loading overlay and show the main content with transitions
    const loadingOverlay = document.getElementById('loadingOverlay');
    const mainContent = document.getElementById('mainContent');

    loadingOverlay.style.opacity = '0';
    mainContent.style.opacity = '1';

    setTimeout(() => {
        loadingOverlay.style.display = 'none';
        mainContent.classList.add('fade-in');
    }, 500); // Wait for the transition to complete
}