# GTI-AI-V2

GTI-AI-V2 is a modular AI-powered trading system for MetaTrader 5 (MT5). It combines market analysis, risk management, trade execution, paper trading, performance tracking, and dashboard monitoring into one architecture.

> **Status:** Active Development

---

# Features

- AI Market Analysis
- Multi-Timeframe Analysis
- Smart Trade Decision Engine
- ATR-Based Stop Loss
- Dynamic Position Sizing
- Trade Setup Engine
- Spread Filter
- Trading Session Filter
- Risk Management
- Paper Trading
- Trade Lifecycle Management
- Statistics Engine
- Trade Journal (CSV)
- Performance Dashboard
- Notification System
- MT5 Integration
- Backtesting Support

---

# Project Structure

```
GTI-AI-V2
│
├── ai/
├── analysis/
├── account/
├── backtesting/
├── config/
├── controller/
├── dashboard/
├── data/
├── execution/
├── filters/
├── history/
├── indicators/
├── journal/
├── learning/
├── models/
├── mt5/
├── news/
├── notifications/
├── paper_trading/
├── risk/
├── scanner/
├── strategy/
├── tests/
├── utils/
├── web/
│
├── main.py
├── run.py
└── README.md
```

---

# Architecture

```
MarketDataService
        │
        ▼
AnalysisPipeline
        │
        ▼
TradingEngine
        │
        ▼
TradeSetupEngine
        │
        ▼
SignalAdapter
        │
        ▼
SpreadFilter
        │
        ▼
SessionFilter
        │
        ▼
RiskManager
        │
        ▼
TradeExecutor
        │
        ▼
TradeLifecycleManager
        │
        ▼
StatisticsEngine
        │
        ▼
TradeJournal
        │
        ▼
Dashboard
```

---

# Requirements

- Python 3.11+
- MetaTrader 5
- Windows
- Git

---

# Installation

Clone the repository:

```bash
git clone https://github.com/ngelejag-afk/GTI-AI-V2.git
cd GTI-AI-V2
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Run

```bash
python main.py
```

or

```bash
python run.py
```

---

# Dashboard

Default dashboard:

```
http://localhost:8000
```

---

# Testing

Run all tests:

```bash
pytest
```

---

# Paper Trading

The system supports paper trading before live execution.

Trade history is automatically stored in:

```
trade_journal.csv
```

---

# Current Components

- Analysis Pipeline
- Trading Engine
- Decision Engine
- Trade Setup Engine
- Signal Adapter
- Risk Manager
- Statistics Engine
- Dashboard
- Trade Journal
- MT5 Integration

---

# Roadmap

- Analytics Engine
- Strategy Optimization
- SQLite Trade Database
- Enhanced Reporting
- Live MT5 Improvements

---

# License

Private project.
