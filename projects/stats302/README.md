# STATS 302 · Modeling S&P 500 Returns

The [analysis notebook](stats302_market_causal_analysis.ipynb) builds market features from Yahoo Finance, checks identifiability under a lagged sector-level causal graph, and explores coefficient estimates using Graphical RICA and cross-moment estimation.

The [coefficient CSV](outputs/sp500_effects_comparison.csv) reproduces the saved notebook output at its displayed precision. The portfolio shows selected estimates by method. The estimates depend on graph assumptions and the full graph was not identified in the unknown-graph check.
