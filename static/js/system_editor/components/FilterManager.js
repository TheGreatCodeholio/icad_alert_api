export class FilterManager {
    constructor() {
        this.region = window.region;
    }

    addFilterToPage(UIManager, filter_data) {
        if (!filter_data) {
            return
        }

        //Add System Links to Sidebar
        const filterListItem = UIManager.createElement('li', {className: 'mb-1', parent: UIManager.filter_menu});

        const filterButton = UIManager.createElement('button', {
            className: 'btn btn-toggle d-inline-flex align-items-center rounded border-0 collapsed',
            attributes: {
                'data-bs-toggle': 'collapse',
                'data-bs-target': `#filter_${filter_data.alert_filter_id}-collapse`,
                'aria-expanded': 'false'
            },
            textContent: filter_data.alert_filter_name,
            parent: filterListItem
        });

        const filterButtonCollapse = UIManager.createElement('div', {
            id: `filter_${filter_data.alert_filter_id}-collapse`,
            className: 'collapse',
            parent: filterListItem
        });

        const filterMenuCollapse = UIManager.createElement('ul', {
            className: 'btn-toggle-nav list-unstyled fw-normal pb-1 small',
            parent: filterButtonCollapse
        });

        // Define the submenu items
        const submenuItems = [
            {id: `filter_${filter_data.alert_filter_id}_general-tab`, text: 'General', link: ''},
            {id: `filter_${filter_data.alert_filter_id}_keyword-tab`, text: 'Keywords', link: ''},
        ];

        // Create menu items dynamically
        submenuItems.forEach(item => {
            this.filterCreateMenuItem(UIManager, filterMenuCollapse, item.id, item.text, item.link);
        });

        const filterGeneralTabContent = UIManager.createElement('div', {
            id: `filter_${filter_data.alert_filter_id}_general-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `filter_${filter_data.alert_filter_id}_general-tab`,
                'tabindex': "0"
            },
            parent: UIManager.filter_content
        })

        this.filterCreateGeneralPage(UIManager, filterGeneralTabContent, filter_data)

        const filterKeywordTabContent = UIManager.createElement('div', {
            id: `filter_${filter_data.alert_filter_id}_keyword-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `filter_${filter_data.alert_filter_id}_keyword-tab`,
                'tabindex': "0"
            },
            parent: UIManager.filter_content
        })

        this.filterCreateKeywordPage(UIManager, filterKeywordTabContent, filter_data)

    }

    filterCreateMenuItem(UIManager, parent, id, text, link){
        let listItem = UIManager.createElement('li', {parent: parent});
        if (link === ''){
            const menu_button = UIManager.createElement('button', {
                id: id,
                type: 'button',
                className: 'nav-link system_setting',
                textContent: text,
                attributes: {
                    'data-bs-toggle': 'tab',
                    'data-bs-target': `#${id}-pane`,
                    'role': 'tab',
                    'aria-controls': `${id}-pane`,
                    'aria-selected': 'false'
                },
                parent: listItem
            });
            menu_button.addEventListener('click', () => {
                const sidebarCollapse = new bootstrap.Collapse(document.getElementById('sidebarCollapse'));
                sidebarCollapse.hide();
            });
        } else {
            const menu_button = UIManager.createElement('button', {
                id: id,
                type: 'button',
                className: 'nav-link system_setting',
                textContent: text,
                parent: listItem
            });
            menu_button.addEventListener('click', () => {
                window.location.href = link;
            });
        }
    }

    filterCreateGeneralPage(UIManager, filterGeneralElement, filter_data){
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "General Config",
            parent: filterGeneralElement
        })

        // Form to Edit General System
        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `filter_general_form_${filter_data.alert_filter_id}`,
            parent: filterGeneralElement
        });

        let inputFields = [
            {
                id: `alert_filter_id`,
                label: 'Filter ID',
                tooltip: 'ID of the Alert Filter. (read only)',
                type: 'number',
                value: filter_data.alert_filter_id,
                col_class: 'col-md-6',
                readOnly: true
            },
            {
                id: `alert_filter_name`,
                label: 'Filter Name',
                tooltip: 'Name Of this filter.',
                type: 'text',
                col_class: 'col-12',
                value: filter_data.alert_filter_name
            },
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, filter_data.alert_filter_id, field.value);
        });

        const formControlCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        // Checkbox for Enabled status
        const checkDiv = document.createElement('div');
        checkDiv.className = 'mb-3 form-check form-switch text-end';
        formControlCol.appendChild(checkDiv);

        const enabledCheckbox = document.createElement('input');
        enabledCheckbox.type = 'checkbox';
        enabledCheckbox.name = 'enabled';
        enabledCheckbox.className = 'form-check-input me-2';
        enabledCheckbox.role = 'switch';
        enabledCheckbox.id = `enabled_filter_${filter_data.alert_filter_id}`;
        enabledCheckbox.checked = filter_data.enabled;
        checkDiv.appendChild(enabledCheckbox);

        const enabledLabel = document.createElement('label');
        enabledLabel.className = 'form-check-label';
        enabledLabel.setAttribute('for', `enabled_filter_${filter_data.alert_filter_id}`);
        enabledLabel.textContent = filter_data.enabled ? 'Filter Enabled' : 'Filter Disabled'; // Set initial label text based on the checkbox state
        checkDiv.appendChild(enabledLabel);

        // Event listener for changing label text upon toggle
        enabledCheckbox.addEventListener('change', function() {
            enabledLabel.textContent = this.checked ? 'Filter Enabled' : 'Filter Disabled';
        });

        const saveFilterButton = UIManager.createElement('button', {
            id: `filterSaveGeneral_${filter_data.alert_filter_id}`,
            className: "btn btn-md btn-success me-2",
            attributes: {
                "data-filter-id": filter_data.alert_filter_id
            },
            textContent: "Save",
            parent: formControlCol,
            type: 'button'
        });

        saveFilterButton.onclick = () => {
            this.filterPostForm(UIManager, '/admin/save_filter_general', `filter_general_form_${filter_data.alert_filter_id}`)
        }

        const deleteTriggerButton = UIManager.createElement('button', {
            id: `deleteFilter_${filter_data.alert_filter_id}`,
            className: "btn btn-md btn-danger",
            attributes: {
                "data-filter-id": filter_data.alert_filter_id
            },
            textContent: "Delete",
            parent: formControlCol,
            type: 'button',
            name: 'delete_filter'
        });
        deleteTriggerButton.onclick = () => {
            this.filterDeleteAction(UIManager, filter_data.alert_filter_id, trigger_data.alert_filter_name)
        }

    }

    filterCreateKeywordPage(UIManager, filterKeywordElement, filter_data){
        UIManager.KeywordManager.renderFilterKeywords(UIManager, filterKeywordElement, filter_data);
    }

    filterPostForm(UIManager, save_url, form_id) {

        save_url = `${UIManager.baseUrl}${save_url}`;

        // Get the form element using its ID
        const form = document.getElementById(form_id);
        if (!form) {
            UIManager.showAlert(`Form Not Found: ${form_id}`)
            return;
        }

        // Check all required fields in the form
        const requiredFields = form.querySelectorAll('[required]');
        let allFieldsValid = true;
        let invalidFields = [];

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                allFieldsValid = false;
                field.classList.add('is-invalid');
                field.addEventListener('input', function() {
                    field.classList.remove('is-invalid');
                });
                // Get the field name or label text for the error message
                let fieldName;
                let fieldLabel = document.querySelector(`label[for="${field.id}"]`);
                if (fieldLabel && fieldLabel.textContent) {
                    fieldName = fieldLabel.textContent.trim().replace(/[:*]$/, ''); // Remove any colon or asterisk from label
                }
                invalidFields.push(fieldName);

            }
        });

        if (!allFieldsValid) {
            invalidFields.forEach(fieldName => {
                UIManager.showAlert(`${fieldName} can not be empty`, 'danger');
            })
            return;
        }

        // Create a FormData object from the form element
        const formData = new FormData(form);

        // Use the Fetch API to send the form data
        fetch(save_url, {
            method: 'POST', // Set the method to POST
            body: formData, // Attach the FormData object as the body of the request
        })
            .then(response => response.json()) // Parse JSON response
            .then(data => {
                if (data.success) {
                    console.log('Success:', data.message);
                    UIManager.showAlert(data.message, "success")
                } else {
                    console.log('Form Post Error:', data);
                    UIManager.showAlert(data.message, "danger")
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                UIManager.showAlert(error, "danger") // Assuming there's a method to update the UI on error
            });
    }

    filterDeleteAction(UIManager, filter_id, filter_name) {
        const systemData = {"filter_id": filter_id, "filter_name": filter_name};
        fetch(`${UIManager.baseUrl}/admin/delete_filter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(systemData)
        })
            .then(response => response.json()) // Parse JSON response
            .then(data => {
                if (data.success) {
                    console.log('Success:', data.message);
                    UIManager.showAlert(data.message, "success")
                    window.location.reload();
                } else {
                    console.log('Form Post Error:', data);
                    UIManager.showAlert(data.message, "danger")
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                UIManager.showAlert(error, "danger") // Assuming there's a method to update the UI on error
            });
    }


}