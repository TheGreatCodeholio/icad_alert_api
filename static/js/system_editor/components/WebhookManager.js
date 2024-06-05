export class WebhookManager {
    constructor() {
        this.region = window.region;
    }

    debounce(func, timeout = 1000) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                func.apply(this, args);
            }, timeout);
        };
    }

    systemRenderWebhooks(UIManager, webhookElement, system_data) {
        webhookElement.innerHTML = '';

        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Webhook Config",
            parent: webhookElement
        })

        const newWebhookForm = UIManager.createElement('div', {
            id: `system_${system_data.system_id}_webhook-form`,
            className: 'd-flex flex-column',  // Using flexbox to arrange children
            parent: webhookElement
        });

        // Container for the webhook URL input and its label
        const formWebhookURLGroup = UIManager.createElement('div', {
            className: 'mb-3',  // Margin bottom for spacing
            parent: newWebhookForm
        });

        UIManager.createElement('label', {
            for: `system_${system_data.system_id}_webhook_url`,  // Ensure the 'for' attribute matches the input's ID
            className: 'form-label',
            textContent: 'Webhook URL',
            parent: formWebhookURLGroup
        });

        UIManager.createElement('input', {
            id: `system_${system_data.system_id}_webhook_url`,
            type: 'url',
            className: 'form-control',  // Bootstrap class for styling form inputs
            attributes: {
                'placeholder': 'https://webhook.example.com',
                'title': 'Webhook URL',
                'aria-label': 'Enter the URL for the webhook'
            },
            parent: formWebhookURLGroup
        });

        // Container for the webhook headers textarea and its label
        const formWebhookHeaderGroup = UIManager.createElement('div', {
            className: 'mb-3',  // Margin bottom for spacing
            parent: newWebhookForm
        });

        UIManager.createElement('label', {
            for: `system_${system_data.system_id}_webhook_headers`,
            className: 'form-label',
            textContent: 'Webhook Headers (JSON)',
            parent: formWebhookHeaderGroup
        });

        UIManager.createElement('textarea', {
            id: `system_${system_data.system_id}_webhook_headers`,
            className: 'form-control',  // Bootstrap class for styling textareas
            attributes: {
                'placeholder': '{"key": "value"}',
                'title': 'Webhook Headers (JSON)',
                'aria-label': 'Enter the headers for the webhook in JSON format',
                'rows': 5
            },
            parent: formWebhookHeaderGroup
        });

        const formWebhookBodyGroup = UIManager.createElement('div', {
            className: 'mb-3',  // Margin bottom for spacing
            parent: newWebhookForm
        });

        UIManager.createElement('label', {
            for: `system_${system_data.system_id}_webhook_body`,
            className: 'form-label',
            textContent: 'Webhook Body (JSON)',
            parent: formWebhookBodyGroup
        });

        UIManager.createElement('textarea', {
            id: `system_${system_data.system_id}_webhook_body`,
            className: 'form-control',  // Bootstrap class for styling textareas
            attributes: {
                'placeholder': '{"key": "value"}',
                'title': 'Webhook Body (JSON)',
                'aria-label': 'Enter the body for the webhook in JSON format',
                'rows': 5
            },
            parent: formWebhookBodyGroup
        });

        // Create a container for the checkbox and the button, using flexbox
        const actionContainer = UIManager.createElement('div', {
            className: 'd-flex justify-content-between align-items-center mt-3',
            parent: newWebhookForm
        });

        // Create a div that will hold the checkbox and its label
        const checkBoxContainer = UIManager.createElement('div', {
            className: 'form-check form-switch',
            parent: actionContainer
        });

        const checkBoxInput = UIManager.createElement('input', {
            id: `system_${system_data.system_id}_webhook_enabled`,
            type: 'checkbox',
            role: 'switch',
            className: 'form-check-input me-2',
            parent: checkBoxContainer,
            attributes: {
                'role': 'switch',
                'aria-label': "Checkbox for enabling webhook"
            }
        });

        const checkBoxLabel = UIManager.createElement('label', {
            className: 'form-check-label',
            textContent: 'Webhook Disabled',
            attributes: {'for': `system_${system_data.system_id}_webhook_enabled`},
            parent: checkBoxContainer
        });

        checkBoxInput.addEventListener('change', function () {
            checkBoxLabel.textContent = this.checked ? 'Webhook Enabled' : 'Webhook Disabled';
        });

        // Add the submit button to add a new webhook, aligned to the right of the checkbox
        const addButton = UIManager.createElement('button', {
            className: 'btn btn-primary',
            textContent: 'Add Webhook',
            parent: actionContainer
        });

        addButton.onclick = () => this.systemAddWebhook(UIManager, system_data)

        const accordianTitle = UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Current Webhooks",
            parent: webhookElement
        })

        const accordionContainer = UIManager.createElement('div', {
            id: `webhooks_accordion_${system_data.system_id}`,
            className: "accordion mt-4 mb-4",
            parent: webhookElement
        })


        system_data.system_webhooks.forEach((webhook, index) => {
            this.systemAppendWebhookAccordion(UIManager, webhook, index, accordionContainer, system_data);
        });

        const controlCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: webhookElement})

        const saveChangesButton = UIManager.createElement('button', {
            className: 'btn btn-success',
            textContent: "Save Changes",
            parent: controlCol
        })
        saveChangesButton.onclick = () => this.systemSaveWebhooks(UIManager, system_data)
    }

    systemAppendWebhookAccordion(UIManager, webhook, index, accordionContainer, system_data) {

        // Create the accordion item
        const item = document.createElement('div');
        item.className = 'accordion-item';
        item.setAttribute('data-index', index);
        accordionContainer.appendChild(item);

        // Create the header of the accordion
        const header = document.createElement('h2');
        header.className = 'accordion-header';
        header.id = `heading_webhook_${system_data.system_id}_${index}`;
        item.appendChild(header);

        const button = document.createElement('button');
        button.className = 'accordion-button collapsed';
        button.type = 'button';
        button.setAttribute('data-bs-toggle', 'collapse');
        button.setAttribute('data-bs-target', `#collapse_webhook_${system_data.system_id}_${index}`);
        button.setAttribute('aria-expanded', 'false');
        button.setAttribute('aria-controls', `collapse_webhook_${system_data.system_id}_${index}`);
        button.textContent = `Webhook: ${webhook.webhook_url}`;
        header.appendChild(button);

        // Create the collapsible content area
        const collapseDiv = document.createElement('div');
        collapseDiv.id = `collapse_webhook_${system_data.system_id}_${index}`;
        collapseDiv.className = 'accordion-collapse collapse';
        collapseDiv.setAttribute('aria-labelledby', `heading_webhook_${system_data.system_id}_${index}`);
        collapseDiv.setAttribute('data-bs-parent', '#webhooks-accordion');
        item.appendChild(collapseDiv);

        const bodyDiv = document.createElement('div');
        bodyDiv.className = 'accordion-body';
        collapseDiv.appendChild(bodyDiv);

        // Input for URL
        const urlFormGroup = document.createElement('div');
        urlFormGroup.className = 'mb-3';
        bodyDiv.appendChild(urlFormGroup);

        const urlLabel = document.createElement('label');
        urlLabel.className = 'form-label';
        urlLabel.textContent = 'URL';
        urlFormGroup.appendChild(urlLabel);

        const urlInput = document.createElement('input');
        urlInput.type = 'url';
        urlInput.className = 'form-control';
        urlInput.value = webhook.webhook_url;
        urlInput.onblur = this.debounce(() => {
            if (!urlInput.value.startsWith('http://') && !urlInput.value.startsWith('https://')) {
                UIManager.showAlert('Please enter a valid URL.', 'danger');
                return;
            }
            webhook.webhook_url = urlInput.value
        });
        urlFormGroup.appendChild(urlInput);

        // Textarea for JSON headers
        const headersFormGroup = document.createElement('div');
        headersFormGroup.className = 'mb-3';
        bodyDiv.appendChild(headersFormGroup);

        const headersLabel = document.createElement('label');
        headersLabel.className = 'form-label';
        headersLabel.textContent = 'Headers (JSON)';
        headersFormGroup.appendChild(headersLabel);

        const headersInput = document.createElement('textarea');
        headersInput.className = 'form-control';

        // Ensure webhook_headers is a valid object or provide a default empty object
        if (typeof webhook.webhook_headers !== 'object' || webhook.webhook_headers === null) {
            webhook.webhook_headers = {};
        }

        // Convert the JSON object to a formatted JSON string for editing
        headersInput.value = JSON.stringify(webhook.webhook_headers, null, 4);
        headersInput.onblur = this.debounce(() => {
            try {
                webhook.webhook_headers = JSON.parse(headersInput.value);
            } catch (e) {
                UIManager.showAlert('Invalid JSON format', 'danger');
            }

        });
        headersFormGroup.appendChild(headersInput);

        // Textarea for JSON body
        const bodyFormGroup = document.createElement('div');
        bodyFormGroup.className = 'mb-3';
        bodyDiv.appendChild(bodyFormGroup);

        const bodyLabel = document.createElement('label');
        bodyLabel.className = 'form-label';
        bodyLabel.textContent = 'Body (JSON)';
        bodyFormGroup.appendChild(bodyLabel);

        const bodyInput = document.createElement('textarea');
        bodyInput.className = 'form-control';

        // Ensure webhook_headers is a valid object or provide a default empty object
        if (typeof webhook.webhook_body !== 'object' || webhook.webhook_body === null) {
            webhook.webhook_body = {};
        }

        // Convert the JSON object to a formatted JSON string for editing
        bodyInput.value = JSON.stringify(webhook.webhook_body, null, 4);
        bodyInput.onblur = this.debounce(() => {
            try {
                webhook.webhook_body = JSON.parse(bodyInput.value);
            } catch (e) {
                UIManager.showAlert('Invalid JSON format', 'danger');
            }

        });
        bodyFormGroup.appendChild(bodyInput);

        // Checkbox for Enabled status
        const checkDiv = document.createElement('div');
        checkDiv.className = 'mb-3 form-check form-switch';
        bodyDiv.appendChild(checkDiv);

        const enabledCheckbox = document.createElement('input');
        enabledCheckbox.type = 'checkbox';
        enabledCheckbox.className = 'form-check-input me-2';
        enabledCheckbox.role = 'switch';
        enabledCheckbox.id = `enabled_webhook_${system_data.system_id}_${index}`;
        enabledCheckbox.checked = webhook.enabled;
        checkDiv.appendChild(enabledCheckbox);

        const enabledLabel = document.createElement('label');
        enabledLabel.className = 'form-check-label';
        enabledLabel.setAttribute('for', `enabled_webhook_${system_data.system_id}_${index}`);
        enabledLabel.textContent = webhook.enabled ? 'Webhook Enabled' : 'Webhook Disabled';
        checkDiv.appendChild(enabledLabel);

        enabledCheckbox.addEventListener('change', function () {
            webhook.enabled = enabledCheckbox.checked;
            enabledLabel.textContent = webhook.enabled ? 'Webhook Enabled' : 'Webhook Disabled';
        });

        const controlCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: bodyDiv})

        // Delete button
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger';
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => {
            const accordionContainer = document.getElementById(`webhooks_accordion_${system_data.system_id}`);

            const accordionItem = accordionContainer.querySelector(`.accordion-item[data-index="${index}"]`);

            if (accordionItem) {
                accordionItem.parentNode.removeChild(accordionItem);
                system_data.system_webhooks.splice(index, 1);
            }
        };

        controlCol.appendChild(deleteButton);
    }

    systemAddWebhook(UIManager, system_data) {
        const webhook_url = document.getElementById(`system_${system_data.system_id}_webhook_url`).value;
        const webhook_headers = document.getElementById(`system_${system_data.system_id}_webhook_headers`).value;
        const webhook_body = document.getElementById(`system_${system_data.system_id}_webhook_body`).value;
        const enabled = document.getElementById(`system_${system_data.system_id}_webhook_enabled`).checked;

        // Validate the URL
        if (!webhook_url) {
            UIManager.showAlert('Webhook URL cannot be empty.', 'danger');
            return;
        }

        if (!webhook_url.startsWith('http://') && !webhook_url.startsWith('https://')) {
            UIManager.showAlert('Webhook URL must be valid URL.', 'danger');
            return;
        }

        // Validate JSON for headers
        let parsedHeaders;
        try {
            parsedHeaders = JSON.parse(webhook_headers); // Validate JSON
        } catch (e) {
            UIManager.showAlert('Headers must be in valid JSON format', 'danger');
            return;
        }

        // Validate JSON for body
        let parsedBody;
        try {
            parsedBody = JSON.parse(webhook_body); // Validate JSON
        } catch (e) {
            UIManager.showAlert('Body must be in valid JSON format', 'danger');
            return;
        }

        const newWebhook = {
            webhook_id: null,
            webhook_url: webhook_url,
            webhook_headers: parsedHeaders,
            webhook_body: parsedBody,
            enabled: enabled
        };

        // Calculate the index for the new webhook
        const newIndex = system_data.system_webhooks.length;

        system_data.system_webhooks.push(newWebhook);

        let accordianContainer = document.getElementById(`webhooks_accordion_${system_data.system_id}`)
        this.systemAppendWebhookAccordion(UIManager, newWebhook, newIndex, accordianContainer, system_data)

        // Create and append the new webhook data
        // Here you would normally update the data structure or call an API
        console.log('Webhook added:', {webhook_url, parsedHeaders, parsedBody, enabled});

        // Clear the form inputs (Example only, needs actual implementation)
        document.getElementById(`system_${system_data.system_id}_webhook_url`).value = '';
        document.getElementById(`system_${system_data.system_id}_webhook_headers`).value = '';
        document.getElementById(`system_${system_data.system_id}_webhook_body`).value = '';
        document.getElementById(`system_${system_data.system_id}_webhook_enabled`).checked = false;
    }

    systemSaveWebhooks(UIManager, system_data) {
        // Construct the URL for the save operation
        const save_url = `/admin/save_system_webhooks`;

        // Get the current webhook data from the system_data which should be updated throughout operations
        const webhookData = {"system_id": system_data.system_id, "system_webhooks": system_data.system_webhooks};

        console.log(webhookData)

        fetch(save_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(webhookData)
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to save changes');
                }
            })
            .then(data => {
                if (data.success) {
                    UIManager.showAlert(data.message, "success");
                } else {
                    UIManager.showAlert("Failed to save webhooks. Error: " + data.message, "danger");
                }
            })
            .catch(error => {
                console.error("Error saving webhooks:", error);
                // Display an error message
                UIManager.showAlert("Failed to save webhooks. Error: " + error.message, "danger");
            });
    }

    triggerRenderWebhooks(UIManager, webhookElement, trigger_data) {
        webhookElement.innerHTML = '';

        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Webhook Config",
            parent: webhookElement
        })

        const newWebhookForm = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook-form`,
            className: 'd-flex flex-column',  // Using flexbox to arrange children
            parent: webhookElement
        });

        // Container for the webhook URL input and its label
        const formWebhookURLGroup = UIManager.createElement('div', {
            className: 'mb-3',  // Margin bottom for spacing
            parent: newWebhookForm
        });

        UIManager.createElement('label', {
            for: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_url`,
            className: 'form-label',
            textContent: 'Webhook URL',
            parent: formWebhookURLGroup
        });

        UIManager.createElement('input', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_url`,
            type: 'url',
            className: 'form-control',
            attributes: {
                'placeholder': 'https://webhook.example.com',
                'title': 'Webhook URL',
                'aria-label': 'Enter the URL for the webhook'
            },
            parent: formWebhookURLGroup
        });

        // Container for the webhook headers textarea and its label
        const formWebhookHeaderGroup = UIManager.createElement('div', {
            className: 'mb-3',  // Margin bottom for spacing
            parent: newWebhookForm
        });

        UIManager.createElement('label', {
            for: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_headers`,
            className: 'form-label',
            textContent: 'Webhook Headers (JSON)',
            parent: formWebhookHeaderGroup
        });

        UIManager.createElement('textarea', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_headers`,
            className: 'form-control',
            attributes: {
                'placeholder': '{"key": "value"}',
                'title': 'Webhook Headers (JSON)',
                'aria-label': 'Enter the headers for the webhook in JSON format',
                'rows': 5
            },
            parent: formWebhookHeaderGroup
        });

        const formWebhookBodyGroup = UIManager.createElement('div', {
            className: 'mb-3',  // Margin bottom for spacing
            parent: newWebhookForm
        });

        UIManager.createElement('label', {
            for: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_body`,
            className: 'form-label',
            textContent: 'Webhook Body (JSON)',
            parent: formWebhookBodyGroup
        });

        UIManager.createElement('textarea', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_body`,
            className: 'form-control',  // Bootstrap class for styling textareas
            attributes: {
                'placeholder': '{"key": "value"}',
                'title': 'Webhook Body (JSON)',
                'aria-label': 'Enter the body for the webhook in JSON format',
                'rows': 5
            },
            parent: formWebhookBodyGroup
        });

        // Create a container for the checkbox and the button, using flexbox
        const actionContainer = UIManager.createElement('div', {
            className: 'd-flex justify-content-between align-items-center mt-3',
            parent: newWebhookForm
        });

        // Create a div that will hold the checkbox and its label
        const checkBoxContainer = UIManager.createElement('div', {
            className: 'form-check form-switch',
            parent: actionContainer
        });

        const checkBoxInput = UIManager.createElement('input', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_enabled`,
            type: 'checkbox',
            role: 'switch',
            className: 'form-check-input me-2',
            parent: checkBoxContainer,
            attributes: {
                'role': 'switch',
                'aria-label': "Checkbox for enabling webhook"
            }
        });

        const checkBoxLabel = UIManager.createElement('label', {
            className: 'form-check-label',
            textContent: 'Webhook Disabled',
            attributes: {'for': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_enabled`},
            parent: checkBoxContainer
        });

        checkBoxInput.addEventListener('change', function () {
            checkBoxLabel.textContent = this.checked ? 'Webhook Enabled' : 'Webhook Disabled';
        });

        // Add the submit button to add a new webhook, aligned to the right of the checkbox
        const addButton = UIManager.createElement('button', {
            className: 'btn btn-primary',
            textContent: 'Add Webhook',
            parent: actionContainer
        });

        addButton.onclick = () => this.triggerAddWebhook(UIManager, trigger_data)

        const accordianTitle = UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Current Webhooks",
            parent: webhookElement
        })

        const accordionContainer = UIManager.createElement('div', {
            id: `webhooks_accordion_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            className: "accordion mt-4 mb-4",
            parent: webhookElement
        })

        trigger_data.trigger_webhooks.forEach((webhook, index) => {
            this.triggerAppendWebhookAccordion(UIManager, webhook, index, accordionContainer, trigger_data);
        });

        const controlCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: webhookElement})

        const saveChangesButton = UIManager.createElement('button', {
            className: 'btn btn-success text-end',
            textContent: "Save Changes",
            parent: controlCol
        })
        saveChangesButton.onclick = () => this.triggerSaveWebhooks(UIManager, trigger_data)
    }

    triggerAppendWebhookAccordion(UIManager, webhook, index, accordionContainer, trigger_data) {

        // Create the accordion item
        const item = document.createElement('div');
        item.className = 'accordion-item';
        item.setAttribute('data-index', index);
        accordionContainer.appendChild(item);

        // Create the header of the accordion
        const header = document.createElement('h2');
        header.className = 'accordion-header';
        header.id = `heading_webhook_${trigger_data.system_id}_${trigger_data.trigger_id}_${index}`;
        item.appendChild(header);

        const button = document.createElement('button');
        button.className = 'accordion-button collapsed';
        button.type = 'button';
        button.setAttribute('data-bs-toggle', 'collapse');
        button.setAttribute('data-bs-target', `#collapse_webhook_${trigger_data.system_id}_${trigger_data.trigger_id}_${index}`);
        button.setAttribute('aria-expanded', 'false');
        button.setAttribute('aria-controls', `collapse_webhook_${trigger_data.system_id}_${trigger_data.trigger_id}_${index}`);
        button.textContent = `Webhook: ${webhook.webhook_url}`;
        header.appendChild(button);

        // Create the collapsible content area
        const collapseDiv = document.createElement('div');
        collapseDiv.id = `collapse_webhook_${trigger_data.system_id}_${trigger_data.trigger_id}_${index}`;
        collapseDiv.className = 'accordion-collapse collapse';
        collapseDiv.setAttribute('aria-labelledby', `heading_webhook_${trigger_data.system_id}_${trigger_data.trigger_id}_${index}`);
        collapseDiv.setAttribute('data-bs-parent', '#webhooks-accordion');
        item.appendChild(collapseDiv);

        const bodyDiv = document.createElement('div');
        bodyDiv.className = 'accordion-body';
        collapseDiv.appendChild(bodyDiv);

        // Input for URL
        const urlFormGroup = document.createElement('div');
        urlFormGroup.className = 'mb-3';
        bodyDiv.appendChild(urlFormGroup);

        const urlLabel = document.createElement('label');
        urlLabel.className = 'form-label';
        urlLabel.textContent = 'URL';
        urlFormGroup.appendChild(urlLabel);

        const urlInput = document.createElement('input');
        urlInput.type = 'url';
        urlInput.className = 'form-control';
        urlInput.value = webhook.webhook_url;
        urlInput.onblur = this.debounce(() => {
            if (!urlInput.value.startsWith('http://') && !urlInput.value.startsWith('https://')) {
                UIManager.showAlert('Please enter a valid URL.', 'danger');
                return;
            }
            webhook.webhook_url = urlInput.value
        });
        urlFormGroup.appendChild(urlInput);

        // Textarea for JSON headers
        const headersFormGroup = document.createElement('div');
        headersFormGroup.className = 'mb-3';
        bodyDiv.appendChild(headersFormGroup);

        const headersLabel = document.createElement('label');
        headersLabel.className = 'form-label';
        headersLabel.textContent = 'Headers (JSON)';
        headersFormGroup.appendChild(headersLabel);

        const headersInput = document.createElement('textarea');
        headersInput.className = 'form-control';

        // Ensure webhook_headers is a valid object or provide a default empty object
        if (typeof webhook.webhook_headers !== 'object' || webhook.webhook_headers === null) {
            webhook.webhook_headers = {};
        }

        // Convert the JSON object to a formatted JSON string for editing
        headersInput.value = JSON.stringify(webhook.webhook_headers, null, 4);
        headersInput.onblur = this.debounce(() => {
            try {
                webhook.webhook_headers = JSON.parse(headersInput.value);
            } catch (e) {
                UIManager.showAlert('Invalid JSON format', 'danger');
            }

        });
        headersFormGroup.appendChild(headersInput);

        // Textarea for JSON body
        const bodyFormGroup = document.createElement('div');
        bodyFormGroup.className = 'mb-3';
        bodyDiv.appendChild(bodyFormGroup);

        const bodyLabel = document.createElement('label');
        bodyLabel.className = 'form-label';
        bodyLabel.textContent = 'Body (JSON)';
        bodyFormGroup.appendChild(bodyLabel);

        const bodyInput = document.createElement('textarea');
        bodyInput.className = 'form-control';

        // Ensure webhook_headers is a valid object or provide a default empty object
        if (typeof webhook.webhook_body !== 'object' || webhook.webhook_body === null) {
            webhook.webhook_body = {};
        }

        // Convert the JSON object to a formatted JSON string for editing
        bodyInput.value = JSON.stringify(webhook.webhook_body, null, 4);
        bodyInput.onblur = this.debounce(() => {
            try {
                webhook.webhook_body = JSON.parse(bodyInput.value);
            } catch (e) {
                UIManager.showAlert('Invalid JSON format', 'danger');
            }

        });
        bodyFormGroup.appendChild(bodyInput);

        // Checkbox for Enabled status
        const checkDiv = document.createElement('div');
        checkDiv.className = 'mb-3 form-check form-switch';
        bodyDiv.appendChild(checkDiv);

        const enabledCheckbox = document.createElement('input');
        enabledCheckbox.type = 'checkbox';
        enabledCheckbox.className = 'form-check-input me-2';
        enabledCheckbox.role = 'switch';
        enabledCheckbox.id = `enabled_webhook_${trigger_data.system_id}_${trigger_data.trigger_id}_${index}`;
        enabledCheckbox.checked = webhook.enabled;
        checkDiv.appendChild(enabledCheckbox);

        const enabledLabel = document.createElement('label');
        enabledLabel.className = 'form-check-label';
        enabledLabel.setAttribute('for', `enabled_webhook_${trigger_data.system_id}_${trigger_data.trigger_id}_${index}`);
        enabledLabel.textContent = webhook.enabled ? 'Webhook Enabled' : 'Webhook Disabled';
        checkDiv.appendChild(enabledLabel);

        enabledCheckbox.addEventListener('change', function () {
            webhook.enabled = enabledCheckbox.checked;
            enabledLabel.textContent = webhook.enabled ? 'Webhook Enabled' : 'Webhook Disabled';
        });
        const controlCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: bodyDiv})
        // Delete button
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger';
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => {
            const accordionContainer = document.getElementById(`webhooks_accordion_${trigger_data.system_id}_${trigger_data.trigger_id}`);

            const accordionItem = accordionContainer.querySelector(`.accordion-item[data-index="${index}"]`);

            if (accordionItem) {
                accordionItem.parentNode.removeChild(accordionItem);
                trigger_data.trigger_webhooks.splice(index, 1);
            }
        };

        controlCol.appendChild(deleteButton);
    }

    triggerAddWebhook(UIManager, trigger_data) {
        const webhook_url = document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_url`).value;
        const webhook_headers = document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_headers`).value;
        const webhook_body = document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_body`).value;
        const enabled = document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_enabled`).checked;

        // Validate the URL
        if (!webhook_url) {
            UIManager.showAlert('Webhook URL cannot be empty.', 'danger');
            return;
        }

        if (!webhook_url.startsWith('http://') && !webhook_url.startsWith('https://')) {
            UIManager.showAlert('Webhook URL must be valid URL.', 'danger');
            return;
        }

        // Validate JSON for headers
    let parsedHeaders;
    try {
        parsedHeaders = JSON.parse(webhook_headers); // Validate JSON
    } catch (e) {
        UIManager.showAlert('Headers must be in valid JSON format', 'danger');
        return;
    }

    // Validate JSON for body
    let parsedBody;
    try {
        parsedBody = JSON.parse(webhook_body); // Validate JSON
    } catch (e) {
        UIManager.showAlert('Body must be in valid JSON format', 'danger');
        return;
    }

        const newWebhook = {
            webhook_id: null,
            webhook_url: webhook_url,
            webhook_headers: parsedHeaders,
            webhook_body: parsedBody,
            enabled: enabled
        };

        // Calculate the index for the new webhook
        const newIndex = trigger_data.trigger_webhooks.length;

        trigger_data.trigger_webhooks.push(newWebhook);

        let accordianContainer = document.getElementById(`webhooks_accordion_${trigger_data.system_id}_${trigger_data.trigger_id}`)
        this.triggerAppendWebhookAccordion(UIManager, newWebhook, newIndex, accordianContainer, trigger_data)

        // Create and append the new webhook data
        // Here you would normally update the data structure or call an API
        console.log('Trigger Webhook added:', {webhook_url, parsedHeaders, parsedBody, enabled});

        // Clear the form inputs (Example only, needs actual implementation)
        document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_url`).value = '';
        document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_headers`).value = '{}';
        document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_body`).value = '{}';
        document.getElementById(`trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook_enabled`).checked = false;
    }

    triggerSaveWebhooks(UIManager, trigger_data) {
        // Construct the URL for the save operation
        const save_url = `${UIManager.baseUrl}/admin/save_trigger_webhooks`;

        // Get the current webhook data from the system_data which should be updated throughout operations
        const webhookData = {
            "trigger_id": trigger_data.trigger_id,
            "system_id": trigger_data.system_id,
            "trigger_webhooks": trigger_data.trigger_webhooks
        };

        console.log(webhookData)

        fetch(save_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(webhookData)
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to save changes');
                }
            })
            .then(data => {
                if (data.success) {
                    UIManager.showAlert(data.message, "success");
                } else {
                    UIManager.showAlert("Failed to save webhooks. Error: " + data.message, "danger");
                }
            })
            .catch(error => {
                console.error("Error saving webhooks:", error);
                // Display an error message
                UIManager.showAlert("Failed to save webhooks. Error: " + error.message, "danger");
            });
    }
}