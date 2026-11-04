# Named process steps

A number is reading order. The name in angle brackets stays put when a step is inserted.

```cairn
CONTEXT
Invoice desk — the clerk and the ledger.

REQUIREMENTS
R1. An invoice is approved or returned. [MUST]
   ACCEPTANCE: the ledger records one terminal decision.

PROCESS ApproveInvoice (INPUT: invoice; OUTPUT: decision)
  1. <receive-invoice> Receive the supplier invoice. [CODE, DETERMINISTIC]
  2. <approve> DECISION Approve or return. [HUMAN, GATED]
     BINDS: requirement-approve-invoice
  3. <record-decision> Record the outcome. [CODE, DETERMINISTIC]
     PURPOSE: the ledger is the record a later audit reads
```
