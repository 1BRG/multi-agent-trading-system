# Bug Report: Portfolio Entry And Metrics Issues

## Summary

The Portfolio workspace allowed confusing or contradictory position data and displayed portfolio metrics in a way that mixed initial cash, invested cost and market value.

## Impact

- Users could not clearly understand how to add a position based on a historical purchase date.
- The UI exposed cash reserve/uninvested cash even though it was not part of the active workflow.
- Position weight could be manually entered instead of derived from the portfolio's actual invested cost.
- The holdings table did not clearly show buy price, current price, invested amount and current value per stock.

## Reproduction

1. Open `http://localhost:3000/dashboard`.
2. Go to `Stocks > Portfolio`.
3. Create or select a portfolio.
4. Try to add a holding with a purchase date and quantity.
5. Observe unclear price/date behavior, cash reserve labeling and missing per-position valuation columns.

## Expected Behavior

- Portfolio creation should only ask for the portfolio container data.
- Position creation should either resolve a historical market price from the selected purchase date or accept a custom price.
- Contradictory data should be rejected by frontend and backend validation.
- Weight should be computed dynamically from each position's invested cost relative to total invested cost.
- Holdings should show buy price, current price, invested cost and current value.

## Resolution

Implemented on branch `stefan-grading-evidence`:

- Added purchase-date price resolution through stored `asset_prices`.
- Added backend validation for price source, purchase date, price date and cost basis.
- Removed cash reserve from the visible Portfolio UI.
- Replaced manually entered target weight with dynamic investment weight.
- Added holdings table columns for buy price, current price, invested cost and current value.
- Added automated tests for portfolio validation and price resolution.
