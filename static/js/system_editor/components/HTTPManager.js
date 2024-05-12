export class HTTPManager {

    /**
     * Fetch data from a URL with enhanced options for query parameters and body data.
     *
     * @param {string} url - The base URL to fetch from.
     * @param {object} [options={}] - Optional settings for the fetch request.
     * @param {object} [options.params] - Query parameters to append to the URL.
     * @param {string} [options.method='GET'] - HTTP method to use (GET, POST, etc.).
     * @param {object} [options.body] - Data to send in the body of the request, for POST or PUT requests.
     * @param {HeadersInit} [options.headers] - Headers to include in the request.
     * @returns {Promise<any>} A promise that resolves with the response data.
     */
    fetchData(url, options = {}) {
        // Construct URL with query parameters if present
        const urlObj = new URL(url);
        if (options.params) {
            Object.keys(options.params).forEach(key => urlObj.searchParams.append(key, options.params[key]));
        }

        // Setup fetch options
        const fetchOptions = {
            method: options.method || 'GET',
            headers: options.headers || {},
        };

        // Add body if method is POST or PUT and body is provided
        if ((fetchOptions.method === 'POST' || fetchOptions.method === 'PUT') && options.body) {
            fetchOptions.body = JSON.stringify(options.body);
            fetchOptions.headers['Content-Type'] = 'application/json';
        }

        // Perform the fetch request
        return fetch(urlObj.toString(), fetchOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => console.error('Fetch error:', error));
    }

    postData(url, data) {
        return this.fetchData(url, {
            method: 'POST',
            body: data
        });
    }

}