import {HTTPManager} from "./components/HTTPManager.js";
import {UIManager} from "./components/UIManager.js";
import {SystemManager} from "./components/SystemManager.js"
import {TriggerManager} from "./components/TriggerManager.js";
import {EmailAddressManager} from "./components/EmailAddressManager.js";
import {WebhookManager} from "./components/WebhookManager.js";
import {FilterManager} from "./components/FilterManager.js";
import {KeywordManager} from "./components/KeywordManager.js";

export class SystemEditor {

    constructor() {
        this.url_path = window.location.pathname;
        this.base_url = window.location.origin
        this.HttpManager = new HTTPManager();
        this.SystemManger = new SystemManager();
        this.TriggerManager = new TriggerManager();
        this.EmailManager = new EmailAddressManager();
        this.WebhookManager = new WebhookManager();
        this.FilterManager = new FilterManager();
        this.KeywordManager = new KeywordManager();
        this.UIManager = new UIManager(this.SystemManger, this.TriggerManager, this.EmailManager, this.WebhookManager, this.FilterManager, this.KeywordManager);
        this.system_id = null;
        this.trigger_id = null;
        this.filter_id = null;
        this.system_data = null;

        this.getQueryStrings();
        this.processFlashMessages();
        this.initEditor();
    }

    processFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');

        flashMessages.forEach((el) => {
            const category = el.getAttribute('data-category');
            const message = el.getAttribute('data-message');

            this.UIManager.showAlert(message, category);

            el.remove();

        });
    }

    getQueryStrings(){
        const queryString = window.location.search;
        const params = new URLSearchParams(queryString);
        this.system_id = params.get("system_id");
        this.trigger_id = params.get("trigger_id");
        this.filter_id = params.get("filter_id");

    }

    async initEditor() {
        console.log(this.url_path)
        if (this.url_path === "/admin/systems") {
            const request_url = `${this.base_url}/api/get_systems`;
            const options = {
                params: {
                    with_triggers: true
                }
            };

            this.HttpManager.fetchData(request_url, options)
                .then(systems_data => {
                    this.UIManager.initSystemsPage(systems_data);
                })
                .catch(error => {
                    this.UIManager.showAlert(`Error fetching systems: ${error}`, "danger")
                });
        } else if (this.url_path === "/admin/triggers") {
            const request_url_system = `${this.base_url}/api/get_systems`;
            const request_url_filter = `${this.base_url}/api/get_filters`;

            // Ensure there is a system_id
            if (!this.system_id) {
                this.UIManager.showAlert(`Error fetching system triggers: No System ID Given`, "danger");
                return;
            }

            const options = {
                params: {
                    system_id: this.system_id,
                    with_triggers: true
                }
            };

            try {
                // Fetch data from both endpoints
                const systemPromise = this.HttpManager.fetchData(request_url_system, options);
                const filterPromise = this.HttpManager.fetchData(request_url_filter);

                // Use Promise.all to wait for both promises to resolve
                const [system_data, filter_data] = await Promise.all([systemPromise, filterPromise]);

                console.log(system_data, filter_data);

                // Handle system data
                if (system_data.success) {
                    // You might want to do something with filter_data here or pass it along
                    this.UIManager.initTriggersPage(system_data.result[0], filter_data.result);
                } else {
                    this.UIManager.showAlert(system_data.message, "danger");
                }
            } catch (error) {
                this.UIManager.showAlert(`Error fetching system triggers: ${error}`, "danger");
            }
        } else if (this.url_path === "/admin/filters"){
            const request_url = `${this.base_url}/api/get_filters`;

            const options = {
                params: {
                }
            };

            this.HttpManager.fetchData(request_url, options)
                .then(filter_data => {
                    console.log(filter_data)
                    if (filter_data.success){
                        this.UIManager.initFiltersPage(filter_data);
                    } else {
                        this.UIManager.showAlert(filter_data.message, "danger")
                    }
                })
                .catch(error => {
                    this.UIManager.showAlert(`Error fetching system triggers: ${error}`, "danger")
                });
        }
    }

}