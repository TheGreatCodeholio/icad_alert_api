export class SystemManager {
    constructor() {
        this.region = window.region;
    }

    addSystemToPage(UIManager, system_data) {
        if (!system_data) {
            return
        }

        //Add System Links to Sidebar
        const systemListItem = UIManager.createElement('li', {className: 'mb-1', parent: UIManager.system_menu});

        const systemButton = UIManager.createElement('button', {
            className: 'btn btn-toggle d-inline-flex align-items-center rounded border-0 collapsed',
            attributes: {
                'data-bs-toggle': 'collapse',
                'data-bs-target': `#system_${system_data.system_id}-collapse`,
                'aria-expanded': 'false'
            },
            textContent: system_data.system_name,
            parent: systemListItem
        });

        const systemButtonCollapse = UIManager.createElement('div', {
            id: `system_${system_data.system_id}-collapse`,
            className: 'collapse',
            parent: systemListItem
        });

        const systemMenuCollapse = UIManager.createElement('ul', {
            className: 'btn-toggle-nav list-unstyled fw-normal pb-1 small',
            parent: systemButtonCollapse
        });

        // Define the submenu items
        const submenuItems = [
            {id: `system_${system_data.system_id}_general-tab`, text: 'General', link: ''},
            {id: `system_${system_data.system_id}_email-settings-tab`, text: 'Email Settings', link: ''},
            {id: `system_${system_data.system_id}_email-tab`, text: 'Email Addresses', link: ''},
            {id: `system_${system_data.system_id}_pushover-tab`, text: 'Pushover', link: ''},
            {id: `system_${system_data.system_id}_facebook-tab`, text: 'Facebook', link: ''},
            {id: `system_${system_data.system_id}_telegram-tab`, text: 'Telegram', link: ''},
            {id: `system_${system_data.system_id}_webhook-tab`, text: 'Webhooks', link: ''},
            {id: `system_${system_data.system_id}_trigger-tab`, text: 'Triggers', link: `${UIManager.baseUrl}/admin/triggers?system_id=${system_data.system_id}`}
        ];

        // Create menu items dynamically
        submenuItems.forEach(item => {
            this.systemCreateMenuItem(UIManager, systemMenuCollapse, item.id, item.text, item.link);
        });

        const systemGeneralTabContent = UIManager.createElement('div', {
            id: `system_${system_data.system_id}_general-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `system_${system_data.system_id}_general-tab`,
                'tabindex': "0"
            },
            parent: UIManager.system_content
        })

        this.systemCreateGeneralPage(UIManager, systemGeneralTabContent, system_data)

        const systemEmailTabContent = UIManager.createElement('div', {
            id: `system_${system_data.system_id}_email-settings-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `system_${system_data.system_id}_email-settings-tab`,
                'tabindex': "0"
            },
            parent: UIManager.system_content
        })

        this.systemCreateEmailSettingsPage(UIManager, systemEmailTabContent, system_data)

        const systemEmailAddressesTabContent = UIManager.createElement('div', {
            id: `system_${system_data.system_id}_email-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `system_${system_data.system_id}_email-tab`,
                'tabindex': "0"
            },
            parent: UIManager.system_content
        })

        this.systemCreateEmailAddressesPage(UIManager, systemEmailAddressesTabContent, system_data)

        const systemPushoverTabContent = UIManager.createElement('div', {
            id: `system_${system_data.system_id}_pushover-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `system_${system_data.system_id}_pushover-tab`,
                'tabindex': "0"
            },
            parent: UIManager.system_content
        })

        this.systemCreatePushoverPage(UIManager, systemPushoverTabContent, system_data)

        const systemFacebookTabContent = UIManager.createElement('div', {
            id: `system_${system_data.system_id}_facebook-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `system_${system_data.system_id}_facebook-tab`,
                'tabindex': "0"
            },
            parent: UIManager.system_content
        })

        this.systemCreateFacebookPage(UIManager, systemFacebookTabContent, system_data)

        const systemTelegramTabContent = UIManager.createElement('div', {
            id: `system_${system_data.system_id}_telegram-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'role': '',
                'aria-labelledby': `system_${system_data.system_id}_telegram-tab`,
                'tabindex': "0"
            },
            parent: UIManager.system_content
        })

        this.systemCreateTelegramPage(UIManager, systemTelegramTabContent, system_data)

        const systemWebhookTabContent = UIManager.createElement('div', {
            id: `system_${system_data.system_id}_webhook-tab-pane`,
            className: 'tab-pane fade',
            attributes: {
                'aria-labelledby': `system_${system_data.system_id}_webhook-tab`,
                'tabindex': "0"
            },
            parent: UIManager.system_content
        })

        this.systemCreateWebhookPage(UIManager, systemWebhookTabContent, system_data)

    }

    systemCreateMenuItem(UIManager, parent, id, text, link) {
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

    systemCreateGeneralPage(UIManager, generalElement, system_data) {

        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "General Config",
            parent: generalElement
        })

        // Form to Edit General System
        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `system_general_form_${system_data.system_id}`,
            parent: generalElement
        });

        UIManager.createElement('input', {
            type: "hidden",
            value: system_data.system_id,
            name: 'system_id',
            parent: form
        })

        UIManager.createElement('input', {
            type: "hidden",
            value: system_data.system_short_name,
            name: 'system_short_name_orig',
            parent: form
        })

        let inputFields = [
            {
                label: 'System ID:',
                id: 'system_id',
                type: 'text',
                value: system_data.system_id,
                readOnly: true,
                tooltip: 'System Identifier',
                col_class: 'col-4',

            },
            {
                label: 'Short Name:',
                id: 'system_short_name',
                type: 'text',
                value: system_data.system_short_name,
                tooltip: 'Shortened System Name (No Spaces)',
                col_class: 'col-8',
                required: true
            },
            {
                label: 'System Name:',
                id: 'system_name',
                type: 'text',
                value: system_data.system_name,
                tooltip: 'Name of the System',
                col_class: 'col-6'
            },
            {
                label: 'System County:',
                id: 'system_county',
                type: 'text',
                value: system_data.system_county,
                tooltip: 'County of the System',
                col_class: 'col-6'
            },
        ];
        if (this.region === "US") {
            inputFields.push({
                    label: 'System State:',
                    id: 'system_state',
                    type: 'select',
                    options: [
                        {value: '', text: 'State'},
                        {value: 'AL', text: 'Alabama'},
                        {value: 'AK', text: 'Alaska'},
                        {value: 'AZ', text: 'Arizona'},
                        {value: 'AR', text: 'Arkansas'},
                        {value: 'CA', text: 'California'},
                        {value: 'CO', text: 'Colorado'},
                        {value: 'CT', text: 'Connecticut'},
                        {value: 'DE', text: 'Delaware'},
                        {value: 'FL', text: 'Florida'},
                        {value: 'GA', text: 'Georgia'},
                        {value: 'HI', text: 'Hawaii'},
                        {value: 'ID', text: 'Idaho'},
                        {value: 'IL', text: 'Illinois'},
                        {value: 'IN', text: 'Indiana'},
                        {value: 'IA', text: 'Iowa'},
                        {value: 'KS', text: 'Kansas'},
                        {value: 'KY', text: 'Kentucky'},
                        {value: 'LA', text: 'Louisiana'},
                        {value: 'ME', text: 'Maine'},
                        {value: 'MD', text: 'Maryland'},
                        {value: 'MA', text: 'Massachusetts'},
                        {value: 'MI', text: 'Michigan'},
                        {value: 'MN', text: 'Minnesota'},
                        {value: 'MS', text: 'Mississippi'},
                        {value: 'MO', text: 'Missouri'},
                        {value: 'MT', text: 'Montana'},
                        {value: 'NE', text: 'Nebraska'},
                        {value: 'NV', text: 'Nevada'},
                        {value: 'NH', text: 'New Hampshire'},
                        {value: 'NJ', text: 'New Jersey'},
                        {value: 'NM', text: 'New Mexico'},
                        {value: 'NY', text: 'New York'},
                        {value: 'NC', text: 'North Carolina'},
                        {value: 'ND', text: 'North Dakota'},
                        {value: 'OH', text: 'Ohio'},
                        {value: 'OK', text: 'Oklahoma'},
                        {value: 'OR', text: 'Oregon'},
                        {value: 'PA', text: 'Pennsylvania'},
                        {value: 'RI', text: 'Rhode Island'},
                        {value: 'SC', text: 'South Carolina'},
                        {value: 'SD', text: 'South Dakota'},
                        {value: 'TN', text: 'Tennessee'},
                        {value: 'TX', text: 'Texas'},
                        {value: 'UT', text: 'Utah'},
                        {value: 'VT', text: 'Vermont'},
                        {value: 'VA', text: 'Virginia'},
                        {value: 'WA', text: 'Washington'},
                        {value: 'WV', text: 'West Virginia'},
                        {value: 'WI', text: 'Wisconsin'},
                        {value: 'WY', text: 'Wyoming'}
                    ],
                    value: system_data.system_state,
                    tooltip: 'State of the System',
                    col_class: 'col-6'
                },
                {
                    label: 'System FIPS:',
                    id: 'system_fips',
                    type: 'text',
                    value: system_data.system_fips,
                    tooltip: 'FIPS Code for the System',
                    col_class: 'col-6'
                },);
        } else if (this.region === "CA") {
            inputFields.push({
                    label: 'System Province:',
                    id: 'system_state',
                    type: 'select',
                    options: [
                        {value: '', text: 'Province'},
                        {value: 'AB', text: 'Alberta'},
                        {value: 'BC', text: 'British Columbia'},
                        {value: 'MB', text: 'Manitoba'},
                        {value: 'NB', text: 'New Brunswick'},
                        {value: 'NL', text: 'Newfoundland and Labrador'},
                        {value: 'NS', text: 'Nova Scotia'},
                        {value: 'ON', text: 'Ontario'},
                        {value: 'PE', text: 'Prince Edward Island'},
                        {value: 'QC', text: 'Quebec'},
                        {value: 'SK', text: 'Saskatchewan'},
                        {value: 'NT', text: 'Northwest Territories'},
                        {value: 'NU', text: 'Nunavut'},
                        {value: 'YT', text: 'Yukon'}
                    ],
                    value: system_data.system_state,
                    tooltip: 'Province of the System',
                    col_class: 'col-6',
                },
                {
                    label: 'System SGC:',
                    id: 'system_fips',
                    type: 'text',
                    value: system_data.system_fips,
                    tooltip: 'SCG Code for the System',
                    col_class: 'col-6'
                },);
        }

        inputFields.push(
            {
                label: 'System API Key:',
                id: 'system_api_key',
                type: 'text',
                value: system_data.system_api_key,
                readOnly: true,
                tooltip: 'Your System API Key',
                regenerate: true,
                col_class: 'col-6'
            },
            {
                label: 'System Stream URL:',
                id: 'stream_url',
                type: 'text',
                value: system_data.stream_url,
                readOnly: false,
                tooltip: 'The URL where you can listen to the System Stream',
                col_class: 'col-6'
            }
        )

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, system_data.system_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveSystemButton = UIManager.createElement('button', {
            id: `systemSaveGeneral_${system_data.system_id}`,
            className: "btn btn-md btn-success me-2",
            attributes: {
                "data-system-id": system_data.system_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button'
        });

        saveSystemButton.onclick = () => {
            this.systemPostForm(UIManager, '/admin/save_system_general', `system_general_form_${system_data.system_id}`)
        }


        const deleteSystemButton = UIManager.createElement('button', {
            id: `deleteSystem_${system_data.system_id}`,
            className: "btn btn-md btn-danger",
            attributes: {
                "data-system-id": system_data.system_id
            },
            textContent: "Delete",
            parent: formSubmitCol,
            type: 'button',
            name: 'delete_system'
        });
        deleteSystemButton.onclick = () => {
            this.systemDeleteAction(UIManager, system_data.system_id, system_data.system_name, system_data.system_short_name)
        }
    }

    systemCreateEmailSettingsPage(UIManager, emailElement, system_data) {
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Email Config",
            parent: emailElement
        })

        // Form to Edit System Email Settings
        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `system_email_edit_form_${system_data.system_id}`,
            parent: emailElement
        });

        UIManager.createElement('input', {
            type: "hidden",
            name: 'system_id',
            value: system_data.system_id,
            parent: form
        })

        let inputFields = [
            {
                label: 'Enable Emails',
                id: 'email_enabled',
                tooltip: 'Enable/Disable sending alerts via Email.',
                type: 'select',
                col_class: 'col-4',
                value: system_data.email_enabled,
                options: [{value: '1', text: 'Enabled'}, {value: '0', text: 'Disabled', selected: true}]
            },
            {
                label: 'SMTP Host',
                id: 'smtp_hostname',
                tooltip: 'Hostname for SMTP Server',
                type: 'text',
                col_class: 'col-8',
                value: system_data.smtp_hostname
            },
            {
                label: 'SMTP Port',
                id: 'smtp_port',
                tooltip: 'SMTP Server Port',
                type: 'text',
                col_class: 'col-6',
                value: system_data.smtp_port
            },
            {
                label: 'SMTP Username',
                id: 'smtp_username',
                tooltip: 'Username for SMTP Server',
                type: 'text',
                col_class: 'col-6',
                value: system_data.smtp_username
            },
            {
                label: 'SMTP Password',
                id: 'smtp_password',
                tooltip: 'SMTP User\'s Password',
                type: 'password',
                col_class: 'col-6',
                value: system_data.smtp_password
            },
            {
                label: 'Email Address',
                id: 'email_address_from',
                tooltip: 'Email Address To Send Email From: icad@example.com',
                type: 'text',
                col_class: 'col-6',
                value: system_data.email_address_from
            },
            {
                label: 'Email Name',
                id: 'email_text_from',
                tooltip: 'Name To Use When Sending Email: iCAD Dispatch',
                type: 'text',
                col_class: 'col-6',
                value: system_data.email_text_from
            },
            {
                label: 'Alert Email Subject',
                id: 'email_alert_subject',
                tooltip: 'Alert Email Subject',
                type: 'text',
                col_class: 'col-12',
                value: system_data.email_alert_subject
            },
            {
                label: 'Alert Email Body',
                id: 'email_alert_body',
                tooltip: 'Alert Email Body',
                type: 'textarea',
                rows: 5,
                col_class: 'col-12',
                value: system_data.email_alert_body
            }
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, system_data.system_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveSystemButton = UIManager.createElement('button', {
            id: `systemEmailSave_${system_data.system_id}`,
            className: "btn btn-md btn-success",
            attributes: {
                "data-system-id": system_data.system_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button',
            name: 'save_email'
        });

        saveSystemButton.onclick = () => {
            this.systemPostForm(UIManager, '/admin/save_system_email_settings', `system_email_edit_form_${system_data.system_id}`)
        }

    }

    systemCreateEmailAddressesPage(UIManager, emailAddressElement, system_data) {
        UIManager.EmailAddressManager.renderSystemEmails(UIManager, emailAddressElement, system_data)
    }

    systemCreatePushoverPage(UIManager, pushoverElement, system_data) {
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Pushover Config",
            parent: pushoverElement
        })

        // Form to Edit System Email Settings
        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `system_pushover_edit_form_${system_data.system_id}`,
            parent: pushoverElement
        });

        UIManager.createElement('input', {
            type: "hidden",
            name: 'system_id',
            value: system_data.system_id,
            parent: form
        })

        let inputFields = [
            {
                label: 'Enable Pushover',
                id: 'pushover_enabled',
                tooltip: 'Enable/Disable sending alerts via Pushover.',
                type: 'select',
                col_class: 'col-4',
                value: system_data.pushover_enabled,
                options: [{value: '1', text: 'Enabled'}, {value: '0', text: 'Disabled', selected: true}]
            },
            {
                label: 'System Pushover Group Token',
                id: 'pushover_group_token',
                tooltip: 'Group token from Pushover For All Agencies.',
                type: 'text',
                col_class: 'col-12',
                value: system_data.pushover_group_token,
            },
            {
                label: 'System Pushover App Token',
                id: 'pushover_app_token',
                tooltip: 'App Token from Pushover App for All Agencies.',
                type: 'text',
                col_class: 'col-12',
                value: system_data.pushover_app_token
            },
            {
                label: 'Pushover Alert Sound',
                id: 'pushover_sound',
                tooltip: 'Alert Sound for Pushover Notification.',
                type: 'text',
                col_class: 'col-6',
                value: system_data.pushover_sound
            },
            {
                label: 'Pushover Message Subject',
                id: 'pushover_subject',
                tooltip: 'Subject for Pushover Message.',
                type: 'text',
                col_class: 'col-6',
                value: system_data.pushover_subject
            },
            {
                label: 'Pushover Message HTML',
                id: 'pushover_body',
                tooltip: 'Message Body for Pushover.',
                type: 'textarea',
                rows: 5,
                col_class: 'col-12',
                value: system_data.pushover_body
            }

        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, system_data.system_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveSystemButton = UIManager.createElement('button', {
            id: `systemPushoverSave_${system_data.system_id}`,
            className: "btn btn-md btn-success",
            attributes: {
                "data-system-id": system_data.system_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button',
            name: 'save_pushover'
        });

        saveSystemButton.onclick = () => {
            this.systemPostForm(UIManager, '/admin/save_system_pushover', `system_pushover_edit_form_${system_data.system_id}`)
        }

    }

    systemCreateFacebookPage(UIManager, facebookElement, system_data) {
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Facebook Config",
            parent: facebookElement
        })

        // Form to Edit System Email Settings
        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `system_facebook_edit_form_${system_data.system_id}`,
            parent: facebookElement
        });

        UIManager.createElement('input', {
            type: "hidden",
            value: system_data.system_id,
            name: 'system_id',
            parent: form
        })

        let inputFields = [
            {
                label: 'Enable Facebook Page Posting',
                id: 'facebook_enabled',
                tooltip: 'Enable/Disable posting to Facebook Page.',
                type: 'select',
                col_class: 'col-4',
                value: system_data.facebook_enabled,
                options: [{value: '1', text: 'Enabled'}, {value: '0', text: 'Disabled', selected: true}]
            },
            {
                label: 'Facebook Page ID',
                id: 'facebook_page_id',
                tooltip: 'Facebook Page ID.',
                type: 'text',
                col_class: 'col-12',
                value: system_data.facebook_page_id,
            },
            {
                label: 'Facebook Page Token',
                id: 'facebook_page_token',
                tooltip: 'Facebook Page Token.',
                type: 'text',
                col_class: 'col-12',
                value: system_data.facebook_page_token,
            },
            {
                label: 'Enable Facebook Post Comment',
                id: 'facebook_comment_enabled',
                tooltip: 'Enable/Disable posting to comment on Facebook Post.',
                type: 'select',
                col_class: 'col-4',
                value: system_data.facebook_comment_enabled,
                options: [{value: '1', text: 'Enabled'}, {value: '0', text: 'Disabled', selected: true}]
            },
            {
                label: 'Facebook Post Body',
                id: 'facebook_post_body',
                tooltip: 'Message Body for Facebook Post.',
                type: 'textarea',
                rows: 5,
                col_class: 'col-12',
                value: system_data.facebook_post_body
            },
            {
                label: 'Facebook Post Comment Body',
                id: 'facebook_comment_body',
                tooltip: 'Message Body for Facebook Post Comment.',
                type: 'textarea',
                rows: 5,
                col_class: 'col-12',
                value: system_data.facebook_comment_body
            },
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, system_data.system_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveSystemButton = UIManager.createElement('button', {
            id: `systemFacebookSave_${system_data.system_id}`,
            className: "btn btn-md btn-success",
            attributes: {
                "data-system-id": system_data.system_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button',
            name: 'save_facebook'
        });

        saveSystemButton.onclick = () => {
            this.systemPostForm(UIManager, '/admin/save_system_facebook', `system_facebook_edit_form_${system_data.system_id}`)
        }

    }

    systemCreateTelegramPage(UIManager, telegramElement, system_data) {
        UIManager.createElement('h4', {
            className: "mt-3 mb-3",
            textContent: "Telegram Config",
            parent: telegramElement
        })

        // Form to Edit System Email Settings
        const form = UIManager.createElement('form', {
            className: 'row g-3',
            id: `system_telegram_edit_form_${system_data.system_id}`,
            parent: telegramElement
        });

        UIManager.createElement('input', {
            type: "hidden",
            value: system_data.system_id,
            name: 'system_id',
            parent: form
        })

        let inputFields = [
            {
                label: 'Enable Telegram Channel Posting',
                id: 'telegram_enabled',
                tooltip: 'Enable/Disable posting to Telegram.',
                type: 'select',
                col_class: 'col-4',
                value: system_data.telegram_enabled,
                options: [{value: '1', text: 'Enabled'}, {value: '0', text: 'Disabled', selected: true}]
            },
            {
                label: 'Telegram Channel ID',
                id: 'telegram_channel_id',
                tooltip: 'Telegram Channel ID.',
                type: 'text',
                col_class: 'col-12',
                value: system_data.telegram_channel_id,
            },
            {
                label: 'Telegram Bot Token',
                id: 'telegram_bot_token',
                tooltip: 'Telegram Bot Token issued by Bot Father',
                type: 'text',
                col_class: 'col-12',
                value: system_data.telegram_bot_token
            }
        ]

        inputFields.forEach(field => {
            UIManager.createFormField(form, field, system_data.system_id, field.value);
        });

        const formSubmitCol = UIManager.createElement('div', {className: "col-12 mb-3 text-end", parent: form})

        const saveSystemButton = UIManager.createElement('button', {
            id: `systemTelegramSave_${system_data.system_id}`,
            className: "btn btn-md btn-success",
            attributes: {
                "data-system-id": system_data.system_id
            },
            textContent: "Save",
            parent: formSubmitCol,
            type: 'button',
            name: 'save_telegram'
        });

        saveSystemButton.onclick = () => {
            this.systemPostForm(UIManager, '/admin/save_system_telegram', `system_telegram_edit_form_${system_data.system_id}`)
        }

    }


    systemCreateWebhookPage(UIManager, webhookElement, system_data) {
        UIManager.WebhookManager.systemRenderWebhooks(UIManager, webhookElement, system_data)
    }

    systemPostForm(UIManager, save_url, form_id) {
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

    systemDeleteAction(UIManager, system_id, system_name, system_short_name) {
        const systemData = {"system_id": system_id, "system_name": system_name, "system_short_name": system_short_name};
        const save_url = `${UIManager.baseUrl}/admin/delete_system`;
        fetch(save_url, {
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