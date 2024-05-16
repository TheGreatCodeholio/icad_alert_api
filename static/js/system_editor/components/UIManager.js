export class UIManager {
    constructor(SystemManager, TriggerManager, EmailAddressManager, WebhookManager, FilterManager, KeywordManager) {
        this.region = window.region;
        this.EmailAddressManager = EmailAddressManager;
        this.WebhookManager = WebhookManager;
        this.SystemManager = SystemManager;
        this.TriggerManager = TriggerManager;
        this.FilterManager = FilterManager;
        this.KeywordManager = KeywordManager;
        this.system_menu = document.getElementById('system_sidebar');
        this.trigger_menu = document.getElementById('trigger_sidebar');
        this.filter_menu = document.getElementById('filter_sidebar')
        this.system_content = document.getElementById('systemTabContent');
        this.trigger_content = document.getElementById('triggerTabContent');
        this.filter_content = document.getElementById('filterTabContent')
        this.trigger_title = document.getElementById('trigger_title')
        this.trigger_form_system_id = document.getElementById('systemId')
        this.toast_container = document.getElementById('toastContainer');

        this.createElement = this.createElement.bind(this);
    }

    initSystemsPage(systems_data) {
        if (systems_data.result){
            systems_data.result.forEach(system_data => {
                this.SystemManager.addSystemToPage(this, system_data)
            });
        }

    }

    initTriggersPage(system_data, filter_data) {
        this.TriggerManager.renderTriggersPage(this, system_data, filter_data)
    }

    initFiltersPage(filters_data){
        if (filters_data.result){
            filters_data.result.forEach(filter_data => {
                this.FilterManager.addFilterToPage(this, filter_data)
            })

        }
    }

    /**
     * Utility function to create and return a DOM element with options.
     *
     * @param {string} type - The type of DOM element to create (e.g., 'div', 'input').
     * @param {Object} options - Configuration options for the element.
     * @returns {HTMLElement} The created DOM element.
     */
    createElement(type, options = {}) {
        const element = document.createElement(type);
        if (options.className) element.className = options.className;
        if (options.textContent) element.textContent = options.textContent;
        if (options.innerHTML) element.innerHTML = options.innerHTML;
        if (options.parent) options.parent.appendChild(element);
        if (options.role) element.role = options.role;
        if (options.type) element.type = options.type;
        if (options.value) element.value = options.value;
        if (options.id) element.id = options.id;
        if (options.name) element.name = options.name;
        if (options.readOnly) element.readOnly = true;
        if (options.selected) element.selected = true;
        if (options.required) element.required = true;
        if (options.for) element.setAttribute('for', options.for)

        if (type === 'form') {
            if (options.action) element.action = options.action;
            if (options.method) element.method = options.method;
        }

        // Set additional attributes if provided
        Object.keys(options.attributes || {}).forEach(key => {
            if (options.attributes[key] !== undefined && options.attributes[key] !== 'onClick' && options.attributes[key] !== 'link') { // Check for undefined to allow removal of attributes
                element.setAttribute(key, options.attributes[key]);
            }
        });

        // Set click event handler
        if (options.onClick) {
            element.onclick = options.onClick;
        }

        // Special handling for buttons with URL links
        if (type === 'button' && options.link) {
            element.onclick = function () {
                window.location.href = options.link;
            };
        }

        // Special handling for anchor tags
        if (type === 'a' && options.link) {
            element.href = options.link;
        }

        return element;
    }

    createFormField(parent, field, systemId, fieldValue) {
        const fieldId = `${field.id}_${systemId}`;
        const {type, label, tooltip, required, options, readOnly} = field;

        // Determine column sizing
        const colSizeClass = field.col_class || 'col-12';
        const formGroupDiv = this.createElement('div', {
            className: `${colSizeClass} mb-3 ${type === 'checkbox' ? 'form-check form-switch' : ''}`,
            parent: parent
        });


        // Create label
        this.createElement('label', {
            for: fieldId,
            className: type === 'checkbox' ? 'form-check-label' : 'form-label',
            textContent: label,
            parent: formGroupDiv
        });

        // Input Group for different types of inputs
        const inputGroupDiv = this.createElement('div', {
            className: 'input-group',
            parent: type === 'select' || type === 'password' || (type === 'text' && field.id === 'system_api_key') ? formGroupDiv : null
        });

        // Create input, textarea
        let inputElement;

        // Define input elements based on type
        switch (type) {
            case 'textarea':
                inputElement = this.createElement('textarea', {
                    id: fieldId,
                    name: field.id,
                    className: 'form-control',
                    value: fieldValue ?? '',
                    readOnly: readOnly,
                    required: required,
                    attributes: {
                        'rows': field.rows || 5,
                        'data-bs-toggle': 'tooltip',
                        'data-bs-placement': 'top',
                        title: tooltip
                    },
                    parent: formGroupDiv
                });
                break;
            case 'checkbox':
                inputElement = this.createElement('input', {
                    type: 'checkbox',
                    id: fieldId,
                    name: field.id,
                    className: 'form-check-input',
                    checked: Boolean(fieldValue),

                    readOnly: readOnly,
                    required: required,
                    attributes: {
                        'role': field.role || '',
                        'data-bs-toggle': 'tooltip',
                        'data-bs-placement': 'top',
                        title: tooltip
                    },
                    parent: formGroupDiv
                });
                break;
            case 'password':
            case 'text':
            case 'email':
            case 'url':
            case 'date':
            case 'time':
            case 'number':
                inputElement = this.createElement('input', {
                    type: type,
                    id: fieldId,
                    name: field.id,
                    className: 'form-control',
                    value: fieldValue ?? '',
                    readOnly: readOnly,
                    required: required,
                    attributes: {
                        'min': field.min,
                        'max': field.max,
                        'step': field.step,
                        'data-bs-toggle': 'tooltip',
                        'data-bs-placement': 'top',
                        title: tooltip
                    },
                    parent: type === 'password' || (type === 'text' && field.id === 'system_api_key') ? inputGroupDiv : formGroupDiv
                });
                break;
            case 'select':
                inputElement = this.createElement('select', {
                    id: fieldId,
                    name: field.id,
                    className: 'form-control',
                    required: required,
                    attributes: {
                        'data-bs-toggle': 'tooltip',
                        'data-bs-placement': 'top',
                        title: tooltip
                    },
                    parent: formGroupDiv
                });
                options.forEach(option => {
                    let fieldValueString = fieldValue.toString();
                    if (fieldValue === true) {
                        fieldValueString = '1';
                    } else if (fieldValue === false) {
                        fieldValueString = '0';
                    }
                    this.createElement('option', {
                        value: option.value,
                        textContent: option.text,
                        selected: fieldValueString === option.value,
                        parent: inputElement
                    });
                });
                break;
            // Add other input types here if necessary
        }

        if (type === 'password') {
            this.createElement('button', {
                type: 'button',
                className: 'btn btn-outline-success',
                innerHTML: '<i class="fa-regular fa-eye"></i>',
                onClick: function () {
                    inputElement.type = inputElement.type === 'password' ? 'text' : 'password';
                    this.innerHTML = inputElement.type === 'text' ? '<i class="fa-solid fa-eye-slash"></i>' : '<i class="fa-regular fa-eye"></i>';
                },
                parent: inputGroupDiv
            });
        } else if (type === 'text' && field.id === 'system_api_key'){
            this.createElement('button', {
                className: 'btn btn-outline-warning',
                type: 'button',
                attributes: {
                    'data-bs-toggle': 'tooltip',
                    'data-bs-placement': 'top',
                    title: 'Regenerate API Key'
                },
                innerHTML: '<i class="fas fa-sync-alt"></i>',
                onClick: function () {
                    inputElement.value = ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
                        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));
                },
                parent: inputGroupDiv
            });
        }

        // Special handling for system_api_key with regenerate button


        // Append inputGroupDiv to formGroupDiv if it has children and hasn't been appended already
        if (!inputGroupDiv.parentNode && inputGroupDiv.hasChildNodes()) {
            formGroupDiv.appendChild(inputGroupDiv);
        }
    }


    showAlert(message, type) {
        console.log(message)
        const bgClass = {
            success: 'bg-success',
            warning: 'bg-warning',
            info: 'bg-info',
            danger: 'bg-danger'
        };

        const toastHtml = `<div class="toast align-items-center text-white border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="5000">
                                    <div class="d-flex ${bgClass[type] || 'bg-primary'}">
                                      <div class="toast-body">
                                        ${message}
                                      </div>
                                      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                                    </div>
                                  </div>`;

        this.toast_container.insertAdjacentHTML('beforeend', toastHtml);

        const toastEl = this.toast_container.lastElementChild;
        const toast = new bootstrap.Toast(toastEl);
        toast.show();

        // The toast will automatically hide after 5 seconds due to data-bs-autohide and data-bs-delay
    }

}