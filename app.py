from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# A simple in-memory list to store budget entries for the session
transactions = []

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PlanIT - Budget Tracker</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }
        .container { max-width: 600px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; margin-top: 0; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; color: #94a3b8; }
        input, select { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #fff; box-sizing: border-box; }
        button { background: #38bdf8; color: #0f172a; border: none; padding: 12px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; }
        button:hover { background: #0ea5e9; }
        .transaction-list { margin-top: 30px; border-top: 1px solid #334155; padding-top: 20px; }
        .tx-item { display: flex; justify-content: space-between; background: #0f172a; padding: 10px 15px; border-radius: 6px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PlanIT Budget Tracker</h1>
        <p>Log your expenses and manage your balance efficiently.</p>
        
        <form id="budgetForm">
            <div class="form-group">
                <label>Description</label>
                <input type="text" id="desc" placeholder="e.g., Groceries, Transport" required>
            </div>
            <div class="form-group">
                <label>Amount (ZAR)</label>
                <input type="number" id="amount" placeholder="0.00" step="0.01" required>
            </div>
            <button type="submit">Add Transaction</button>
        </form>

        <div class="transaction-list">
            <h3>Recent Transactions</h3>
            <div id="txContainer">
                <!-- Transactions will load here -->
            </div>
        </div>
    </div>

    <script>
        document.getElementById('budgetForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const desc = document.getElementById('desc').value;
            const amount = document.getElementById('amount').value;

            const response = await fetch('/add_transaction', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: desc, amount: amount })
            });

            if (response.ok) {
                loadTransactions();
                document.getElementById('budgetForm').reset();
            }
        });

        async function loadTransactions() {
            const res = await fetch('/get_transactions');
            const data = await res.json();
            const container = document.getElementById('txContainer');
            container.innerHTML = '';
            
            data.forEach(tx => {
                const div = document.createElement('div');
                div.className = 'tx-item';
                div.innerHTML = `<span>${tx.description}</span> <span>R ${tx.amount}</span>`;
                container.appendChild(div);
            });
        }

        loadTransactions();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.json
    if data:
        transactions.append({
            'description': data.get('description'),
            'amount': data.get('amount')
        })
    return '', 204

@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
