# Transaction guidelines

- Use one request-scoped session and close it in all outcomes.
- Commit only after a complete service operation succeeds; rollback on failure.
- Repository helpers should not commit unless their contract explicitly owns the transaction.
- Keep multi-table changes in one transaction and let constraints reject partial state.
- Keep inference and long-running media/video work outside open transactions.
- Do not catch database errors and continue using the failed session before rollback.
- Migration and seed commands remain separate, explicit operations.
