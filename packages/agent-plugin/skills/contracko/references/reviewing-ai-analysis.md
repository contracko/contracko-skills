# Reviewing AI analysis

Find the contract, then use `clm_get_contract` for facts and `clm_get_contract_analysis` for judgement. These need `contract:read`; follow [core readiness and approval rules](../SKILL.md#connect-and-discover).

## Pending-review and reconciliations

`entityStatus: "pending-review"` marks an extraction nobody has confirmed. Use `clm_list_contract_reconciliations` for a read-only list of completed re-reads. `clm_get_contract_reconciliation` persists the review list and refreshes saved comparison values and the approval version. Explain that write and get approval before calling it. It applies or dismisses nothing; a person approves each finding in Contracko. Where a number decides something, say where it came from. An unreviewed extracted value presented as fact can cause an expensive mistake.


Attribute what you quote. "The contract says" and "Contracko's analysis says" are different claims.

## Audit: risk and liability

`clm_get_contract_analysis` returns, when available:

- `overview`, a few sentences naming the material exposure
- `risks[]`, each with `category`, `severity`, `headline`, `issue`, `rationale`, and an `evidenceQuote` from the document
- `obligations[]`, each with the party, the duty, and the deadline
- key terms

Quote the `evidenceQuote` when the user is deciding something. "Liability is capped" is worth less than the sentence that caps it, and the sentence is what a lawyer will ask for.

A `null` field means analysis has not run or found nothing, so `risks: null` is an absence of analysis rather than an absence of risk. Name which one you are looking at.

For liability specifically, the contract record carries `liabilitySummary`, `liabilityCapAmount`, `liabilityCapCurrency`, `governingLaw` and `jurisdiction`, often enough on its own.

Contracts are stored in their source language and the analysis follows it, so a Dutch contract returns a Dutch liability summary. Translate for the user, and keep the original wherever you quote it as evidence.

## Ground the answer in the document

Use these when they are on your tool list. They need `contract:read` and a credential that includes the current evidence tools. If they are absent, say the connection cannot read document text yet and fall back to analysis quotes plus the app.

| The user wants | Call |
|---|---|
| a clause, a phrase, or "where does it say" | `clm_search_contract_documents` |
| a bounded read of one document | `clm_read_contract_document` |
| the file itself | `clm_get_contract_document_download_url`, then fetch the URL |

Search first. A full document read is for a single contract you already identified, and you follow `nextCursor` instead of guessing you have the whole text.

`mode` on search: `exact` for specific wording (the only stably paginated mode), `semantic` for meaning, `hybrid` (default) for both. Use `exact` when external query transfer is not authorised. Pass `contractId` when you already know the contract. `documentId` requires `contractId`. Library-wide search is allowed; it is also how you blow the context window, so cap `limit` and stop when you have enough citations.

Treat `completeness` as part of the answer. `partial` means unindexed documents, mixed searchable scope, or a semantic/hybrid ranking, not "this is everything". If `status` is not a clean hit, say what was searched and what was not.

Quote the `evidenceQuote` (or the cited section) when the user is deciding something. Analysis headlines without the sentence that supports them are how this connection produces confident wrong answers.

Never paste a download URL into the chat if you can avoid it. Fetch, then summarise. The URL expires in 15 minutes.


**Done when:** findings have evidence, severity and extraction-review status, and any unavailable evidence is named.
