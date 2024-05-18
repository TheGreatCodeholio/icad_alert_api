export class EmailAddressManager {
    constructor() {
        this.region = window.region;
    }

    renderSystemEmails(UIManager, emailAddressElement, system_data) {
        this.system_data = system_data;
        emailAddressElement.innerHTML = '';

        UIManager.createElement('h4',{
            className: "mt-3 mb-3",
            textContent: "Alert Email Config",
            parent: emailAddressElement
        })

        let email_data = system_data.system_emails
        let emailAddressTable = UIManager.createElement('table', {
            id: `system_${system_data.system_id}_email-table`,
            className: 'table',
            parent: emailAddressElement
        })
        let emailAddressTableHead = UIManager.createElement('thead', {parent: emailAddressTable})
        let emailAddressTableHeadRow = UIManager.createElement('tr', {parent: emailAddressTableHead})
        UIManager.createElement('th', {textContent: "Email Address", parent: emailAddressTableHeadRow})
        UIManager.createElement('th', {textContent: "Status", parent: emailAddressTableHeadRow})
        UIManager.createElement('th', {textContent: "Actions", parent: emailAddressTableHeadRow})

        const emailAddressTableBody = UIManager.createElement('tbody', {
            id: `system_${system_data.system_id}_email-table-body`,
            parent: emailAddressTable
        })

        email_data.forEach((email, index) => {
            this.appendSystemEmailRow(email, index, emailAddressTableBody, system_data);
        });

        // Main container for the form elements using a flexible layout
        const formContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center justify-content-between mb-3',
            parent: emailAddressElement
        });

        // Container for the email input
        const emailInputContainer = UIManager.createElement('div', {
            className: 'flex-grow-1 me-2', // Grow to use available space, margin on the right
            parent: formContainer
        });

        // Email input field
        const emailInput = UIManager.createElement('input', {
            id: `system_${system_data.system_id}_email-input`,
            type: 'email',
            className: 'form-control',
            attributes: {
                "placeholder": "Enter email address"
            },
            parent: emailInputContainer
        });

        // Container for the checkbox, using flexbox for alignment
        const checkBoxContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center me-2 form-check form-switch', // Margin on the right
            parent: formContainer
        });

        // Checkbox for enabling/disabling email
        const checkBoxInput = UIManager.createElement('input', {
            id: `system_${system_data.system_id}_email-checkbox`,
            type: 'checkbox',
            className: 'form-check-input mt-0 me-2', // Vertically centered
            attributes: {
                'aria-label': "Checkbox for enabling email"
            },
            parent: checkBoxContainer
        });

        // Label for the checkbox
        const checkBoxLabel = UIManager.createElement('label', {
            textContent: 'Disabled',
            className: 'form-check-label ms-2', // Margin on the left for spacing
            attributes: { 'for': `system_${system_data.system_id}_email-checkbox` },
            parent: checkBoxContainer
        });

        checkBoxInput.addEventListener('change', function() {
            checkBoxLabel.textContent = this.checked ? 'Enabled' : 'Disabled';
        });

        // Container for buttons, ensuring they are grouped and aligned to the right
        const buttonContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center',
            parent: formContainer
        });

        // Button for adding email
        const addEmailButton = UIManager.createElement('button', {
            className: 'btn btn-primary me-2', // Margin on the right
            textContent: "Add Email",
            parent: buttonContainer
        });
        addEmailButton.onclick = () => this.systemAddEmail(UIManager, emailAddressElement, system_data);

        // Button for saving changes
        const saveChangesButton = UIManager.createElement('button', {
            className: 'btn btn-success',
            textContent: "Save Changes",
            parent: buttonContainer
        });
        saveChangesButton.onclick = () => this.systemSaveEmail(UIManager, emailAddressElement, system_data);
    }
    appendSystemEmailRow(email, index, tableBody, system_data) {
        const row = tableBody.insertRow();

        // Email address cell
        const emailCell = row.insertCell(0);
        emailCell.textContent = email.email_address;

        // Toggle switch cell
        const toggleCell = row.insertCell(1);
        toggleCell.className = 'form-check form-switch'; // Bootstrap classes for switch styling

        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.className = 'form-check-input me-2'; // Bootstrap switch input class
        toggleInput.id = `toggle-email-${index}`; // Unique ID for the label
        toggleInput.checked = email.enabled;
        toggleInput.setAttribute('role', 'switch');
        toggleInput.onchange = () => {
            email.enabled = toggleInput.checked;
            toggleLabel.textContent = toggleInput.checked ? 'Enabled' : 'Disabled';
        };

        const toggleLabel = document.createElement('label');
        toggleLabel.className = 'form-check-label';
        toggleLabel.setAttribute('for', `toggle-email-${index}`);
        toggleLabel.textContent = email.enabled ? 'Enabled' : 'Disabled';

        toggleCell.appendChild(toggleInput);
        toggleCell.appendChild(toggleLabel);

        // Delete button cell
        const deleteCell = row.insertCell(2);
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => {
            const rowIndex = Array.from(tableBody.rows).indexOf(row);
            if (rowIndex > -1) {
                system_data.system_emails.splice(rowIndex, 1);
                tableBody.deleteRow(rowIndex);
            } else {
                console.error("Mismatch in row index, unable to delete.");
            }
        };
        deleteCell.appendChild(deleteButton);
    }
    systemAddEmail(UIManager, emailAddressElement, system_data) {
        const emailInput = document.getElementById(`system_${system_data.system_id}_email-input`);
        const enabledInput = document.getElementById(`system_${system_data.system_id}_email-checkbox`);
        if (emailInput.value && emailInput.value.includes('@')) {  // Simple validation for example
            const newEmail = {
                email_id: null,  // Assuming the backend assigns ID on save
                email_address: emailInput.value,
                enabled: enabledInput.checked
            };
            system_data.system_emails.push(newEmail);

            // Directly append new row to the table body instead of rerendering all emails
            const tableBody = document.getElementById(`system_${system_data.system_id}_email-table-body`);
            this.appendSystemEmailRow(newEmail, system_data.system_emails.length - 1, tableBody, system_data);

            emailInput.value = '';
            enabledInput.checked = false;
        } else {
            UIManager.showAlert('Please Enter A Valid Email', 'danger')
        }
    }
    systemSaveEmail(UIManager, emailAddressElement, system_data) {
        // Construct the URL for the save operation
        const save_url = `${UIManager.baseUrl}/admin/save_system_emails`;

        // Get the current email data from the system_data which should be updated throughout operations
        const emailData = {"system_id": system_data.system_id, "system_emails": system_data.system_emails};

        fetch(save_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailData)
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
                    UIManager.showAlert("Failed to save emails. Error: " + data.message, "danger");
                }
            })
            .catch(error => {
                console.error("Error saving emails:", error);
                // Display an error message
                UIManager.showAlert("Failed to save emails. Error: " + error.message, "danger");
            });
    }
    renderTriggerEmails(UIManager, emailAddressElement, trigger_data) {
        emailAddressElement.innerHTML = '';

        UIManager.createElement('h4',{
            className: "mt-3 mb-3",
            textContent: "Alert Email Config",
            parent: emailAddressElement
        })

        let email_data = trigger_data.trigger_emails || []
        let emailAddressTable = UIManager.createElement('table', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-table`,
            className: 'table',
            parent: emailAddressElement
        })
        let emailAddressTableHead = UIManager.createElement('thead', {parent: emailAddressTable})
        let emailAddressTableHeadRow = UIManager.createElement('tr', {parent: emailAddressTableHead})
        UIManager.createElement('th', {textContent: "Email Address", parent: emailAddressTableHeadRow})
        UIManager.createElement('th', {textContent: "Status", parent: emailAddressTableHeadRow})
        UIManager.createElement('th', {textContent: "Actions", parent: emailAddressTableHeadRow})

        const emailAddressTableBody = UIManager.createElement('tbody', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-table-body`,
            parent: emailAddressTable
        })

        email_data.forEach((email, index) => {
            this.appendTriggerEmailRow(email, index, emailAddressTableBody, trigger_data);
        });

        // Main container for the form elements using a flexible layout
        const formContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center justify-content-between mb-3',
            parent: emailAddressElement
        });

        // Container for the email input
        const emailInputContainer = UIManager.createElement('div', {
            className: 'flex-grow-1 me-2', // Grow to use available space, margin on the right
            parent: formContainer
        });

        // Email input field
        const emailInput = UIManager.createElement('input', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-input`,
            type: 'email',
            className: 'form-control',
            attributes: {
                "placeholder": "Enter email address"
            },
            parent: emailInputContainer
        });

        // Container for the checkbox, using flexbox for alignment
        const checkBoxContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center me-2 form-check form-switch', // Margin on the right
            parent: formContainer
        });

        // Checkbox for enabling/disabling email
        const checkBoxInput = UIManager.createElement('input', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-checkbox`,
            type: 'checkbox',
            className: 'form-check-input mt-0', // Vertically centered
            attributes: {
                'aria-label': "Checkbox for enabling email"
            },
            parent: checkBoxContainer
        });

        // Label for the checkbox
        const checkBoxLabel = UIManager.createElement('label', {
            textContent: 'Disabled',
            className: 'form-check-label ms-2', // Margin on the left for spacing
            attributes: { 'for': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-checkbox` },
            parent: checkBoxContainer
        });

        checkBoxInput.addEventListener('change', function() {
            checkBoxLabel.textContent = this.checked ? 'Enabled' : 'Disabled';
        });


        // Container for buttons, ensuring they are grouped and aligned to the right
        const buttonContainer = UIManager.createElement('div', {
            className: 'd-flex align-items-center',
            parent: formContainer
        });

        // Button for adding email
        const addEmailButton = UIManager.createElement('button', {
            className: 'btn btn-primary me-2', // Margin on the right
            textContent: "Add Email",
            parent: buttonContainer
        });
        addEmailButton.onclick = () => this.triggerAddEmail(UIManager, emailAddressElement, trigger_data);

        // Button for saving changes
        const saveChangesButton = UIManager.createElement('button', {
            className: 'btn btn-success',
            textContent: "Save Changes",
            parent: buttonContainer
        });
        saveChangesButton.onclick = () => this.triggerSaveEmail(UIManager, emailAddressElement, trigger_data);
    }
    appendTriggerEmailRow(email, index, tableBody, trigger_data) {
        const row = tableBody.insertRow();

        // Email address cell
        const emailCell = row.insertCell(0);
        emailCell.textContent = email.email_address;

        // Toggle switch cell
        const toggleCell = row.insertCell(1);
        toggleCell.className = 'form-check form-switch'; // Bootstrap classes for switch styling

        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.className = 'form-check-input me-2'; // Bootstrap switch input class
        toggleInput.id = `toggle-email-${index}`; // Unique ID for the label
        toggleInput.checked = email.enabled;
        toggleInput.setAttribute('role', 'switch');
        toggleInput.onchange = () => {
            email.enabled = toggleInput.checked;
            toggleLabel.textContent = toggleInput.checked ? 'Enabled' : 'Disabled';
        };

        const toggleLabel = document.createElement('label');
        toggleLabel.className = 'form-check-label';
        toggleLabel.setAttribute('for', `toggle-email-${index}`);
        toggleLabel.textContent = email.enabled ? 'Enabled' : 'Disabled';

        toggleCell.appendChild(toggleInput);
        toggleCell.appendChild(toggleLabel);

        // Delete button cell
        const deleteCell = row.insertCell(2);
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => {
            const rowIndex = Array.from(tableBody.rows).indexOf(row);
            if (rowIndex > -1) {
                trigger_data.trigger_emails.splice(rowIndex, 1);
                tableBody.deleteRow(rowIndex);
            } else {
                console.error("Mismatch in row index, unable to delete.");
            }
        };
        deleteCell.appendChild(deleteButton);
    }
    triggerAddEmail(UIManager, emailAddressElement, trigger_data) {
        const emailInput = document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-input`);
        const enabledInput = document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-checkbox`);
        if (emailInput.value && emailInput.value.includes('@')) {  // Simple validation for example
            const newEmail = {
                email_id: null,  // Assuming the backend assigns ID on save
                email_address: emailInput.value,
                enabled: enabledInput.checked
            };
            trigger_data.trigger_emails.push(newEmail);

            // Directly append new row to the table body instead of rerendering all emails
            const tableBody = document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-table-body`);
            this.appendSystemEmailRow(newEmail, trigger_data.trigger_emails.length - 1, tableBody, trigger_data);

            emailInput.value = '';
            enabledInput.checked = false;
        } else {
            UIManager.showAlert('Please Enter A Valid Email', 'danger')
        }
    }
    triggerSaveEmail(UIManager, emailAddressElement, trigger_data) {
        // Construct the URL for the save operation
        const save_url = `${UIManager.baseUrl}/admin/save_trigger_emails`;

        // Get the current email data from the system_data which should be updated throughout operations
        const emailData = {"system_id": trigger_data.system_id, "trigger_id": trigger_data.trigger_id, "trigger_emails": trigger_data.trigger_emails};

        console.log(emailData)

        fetch(save_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailData)
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
                    UIManager.showAlert("Failed to save emails. Error: " + data.message, "danger");
                }
            })
            .catch(error => {
                console.error("Error saving emails:", error);
                // Display an error message
                UIManager.showAlert("Failed to save emails. Error: " + error.message, "danger");
            });
    }

}