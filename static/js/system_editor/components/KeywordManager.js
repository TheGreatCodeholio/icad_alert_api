export class KeywordManager {
    constructor() {
        this.region = window.region;
    }

    renderFilterKeywords(UIManager, keywordElement, filter_data) {
        keywordElement.innerHTML = '';

        UIManager.createElement('h4',{
            className: "mt-3 mb-3",
            textContent: "Filter Keyword Config",
            parent: keywordElement
        })

        let keyword_data = filter_data.filter_keywords;
        let keywordTable = UIManager.createElement('table', {
            id: `filter_${filter_data.alert_filter_id}_keyword-table`,
            className: 'table',
            parent: keywordElement
        })

        let keywordTableHead = UIManager.createElement('thead', {parent: keywordTable})
        let keywordTableHeadRow = UIManager.createElement('tr', {parent: keywordTableHead})
        UIManager.createElement('th', {textContent: "Keyword", parent: keywordTableHeadRow})
        UIManager.createElement('th', {textContent: "Status", parent: keywordTableHeadRow})
        UIManager.createElement('th', {textContent: "Exclusion", parent: keywordTableHeadRow})
        UIManager.createElement('th', {textContent: "Actions", parent: keywordTableHeadRow})

        const keywordTableBody = UIManager.createElement('tbody', {
            id: `filter_${filter_data.alert_filter_id}_keyword-table-body`,
            parent: keywordTable
        })

        keyword_data.forEach((keyword, index) => {
            this.appendFilterKeywordRow(keyword, index, keywordTableBody, filter_data);
        });

        // Main container for the form elements using a flexible layout
        const formContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center justify-content-between mb-3',
            parent: keywordElement
        });

        // Container for the email input
        const keywordInputContainer = UIManager.createElement('div', {
            className: 'flex-grow-1 me-2', // Grow to use available space, margin on the right
            parent: formContainer
        });

        // Keyword input field
        const keywordInput = UIManager.createElement('input', {
            id: `filter_${filter_data.alert_filter_id}_keyword-input`,
            type: 'text',
            className: 'form-control',
            attributes: {
                "placeholder": "Enter keyword"
            },
            parent: keywordInputContainer
        });

        // Container for the enabled checkbox, using flexbox for alignment
        const checkBoxEnabledContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center me-2 form-check form-switch', // Margin on the right
            parent: formContainer
        });

        // Checkbox for enabling/disabling email
        const checkBoxEnabledInput = UIManager.createElement('input', {
            id: `filter_${filter_data.alert_filter_id}_keyword-enabled-checkbox`,
            type: 'checkbox',
            className: 'form-check-input mt-0 me-2', // Vertically centered
            attributes: {
                'aria-label': "Checkbox for enabling keyword"
            },
            parent: checkBoxEnabledContainer
        });

        // Label for the checkbox
        const checkBoxEnabledLabel = UIManager.createElement('label', {
            textContent: 'Disabled',
            className: 'form-check-label ms-2', // Margin on the left for spacing
            attributes: { 'for': `filter_${filter_data.alert_filter_id}_keyword-enabled-checkbox` },
            parent: checkBoxEnabledContainer
        });

        checkBoxEnabledInput.addEventListener('change', function() {
            checkBoxEnabledLabel.textContent = this.checked ? 'Enabled' : 'Disabled';
        });

        // Container for the excluded checkbox, using flexbox for alignment
        const checkBoxExcludedContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center me-2 form-check form-switch', // Margin on the right
            parent: formContainer
        });

        // Checkbox for enabling/disabling email
        const checkBoxExcludedInput = UIManager.createElement('input', {
            id: `filter_${filter_data.alert_filter_id}_keyword-excluded-checkbox`,
            type: 'checkbox',
            className: 'form-check-input mt-0 me-2', // Vertically centered
            attributes: {
                'aria-label': "Checkbox for excluding keyword"
            },
            parent: checkBoxExcludedContainer
        });

        // Label for the checkbox
        const checkBoxExcludedLabel = UIManager.createElement('label', {
            textContent: 'Included',
            className: 'form-check-label ms-2', // Margin on the left for spacing
            attributes: { 'for': `filter_${filter_data.alert_filter_id}_keyword-excluded-checkbox` },
            parent: checkBoxExcludedContainer
        });

        checkBoxExcludedInput.addEventListener('change', function() {
            checkBoxExcludedLabel.textContent = this.checked ? 'Excluded' : 'Included';
        });

        // Container for buttons
        const buttonContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center',
            parent: formContainer
        });

        // Button for adding email
        const addKeywordButton = UIManager.createElement('button', {
            className: 'btn btn-primary me-2', // Margin on the right
            textContent: "Add Keyword",
            parent: buttonContainer
        });
        addKeywordButton.onclick = () => this.AddFilterKeyword(UIManager, keywordElement, filter_data);

        // Button for saving changes
        const saveChangesButton = UIManager.createElement('button', {
            className: 'btn btn-success',
            textContent: "Save Changes",
            parent: buttonContainer
        });
        saveChangesButton.onclick = () => this.SaveFilterKeywords(UIManager, keywordElement, filter_data);
    }
    appendFilterKeywordRow(keyword, index, tableBody, filter_data) {
        const row = tableBody.insertRow();

        // Email address cell
        const keywordCell = row.insertCell(0);
        keywordCell.textContent = keyword.keyword;

        // Toggle enable switch cell
        const toggleEnableCell = row.insertCell(1);
        toggleEnableCell.className = 'form-check form-switch'; // Bootstrap classes for switch styling

        const toggleEnableInput = document.createElement('input');
        toggleEnableInput.type = 'checkbox';
        toggleEnableInput.className = 'form-check-input me-2'; // Bootstrap switch input class
        toggleEnableInput.id = `toggle-enable-keyword-${index}`; // Unique ID for the label
        toggleEnableInput.checked = keyword.enabled;
        toggleEnableInput.setAttribute('role', 'switch');
        toggleEnableInput.onchange = () => {
            keyword.enabled = toggleEnableInput.checked;
            toggleEnabledLabel.textContent = toggleEnableInput.checked ? 'Enabled' : 'Disabled';
        };

        const toggleEnabledLabel = document.createElement('label');
        toggleEnabledLabel.className = 'form-check-label';
        toggleEnabledLabel.setAttribute('for', `toggle-enable-keyword-${index}`);
        toggleEnabledLabel.textContent = keyword.enabled ? 'Enabled' : 'Disabled';

        toggleEnableCell.appendChild(toggleEnableInput);
        toggleEnableCell.appendChild(toggleEnabledLabel);

        // Toggle exclusion switch cell
        const toggleExclusionCell = row.insertCell(2);
        toggleExclusionCell.className = 'form-check form-switch'; // Bootstrap classes for switch styling

        const toggleExclusionInput = document.createElement('input');
        toggleExclusionInput.type = 'checkbox';
        toggleExclusionInput.className = 'form-check-input me-2'; // Bootstrap switch input class
        toggleExclusionInput.id = `toggle-exclusion-keyword-${index}`; // Unique ID for the label
        toggleExclusionInput.checked = keyword.is_excluded;
        toggleExclusionInput.setAttribute('role', 'switch');
        toggleExclusionInput.onchange = () => {
            keyword.is_excluded = toggleExclusionInput.checked;
            toggleExclusionLabel.textContent = toggleExclusionInput.checked ? 'Excluded' : 'Included';
        };

        const toggleExclusionLabel = document.createElement('label');
        toggleExclusionLabel.className = 'form-check-label';
        toggleExclusionLabel.setAttribute('for', `toggle-exclusion-keyword-${index}`);
        toggleExclusionLabel.textContent = keyword.is_excluded ? 'Excluded' : 'Included';

        toggleExclusionCell.appendChild(toggleExclusionInput);
        toggleExclusionCell.appendChild(toggleExclusionLabel);

        // Delete button cell
        const deleteCell = row.insertCell(3);
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => {
            const rowIndex = Array.from(tableBody.rows).indexOf(row);
            if (rowIndex > -1) {
                filter_data.filter_keywords.splice(rowIndex, 1);
                tableBody.deleteRow(rowIndex);
            } else {
                console.error("Mismatch in row index, unable to delete.");
            }
        };
        deleteCell.appendChild(deleteButton);
    }
    AddFilterKeyword(UIManager, keywordElement, filter_data) {
        const keywordInput = document.getElementById(`filter_${filter_data.alert_filter_id}_keyword-input`);
        const enabledInput = document.getElementById(`filter_${filter_data.alert_filter_id}_keyword-enabled-checkbox`);
        const excludedInput = document.getElementById(`filter_${filter_data.alert_filter_id}_keyword-excluded-checkbox`);

        if (keywordInput.value) {  // Simple validation for example
            const newKeyword = {
                keyword_id: null,  // Assuming the backend assigns ID on save
                keyword: keywordInput.value,
                is_excluded: excludedInput.checked,
                enabled: enabledInput.checked
            };
            filter_data.filter_keywords.push(newKeyword);

            // Directly append new row to the table body instead of rerendering all emails
            const tableBody = document.getElementById(`filter_${filter_data.alert_filter_id}_keyword-table-body`);
            this.appendFilterKeywordRow(newKeyword, filter_data.filter_keywords.length - 1, tableBody, filter_data);

            keywordInput.value = '';
            enabledInput.checked = false;
            excludedInput.checked = false;
        } else {
            UIManager.showAlert('Please Enter A Valid Keyword', 'danger')
        }
    }
    SaveFilterKeywords(UIManager, keywordElement, filter_data) {
        // Construct the URL for the save operation
        const save_url = `${UIManager.baseUrl}/admin/save_filter_keywords`;

        // Get the current email data from the system_data which should be updated throughout operations
        const keywordData = {"alert_filter_id": filter_data.alert_filter_id, "alert_filter_name": filter_data.alert_filter_name, "filter_keywords": filter_data.filter_keywords};

        console.log(keywordData)

        fetch(save_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(keywordData)
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to save changes');
                }
            })
            .then(data => {
                if(data.success){
                    UIManager.showAlert(data.message, "success");
                } else {
                    UIManager.showAlert("Failed to save keywords. Error: " + data.message, "danger");
                }
            })
            .catch(error => {
                console.error("Error saving emails:", error);
                // Display an error message
                UIManager.showAlert("Failed to save keywords. Error: " + error.message, "danger");
            });
    }

}