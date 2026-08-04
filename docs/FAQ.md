# Frequently Asked Questions

---

## General Questions

### What is Product Insights AI?

It's a self-serve product analytics system that lets you ask natural language questions about Alteryx products and get instant SQL-based answers from Snowflake.

**Example:** "How many active users did we have last month?" → Returns data + SQL + context

### Who can use it?

Anyone with:
- Snowflake access (product teams, analysts, leadership)
- Python 3.9+
- 5 minutes to run setup.sh

### What data sources does it use?

All data comes from `DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE` — our central semantic data warehouse layer. This includes:

- 42 views (Alteryx One, Ask Alteryx, Designer, Trial, etc.)
- 23 validated metrics
- Updated daily

### Is it secure?

Yes. Here's why:

- ✓ No credentials stored in Git
- ✓ SELECT-only enforcement (no writes)
- ✓ Uses your own Snowflake credentials
- ✓ Respects your Snowflake role permissions
- ✓ Audit logging (with no sensitive data logged)

---

## Using the System

### How do I ask questions?

Use natural language. The system understands:

```
✓ "How many active users did we have last month?"
✓ "What's our Copilot adoption rate?"
✓ "Show me version adoption trends"
✓ "Trial conversion rate for Q2"
```

### What if my question isn't understood?

Use keywords from the product names:

| Product | Keywords |
|---------|----------|
| Alteryx One | activation, onboarding, ayx1, alteryx one |
| Ask Alteryx | copilot, chat, adoption |
| Version Adoption | version, adoption, 2025, 2026 |
| Designer | designer, workflow |
| Trial | trial, signup, conversion |

### Can I get historical data?

Yes. Ask about specific time periods:

- "Last month"
- "Last 6 months"
- "Q2 2026"
- "2026-01 to 2026-03"
- "January 2026"

The system detects date ranges from your question.

### What format is the data in?

Answers include:

1. **Metric Definition** — What it means
2. **SQL Query** — Exact query executed
3. **Data** — Results in table format
4. **Freshness** — Last update time
5. **Lineage** — Data source & tables
6. **Limitations** — Important caveats

### Can I export the data?

The system shows results in the CLI. To export:

1. Copy the SQL from the answer
2. Run it directly in Snowflake
3. Export from Snowflake UI

Or ask the analytics team for export support.

---

## Technical Questions

### How does it detect products?

The **router** uses:

1. **Keyword matching** — Looks for product-specific terms
2. **Confidence scoring** — Rates how confident it is (95%+ threshold)
3. **Fallback heuristics** — If unsure, defaults to most likely product

Example: "active users" + "last month" → High confidence it's Alteryx One

### How does it generate SQL?

The **SQL generator**:

1. Identifies the product area (via router)
2. Finds the right metric (via resolver)
3. Generates a safe SELECT query using the source view
4. Adds date filtering based on your question
5. Adds any requested filters or grouping

### What safety checks are in place?

The **SQL validator** performs 7 checks:

1. ✓ Blocks dangerous keywords (CREATE, ALTER, DELETE, etc.)
2. ✓ Enforces SELECT-only
3. ✓ Validates SQL syntax
4. ✓ Checks column existence
5. ✓ Warns on risky joins
6. ✓ Estimates execution time
7. ✓ Enforces row limits

### How fresh is the data?

Data freshness depends on the metric. Most metrics are updated:

- **Daily** — User activity, adoption rates
- **Weekly** — Version distribution
- **Monthly** — Long-term trends

The system tells you when each metric was last updated.

### What if Snowflake is down?

The system gracefully degrades:

- Shows you the SQL that would run
- Explains what data you'd get
- Doesn't return actual results

This is useful for demos or testing.

---

## Metric & Governance Questions

### How many metrics are available?

**23 total**, spread across 6 products:

- Alteryx One: 6 metrics
- Ask Alteryx: 5 metrics
- Version Adoption: 4 metrics
- Designer: 3 metrics
- Account & User: 3 metrics
- Trial: 2 metrics

See `/catalog/global_metric_index.yaml` for the complete list.

