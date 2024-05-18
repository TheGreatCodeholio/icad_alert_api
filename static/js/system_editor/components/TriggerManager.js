export class TriggerManager {
    constructor() {
        this.region = window.region;
    }

    renderTriggersPage(UIManager, system_data, filter_data) {
        console.log(system_data)
        UIManager.trigger_title.innerText = `${system_data.system_name} Triggers`
        UIManager.trigger_form_system_id.value = system_data.system_id
        // UIManager.new_trigger_button.onclick = () => {
        //     this.triggerPostForm(UIManager, '/admin/add_trigger', 'addTriggerForm')
        // }

        let triggers_data = system_data.alert_triggers

        triggers_data.forEach(trigger_data => {
            this.addTriggerToPage(UIManager, trigger_data, filter_data)
        });

    }

    addTriggerToPage(UIManager, trigger_data, filter_data) {
        if (!trigger_data) {
            return
        }

        console.log(trigger_data)

        //Add System Links to Sidebar
        const triggerListItem = UIManager.createElement('li', {className: 'mb-1', parent: UIManager.trigger_menu});

        const triggerButton = UIManager.createElement('button', {
            className: 'btn btn-toggle d-inline-flex align-items-center rounded border-0 collapsed',
            attributes: {
                'data-bs-toggle': 'collapse',
                'data-bs-target': `#trigger_${trigger_data.trigger_id}-collapse`,
                'aria-expanded': 'false'
            },
            textContent: trigger_data.trigger_name,
            parent: triggerListItem
        });

        const triggerButtonCollapse = UIManager.createElement('div', {
            id: `trigger_${trigger_data.trigger_id}-collapse`,
            className: 'collapse',
            parent: triggerListItem
        });

        const triggerMenuCollapse = UIManager.createElement('ul', {
            className: 'btn-toggle-nav list-unstyled fw-normal pb-1 small',
            parent: triggerButtonCollapse
        });

        // Define the submenu items
        const submenuItems = [
            {id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_general-tab`, text: 'General'},
            {id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_two_tone-tab`, text: 'Two Tone'},
            {id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_long_tone-tab`, text: 'Long Tone'},
            {id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_hi_low_tone-tab`, text: 'Hi/Low Tone'},
            {id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_transcript_filter-tab`, text: 'Filter'},
            {id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-tab`, text: 'Email'},
            {id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_pushover-tab`, text: 'Pushover'},
            {id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook-tab`, text: 'Webhooks'}
        ];

        // Create menu items dynamically
        submenuItems.forEach(item => {
            this.triggerCreateMenuItem(UIManager, triggerMenuCollapse, item.id, item.text, item.id);
        });

        const triggerGeneralTabContent = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_general-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'aria-labelledby': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_general-tab`,
                'tabindex': "0"
            },
            parent: UIManager.trigger_content
        })

        this.triggerCreateGeneralPage(UIManager, triggerGeneralTabContent, trigger_data)


        const triggerTwoToneTabContent = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_two_tone-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_two_tone-tab`,
                'tabindex': "0"
            },
            parent: UIManager.trigger_content
        })

        this.triggerCreateTwoTonePage(UIManager, triggerTwoToneTabContent, trigger_data)

        const triggerLongToneTabContent = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_long_tone-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_long_tone-tab`,
                'tabindex': "0"
            },
            parent: UIManager.trigger_content
        })

        this.triggerCreateLongTonePage(UIManager, triggerLongToneTabContent, trigger_data)

        const triggerHiLowToneTabContent = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_hi_low_tone-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_hi_low_long_tone-tab`,
                'tabindex': "0"
            },
            parent: UIManager.trigger_content
        })

        this.triggerCreateHiLowTonePage(UIManager, triggerHiLowToneTabContent, trigger_data)

        const triggerTranscriptFilterTabContent = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_transcript_filter-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_transcript_filter-tab`,
                'tabindex': "0"
            },
            parent: UIManager.trigger_content
        })

        this.triggerCreateTranscriptFilterPage(UIManager, triggerTranscriptFilterTabContent, trigger_data, filter_data)

        const triggerEmailsTabContent = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_email-tab`,
                'tabindex': "0"
            },
            parent: UIManager.trigger_content
        })

        this.triggerCreateEmailAddressesPage(UIManager, triggerEmailsTabContent, trigger_data)

        const triggerPushoverTabContent = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_pushover-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_pushover-tab`,
                'tabindex': "0"
            },
            parent: UIManager.trigger_content
        })

        this.triggerCreatePushoverPage(UIManager, triggerPushoverTabContent, trigger_data)

        const triggerWebhookTabContent = UIManager.createElement('div', {
            id: `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `trigger_${trigger_data.system_id}_${trigger_data.trigger_id}_webhook-tab`,
                'tabindex': "0"
            },
            parent: UIManager.trigger_content
        })

        this.triggerCreateWebhookPage(UIManager, triggerWebhookTabContent, trigger_data)

    }

    triggerCreateMenuItem(UIManager, parent, id, text, target) {
        let listItem = UIManager.createElement('li', {parent: parent});
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
    }

    triggerCreateGeneralPage(UIManager, generalElement, trigger_data) {
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "General Config",
            parent: generalElement
        });

        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `trigger_general_form_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            parent: generalElement
        });

        let inputFields = [
            {
                id: `system_id`,
                label: 'System ID',
                tooltip: 'ID of the system this trigger belongs to. (read only)',
                type: 'number',
                value: trigger_data.system_id,
                col_class: 'col-md-6',
                readOnly: true
            },
            {
                id: `trigger_id`,
                label: 'Trigger ID',
                tooltip: 'ID of this trigger. (read only)',
                type: 'number',
                value: trigger_data.trigger_id,
                col_class: 'col-md-6',
                readOnly: true
            },
            {
                id: `trigger_name`,
                label: 'Trigger Name',
                tooltip: 'Name Of this trigger.',
                type: 'text',
                value: trigger_data.trigger_name,
                col_class: 'col-md-6',
            },
            {
                id: 'tone_tolerance',
                label: 'Tone Tolerance (%)',
                tooltip: 'Tolerance for tone detection percent represented by a whole number',
                type: 'number',
                value: trigger_data.tone_tolerance || 2,
                col_class: 'col-md-6'
            },
            {
                id: 'ignore_time',
                label: 'Ignore Time (s)',
                tooltip: 'Time to ignore in seconds after trigger activated.',
                type: 'number',
                step: 0.1,
                value: trigger_data.ignore_time || 300,
                col_class: 'col-md-6'
            },
            {
                id: 'trigger_stream_url',
                label: 'Trigger Stream URL',
                tooltip: 'URL for the trigger stream',
                type: 'url',
                value: trigger_data.trigger_stream_url,
                placeholder: 'https://scanner.ccfirewire.com',
                col_class: 'col-md-6'
            }

        ];

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, trigger_data.trigger_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        // Checkbox for Enabled status
        const checkFacebookDiv = document.createElement('div');
        checkFacebookDiv.className = 'mb-3 form-check form-switch text-end';
        formSubmitCol.appendChild(checkFacebookDiv);

        const enabledFacebookCheckbox = document.createElement('input');
        enabledFacebookCheckbox.type = 'checkbox';
        enabledFacebookCheckbox.name = 'enable_facebook';
        enabledFacebookCheckbox.className = 'form-check-input me-2';
        enabledFacebookCheckbox.role = 'switch';
        enabledFacebookCheckbox.id = `enabled_facebook_${trigger_data.system_id}_${trigger_data.trigger_id}`;
        enabledFacebookCheckbox.checked = trigger_data.enable_facebook;
        checkFacebookDiv.appendChild(enabledFacebookCheckbox);

        const enabledFacebookLabel = document.createElement('label');
        enabledFacebookLabel.className = 'form-check-label';
        enabledFacebookLabel.setAttribute('for', `enabled_facebook_${trigger_data.system_id}_${trigger_data.trigger_id}`);
        enabledFacebookLabel.textContent = trigger_data.enabled ? 'Facebook Enabled' : 'Facebook Disabled';
        checkFacebookDiv.appendChild(enabledFacebookLabel);

        // Event listener for changing label text upon toggle
        enabledFacebookCheckbox.addEventListener('change', function() {
            enabledFacebookLabel.textContent = this.checked ? 'Facebook Enabled' : 'Facebook Disabled';
        });

        // Checkbox for Enabled status
        const checkTelegramDiv = document.createElement('div');
        checkTelegramDiv.className = 'mb-3 form-check form-switch text-end';
        formSubmitCol.appendChild(checkTelegramDiv);

        const enabledTelegramCheckbox = document.createElement('input');
        enabledTelegramCheckbox.type = 'checkbox';
        enabledTelegramCheckbox.name = 'enable_telegram';
        enabledTelegramCheckbox.className = 'form-check-input me-2';
        enabledTelegramCheckbox.role = 'switch';
        enabledTelegramCheckbox.id = `enabled_telegram_${trigger_data.system_id}_${trigger_data.trigger_id}`;
        enabledTelegramCheckbox.checked = trigger_data.enable_telegram;
        checkTelegramDiv.appendChild(enabledTelegramCheckbox);

        const enabledTelegramLabel = document.createElement('label');
        enabledTelegramLabel.className = 'form-check-label';
        enabledTelegramLabel.setAttribute('for', `enabled_telegram_${trigger_data.system_id}_${trigger_data.trigger_id}`);
        enabledTelegramLabel.textContent = trigger_data.enabled ? 'Telegram Enabled' : 'Telegram Disabled';
        checkTelegramDiv.appendChild(enabledTelegramLabel);

        // Event listener for changing label text upon toggle
        enabledTelegramCheckbox.addEventListener('change', function() {
            enabledTelegramLabel.textContent = this.checked ? 'Telegram Enabled' : 'Telegram Disabled';
        });

        // Checkbox for Enabled status
        const checkDiv = document.createElement('div');
        checkDiv.className = 'mb-3 form-check form-switch text-end';
        formSubmitCol.appendChild(checkDiv);

        const enabledCheckbox = document.createElement('input');
        enabledCheckbox.type = 'checkbox';
        enabledCheckbox.name = 'enabled';
        enabledCheckbox.className = 'form-check-input me-2';
        enabledCheckbox.role = 'switch';
        enabledCheckbox.id = `enabled_trigger_${trigger_data.system_id}_${trigger_data.trigger_id}`;
        enabledCheckbox.checked = trigger_data.enabled;
        checkDiv.appendChild(enabledCheckbox);

        const enabledLabel = document.createElement('label');
        enabledLabel.className = 'form-check-label';
        enabledLabel.setAttribute('for', `enabled_trigger_${trigger_data.system_id}_${trigger_data.trigger_id}`);
        enabledLabel.textContent = trigger_data.enabled ? 'Trigger Enabled' : 'Trigger Disabled'; // Set initial label text based on the checkbox state
        checkDiv.appendChild(enabledLabel);

        // Event listener for changing label text upon toggle
        enabledCheckbox.addEventListener('change', function() {
            enabledLabel.textContent = this.checked ? 'Trigger Enabled' : 'Trigger Disabled';
        });

        const saveTriggerButton = UIManager.createElement('button', {
            id: `triggerSaveGeneral_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            className: "btn btn-md btn-success me-2",
            attributes: {
                "data-system-id": trigger_data.system_id,
                "data-trigger-id": trigger_data.trigger_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button'
        });

        saveTriggerButton.onclick = () => {
            this.triggerPostForm(UIManager, `${UIManager.baseUrl}/admin/save_trigger_general`, `trigger_general_form_${trigger_data.system_id}_${trigger_data.trigger_id}`)
        }

        const deleteTriggerButton = UIManager.createElement('button', {
            id: `deleteTrigger_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            className: "btn btn-md btn-danger",
            attributes: {
                "data-system-id": trigger_data.system_id,
                "data-trigger-id": trigger_data.trigger_id
            },
            textContent: "Delete",
            parent: formSubmitCol,
            type: 'button',
            name: 'delete_trigger'
        });
        deleteTriggerButton.onclick = () => {
            this.triggerDeleteAction(UIManager, trigger_data.system_id, trigger_data.trigger_id, trigger_data.trigger_name)
        }

    }

    triggerCreateTwoTonePage(UIManager, twoToneElement, trigger_data){
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Two Tone Config",
            parent: twoToneElement
        });

        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `trigger_two_tone_form_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            parent: twoToneElement
        });

        let inputFields = [
            {
                id: `system_id`,
                label: 'System ID',
                tooltip: 'ID of the system this trigger belongs to. (read only)',
                type: 'number',
                value: trigger_data.system_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_id`,
                label: 'Trigger ID',
                tooltip: 'ID of this trigger. (read only)',
                type: 'number',
                value: trigger_data.trigger_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_name`,
                label: 'Trigger Name',
                tooltip: 'Name Of this trigger.',
                type: 'text',
                value: trigger_data.trigger_name,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: 'two_tone_a',
                label: 'Two Tone A',
                tooltip: 'Two Tone A in HZ',
                type: 'number',
                step: .1,
                value: trigger_data.two_tone_a,
                col_class: 'col-md-6'
            },
            {
                id: 'two_tone_a_length',
                label: 'Two Tone A Length',
                tooltip: 'Two Tone A Length in seconds',
                type: 'number',
                step: 1,
                value: trigger_data.two_tone_a_length,
                col_class: 'col-md-6'
            },
            {
                id: 'two_tone_b',
                label: 'Two Tone B',
                tooltip: 'Two Tone B in HZ',
                type: 'number',
                step: .1,
                value: trigger_data.two_tone_b,
                col_class: 'col-md-6'
            },
            {
                id: 'two_tone_b_length',
                label: 'Two Tone B Length',
                tooltip: 'Two Tone B Length in seconds.',
                type: 'number',
                step: 1,
                value: trigger_data.two_tone_b_length,
                col_class: 'col-md-6'
            }
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, trigger_data.trigger_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveTriggerButton = UIManager.createElement('button', {
            id: `triggerSaveTwoTone_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            className: "btn btn-md btn-success me-2",
            attributes: {
                "data-system-id": trigger_data.system_id,
                "data-trigger-id": trigger_data.trigger_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button'
        });

        saveTriggerButton.onclick = () => {
            this.triggerPostForm(UIManager, '/admin/save_trigger_two_tone', `trigger_two_tone_form_${trigger_data.system_id}_${trigger_data.trigger_id}`)
        }

    }

    triggerCreateLongTonePage(UIManager, longToneElement, trigger_data){
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Long Tone Config",
            parent: longToneElement
        });

        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `trigger_long_tone_form_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            parent: longToneElement
        });

        let inputFields = [
            {
                id: `system_id`,
                label: 'System ID',
                tooltip: 'ID of the system this trigger belongs to. (read only)',
                type: 'number',
                value: trigger_data.system_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_id`,
                label: 'Trigger ID',
                tooltip: 'ID of this trigger. (read only)',
                type: 'number',
                value: trigger_data.trigger_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_name`,
                label: 'Trigger Name',
                tooltip: 'Name Of this trigger.',
                type: 'text',
                value: trigger_data.trigger_name,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: 'long_tone',
                label: 'Long Tone',
                tooltip: 'Long Tone in HZ',
                type: 'number',
                step: .1,
                value: trigger_data.long_tone,
                col_class: 'col-md-6'
            },
            {
                id: 'long_tone_length',
                label: 'Long Tone Length',
                tooltip: 'Long Tone Length in seconds',
                type: 'number',
                step: 1,
                value: trigger_data.long_tone_length,
                col_class: 'col-md-6'
            }
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, trigger_data.trigger_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveTriggerButton = UIManager.createElement('button', {
            id: `triggerSaveLongTone_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            className: "btn btn-md btn-success me-2",
            attributes: {
                "data-system-id": trigger_data.system_id,
                "data-trigger-id": trigger_data.trigger_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button'
        });

        saveTriggerButton.onclick = () => {
            this.triggerPostForm(UIManager, '/admin/save_trigger_long_tone', `trigger_long_tone_form_${trigger_data.system_id}_${trigger_data.trigger_id}`)
        }

    }

    triggerCreateHiLowTonePage(UIManager, HiLowToneElement, trigger_data){
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Hi Low Tone Config",
            parent: HiLowToneElement
        });

        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `trigger_hi_low_tone_form_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            parent: HiLowToneElement
        });

        let inputFields = [
            {
                id: `system_id`,
                label: 'System ID',
                tooltip: 'ID of the system this trigger belongs to. (read only)',
                type: 'number',
                value: trigger_data.system_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_id`,
                label: 'Trigger ID',
                tooltip: 'ID of this trigger. (read only)',
                type: 'number',
                value: trigger_data.trigger_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_name`,
                label: 'Trigger Name',
                tooltip: 'Name Of this trigger.',
                type: 'text',
                value: trigger_data.trigger_name,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: 'hi_low_tone_a',
                label: 'Hi Low Tone A',
                tooltip: 'Hi Low Tone A in HZ',
                type: 'number',
                step: .1,
                value: trigger_data.hi_low_tone_a,
                col_class: 'col-md-6'
            },
            {
                id: 'hi_low_tone_b',
                label: 'Hi Low Tone B',
                tooltip: 'Hi Low Tone B in HZ',
                type: 'number',
                step: .1,
                value: trigger_data.hi_low_tone_b,
                col_class: 'col-md-6'
            },
            {
                id: 'hi_low_alternations',
                label: 'Hi Low Tone Alternations',
                tooltip: 'Hi Low Tone Minimum Alternations',
                type: 'number',
                step: 1,
                value: trigger_data.hi_low_alternations,
                col_class: 'col-md-6'
            }
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, trigger_data.trigger_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveTriggerButton = UIManager.createElement('button', {
            id: `triggerSaveHiLowTone_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            className: "btn btn-md btn-success me-2",
            attributes: {
                "data-system-id": trigger_data.system_id,
                "data-trigger-id": trigger_data.trigger_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button'
        });

        saveTriggerButton.onclick = () => {
            this.triggerPostForm(UIManager, '/admin/save_trigger_hi_low_tone', `trigger_hi_low_tone_form_${trigger_data.system_id}_${trigger_data.trigger_id}`)
        }

    }

    triggerCreateTranscriptFilterPage(UIManager, transcriptFilterElement, trigger_data, filter_data){
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Transcript Filter Config",
            parent: transcriptFilterElement
        });

        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `trigger_alert_filter_form_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            parent: transcriptFilterElement
        });

        let filterOptions = [{text: "Select Filter", value: "0"}];
        filter_data.forEach(item => {
            const newFilterOption = {
                text: item.alert_filter_name,
                value: item.alert_filter_id
            }
            filterOptions.push(newFilterOption)
        });
        filterOptions.push({text: "None", value: "0"})

        let inputFields = [
            {
                id: `system_id`,
                label: 'System ID',
                tooltip: 'ID of the system this trigger belongs to. (read only)',
                type: 'number',
                value: trigger_data.system_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_id`,
                label: 'Trigger ID',
                tooltip: 'ID of this trigger. (read only)',
                type: 'number',
                value: trigger_data.trigger_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_name`,
                label: 'Trigger Name',
                tooltip: 'Name Of this trigger.',
                type: 'text',
                value: trigger_data.trigger_name,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `alert_filter_id`,
                label: 'Alert Filter',
                tooltip: 'The Alert Filter to use for transcripts',
                type: 'select',
                value: trigger_data.alert_filter_id || "",
                col_class: 'col-4',
                options: filterOptions
            }
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, trigger_data.trigger_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveTriggerButton = UIManager.createElement('button', {
            id: `triggerSaveAlertFilter_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            className: "btn btn-md btn-success me-2",
            attributes: {
                "data-system-id": trigger_data.system_id,
                "data-trigger-id": trigger_data.trigger_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button'
        });

        saveTriggerButton.onclick = () => {
            this.triggerPostForm(UIManager, '/admin/save_trigger_alert_filter', `trigger_alert_filter_form_${trigger_data.system_id}_${trigger_data.trigger_id}`)
        }

    }
    triggerCreateEmailAddressesPage(UIManager, emailAddressElement, trigger_data) {
        UIManager.EmailAddressManager.renderTriggerEmails(UIManager, emailAddressElement, trigger_data)
    }

    triggerCreatePushoverPage(UIManager, pushoverElement, trigger_data){
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Pushover Config",
            parent: pushoverElement
        });

        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `trigger_pushover_form_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            parent: pushoverElement
        });

        let inputFields = [
            {
                id: `system_id`,
                label: 'System ID',
                tooltip: 'ID of the system this trigger belongs to. (read only)',
                type: 'number',
                value: trigger_data.system_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_id`,
                label: 'Trigger ID',
                tooltip: 'ID of this trigger. (read only)',
                type: 'number',
                value: trigger_data.trigger_id,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: `trigger_name`,
                label: 'Trigger Name',
                tooltip: 'Name Of this trigger.',
                type: 'text',
                value: trigger_data.trigger_name,
                col_class: 'd-none',
                readOnly: true
            },
            {
                id: 'pushover_group_token',
                label: 'Pushover Group Token',
                tooltip: 'Pushover Group Token',
                type: 'text',
                value: trigger_data.pushover_group_token,
                col_class: 'col-md-6'
            },
            {
                id: 'pushover_app_token',
                label: 'Pushover App Token',
                tooltip: 'Pushover App Token',
                type: 'text',
                value: trigger_data.pushover_app_token,
                col_class: 'col-md-6'
            },
            {
                id: 'pushover_subject_token',
                label: 'Pushover Alert Subject',
                tooltip: 'Pushover Subject',
                type: 'text',
                value: trigger_data.pushover_subject,
                col_class: 'col-md-6'
            },
            {
                id: 'pushover_sound',
                label: 'Pushover Alert Sound',
                tooltip: 'Pushover Sound',
                type: 'text',
                value: trigger_data.pushover_sound,
                col_class: 'col-md-6'
            },
            {
                id: 'pushover_body',
                label: 'Pushover Alert Body',
                tooltip: 'Pushover Alert Body',
                type: 'text',
                value: trigger_data.pushover_body,
                col_class: 'col-md-12'
            }
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, trigger_data.trigger_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveTriggerButton = UIManager.createElement('button', {
            id: `triggerSavePushover_${trigger_data.system_id}_${trigger_data.trigger_id}`,
            className: "btn btn-md btn-success me-2",
            attributes: {
                "data-system-id": trigger_data.system_id,
                "data-trigger-id": trigger_data.trigger_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button'
        });

        saveTriggerButton.onclick = () => {
            this.triggerPostForm(UIManager, '/admin/save_trigger_pushover', `trigger_pushover_form_${trigger_data.system_id}_${trigger_data.trigger_id}`)
        }

    }

    triggerCreateWebhookPage(UIManager, webhookElement, trigger_data){
        UIManager.WebhookManager.triggerRenderWebhooks(UIManager, webhookElement, trigger_data);
    }
    triggerPostForm(UIManager, save_url, form_id) {
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

    triggerDeleteAction(UIManager, system_id, trigger_id, trigger_name) {
        const triggerData = {"system_id": system_id, "trigger_id": trigger_id, "trigger_name": trigger_name};
        const save_url = `${UIManager.baseUrl}/admin/delete_trigger`;
        fetch(save_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(triggerData)
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