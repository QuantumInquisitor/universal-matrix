class UniversalMatrixClient {
    constructor(baseUrl = "http://127.0.0.1:8000") {
        this.baseUrl = baseUrl.replace(/\/$/, "");
    }

    async getHealth() {
        const response = await fetch(`${this.baseUrl}/`);
        return await response.json();
    }

    async evaluateAgent(nodes) {
        const response = await fetch(`${this.baseUrl}/api/v1/agent/evaluate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nodes })
        });
        return await response.json();
    }
}

module.exports = { UniversalMatrixClient };