### How do I add a new metric?

See [CONTRIBUTING.md](../CONTRIBUTING.md). The process:

1. Create a branch: `git checkout -b feature/new-metric`
2. Add metric YAML in `/products/[product]/metrics/`
3. Update `/catalog/global_metric_index.yaml`
4. Submit PR for review
5. Wait for approval & merge

**Review SLA:**
- Small metrics (1-2): 1-2 days
- Product updates: 3-5 days
- New products: 1 week

### Can I deprecate a metric?

Yes. Instead of deleting:

1. Update `validation_status: deprecated`
2. Document in the metric's YAML
3. Notify users
4. Update the changelog

This prevents breaking existing questions.

### How is metric quality ensured?

Requirements:

- ✓ Clear business definition (for PMs)
- ✓ Technical definition (for engineers)
- ✓ Real example questions
- ✓ Data quality rules
- ✓ Owner assignment
- ✓ Documentation of limitations

Review process via PR:

- ✓ Peer review (analyst team)
- ✓ Semantic validation
- ✓ CI/CD tests (GitHub Actions)

---

## Troubleshooting

### "I couldn't understand your question"

**Try:**
- Using product keywords: "Copilot", "Designer", "trial"
- Simpler phrasing: "active users" instead of "engagement metrics"
- Specific metrics: "What is the Copilot adoption rate?"

### "No data returned"

**Check:**
- Date range is valid (not future dates)
- Filters are reasonable
- Metric exists for that time period

**Debug:**
- Copy the SQL from the answer
- Run it manually in Snowflake
- Check data freshness

### "Connection failed"

**Fix:**
```bash
./setup.sh
```

Re-enter your Snowflake credentials. Verify:
- Account identifier (e.g., `ALTERYX-ALTERYX_EDW`)
- User has warehouse access
- You're on the company network

### "Module not found" errors

**Install dependencies:**
```bash
pip install pyyaml snowflake-connector-python
```

### Performance is slow

**Reasons:**
- Snowflake warehouse is paused
- Query is selecting many rows
- Network latency

**Solutions:**
- Resume your warehouse: Snowflake UI → Warehouses
- Use narrower date ranges
- Check query complexity in the answer

---

## Limitations & Caveats

### What metrics are NOT available?

We cover:
- ✓ Product activation & adoption
- ✓ User engagement & retention
- ✓ Version distribution
- ✓ Trial funnel

We don't cover (yet):
- ✗ Financial metrics
- ✗ Support & billing data
- ✗ Marketing attribution
- ✗ Revenue analytics

### What date ranges work?

**Supported:**
- Last [N] days/weeks/months
- Specific dates: "2026-08-03"
- Ranges: "2026-07 to 2026-08"
- Year-month format: "2026-07"

**Not supported:**
- Future dates
- Exact times (only dates/months)
- Fiscal calendar calculations (yet)

### Can I use this offline?

No — it requires:
- Snowflake connection (for data)
- Python + dependencies (for CLI)
- Internet access (for authentication)

In simulation mode (no Snowflake), it shows SQL only.

### Can I integrate with other tools?

Currently: CLI-only

Future (Phase 7): GraphQL API for programmatic access

---

## Getting Help

### Where do I find more info?

- 📖 **Setup:** See [QUICK_START.md](QUICK_START.md)
- 📚 **Governance:** See [GOVERNANCE.md](GOVERNANCE.md)
- 🤝 **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md)
- 📖 **Main Guide:** See [README.md](../README.md)

### Who do I contact?

- 💬 **Quick questions:** #product-analytics Slack
- 🐛 **Found a bug:** Create an issue in this repo
- 👤 **Need access:** Contact Analytics Lead
- 💡 **Metric idea:** DM the analytics lead

### Can I suggest features?

Yes! Open an issue or ask in #product-analytics:

- New metrics to add
- Products to expand
- UI/UX improvements
- Integration requests

---

**Last Updated:** 2026-08-03

**Questions not listed?** Ask in #product-analytics or create an issue! 🙋
