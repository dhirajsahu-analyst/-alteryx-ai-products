# Quick Start Guide

Get up and running with Product Insights AI in 5 minutes.

---

## Prerequisites

- Python 3.9 or later
- Snowflake account with warehouse access
- ~30 seconds for setup

## Step 1: Clone the Repository

```bash
git clone [YOUR-GIT-SERVER-URL]/Product-Insights-AI.git
cd Product-Insights-AI
```

## Step 2: Run Setup Script

```bash
./setup.sh
```

This will:
- Check Python installation ✓
- Install dependencies (pyyaml, snowflake-connector-python) ✓
- Create configuration directory (~/.config/alteryx/) ✓
- Prompt for Snowflake credentials ✓
- Test connection to Snowflake ✓

**What you'll be asked:**
- Snowflake Account Identifier (e.g., `ALTERYX-ALTERYX_EDW`)
- Snowflake User (e.g., `your_email@alteryx.com`)
- Snowflake Role (e.g., `YOUR_NAME_ROLE`)
- Snowflake Warehouse (e.g., `ANALYTICS_WH`)

## Step 3: Start the CLI

```bash
python agent/cli/main.py
```

You'll see:
```
╔════════════════════════════════════════════════════════════╗
║    PRODUCT INSIGHTS AI — Ask Questions, Get Answers        ║
╚════════════════════════════════════════════════════════════╝

Type your question (or 'help' for examples, 'quit' to exit):
```

## Step 4: Ask Your First Question

Try one of these:

```
> How many active users did we have last month?
> What is our Copilot adoption rate?
> Show me version adoption trends
> What is our trial conversion rate?
```

## Step 5: Explore the Answer

You'll receive:
- **Metric Definition** — What this metric means
- **Business Context** — Why it matters
- **SQL Query** — The exact SQL used (for transparency)
- **Data** — The actual result
- **Freshness** — When the data was last updated
- **Caveats** — Important limitations or notes
- **Lineage** — Where the data comes from

---

## Example Session

```
Type your question (or 'help' for examples, 'quit' to exit):
> How many active users did we have last month?

╔════════════════════════════════════════════════════════════╗
║                   ANSWER                                   ║
╚════════════════════════════════════════════════════════════╝

📊 Metric: Alteryx One Monthly Active Users
📌 Definition: Unique users with activity in a given month
📈 Data Freshness: Updated daily, last refresh 2 hours ago

RESULT:
Month       Active Users
2026-07     12,450
2026-06     11,890
2026-05     10,200

🔍 How It's Calculated:
SELECT COUNT(DISTINCT user_id) as active_users
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.ALTERYX_ACCOUNTS_ACTIVATION_VIEW
WHERE YEAR_MONTH = '2026-07'
...

📚 Data Lineage:
Source: ALTERYX_ACCOUNTS_ACTIVATION_VIEW
Tables: User events, account activation records
Last Updated: 2 hours ago

⚠️  Known Limitations:
- Does not include API-only users
- Trial accounts are included

Type your next question (or 'quit' to exit):
```

---

## Common Questions

### How do I ask about multiple products?

Use natural language — the system detects which product area you're asking about:

```
How many Copilot users are we getting?    # → Ask Alteryx
How did our trial conversion change?       # → Trial Analytics
What's our latest Designer version adoption?  # → Version Adoption
```

### Can I see the SQL for a question?

Yes! Every answer includes the exact SQL query used. Look for the section labeled `🔍 How It's Calculated`.

### What if I don't have Snowflake credentials?

The system will work in **simulation mode** — it will:
- Show you the SQL that would run
- Explain what data you'd get
- But won't return actual data

This is useful for testing or demos.

### What products are available?

```
✓ Alteryx One         — Activation, onboarding, engagement
✓ Ask Alteryx/Copilot — Copilot adoption and retention
✓ Version Adoption    — Product version adoption trends
✓ Designer           — Designer workflows and usage
✓ Account & User     — Overall account and user metrics
✓ Trial             — Trial signups and conversions
```

### Can I contribute new metrics?

Yes! See [CONTRIBUTING.md](../CONTRIBUTING.md) for the analyst workflow.

---

## Troubleshooting

### Connection Error

**Problem:** "Failed to connect to Snowflake"

**Solution:**
1. Check your account identifier: `ALTERYX-ALTERYX_EDW` (not just `ALTERYX`)
2. Verify you're in a network that can reach Snowflake
3. Confirm your role has warehouse access
4. Run `./setup.sh` again to re-enter credentials

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'snowflake'`

**Solution:**
```bash
pip install pyyaml snowflake-connector-python
```

### Question Not Understood

**Problem:** "I couldn't understand your question"

**Solution:**
- Use keywords from the product names: "Copilot", "Designer", "Alteryx One"
- Be specific: "How many active users" instead of "Give me stats"
- Try simpler questions first

### No Data Returned

**Problem:** Query runs but returns empty results

**Possible reasons:**
- Date range doesn't have data (e.g., asking for "next month")
- Filter is too restrictive
- Check data freshness (may not be updated recently)

---

## Next Steps

1. **Explore Examples** — Run through 5-10 questions
2. **Read Docs** — Check [FAQ.md](FAQ.md) and [GOVERNANCE.md](GOVERNANCE.md)
3. **Add Metrics** — See [CONTRIBUTING.md](../CONTRIBUTING.md)
4. **Join Community** — Ask in #product-analytics Slack

---

## Quick Reference

| Task | Command |
|------|---------|
| Start the CLI | `python agent/cli/main.py` |
| First time setup | `./setup.sh` |
| View version | `cat VERSION` |
| View changelog | `cat CHANGELOG.md` |
| Contribute metrics | See `CONTRIBUTING.md` |
| Get help | Type `help` in the CLI |

---

**Happy analyzing! 🚀**

**Questions?** Join #product-analytics on Slack or create an issue in this repo.
