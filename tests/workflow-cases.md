# Skill workflow regression cases

Use these cases when reviewing skill changes or evaluating an agent with the bundle loaded. They
are behavioral acceptance cases, not claims that a model evaluation ran. The automated tests check
catalog/example compatibility and ZIP links; they do not prove an agent follows this guidance.

| Case | Prompt and supplied tool result | Passing behavior | Failing behavior |
|---|---|---|---|
| Renewal candidates | Today is 2026-09-01. Find contracts ending through 2026-11-30. | Uses inclusive endDateFrom/endDateTo; follows all filtered pages; distinguishes expiry from auto-renewal. | Uses updatedSince as an end-date filter; calls document search for exhaustive metadata results. |
| Notice or ending | Find contracts ending OR needing notice next quarter. | Runs separate end-date and notice-date queries, pages both completely, and deduplicates by contract id. | Combines both windows into one AND query and misses records. |
| Vendor ambiguity | Find our contracts with Acme. Party query returns two legal entities. | Resolves which entity is intended before using counterpartyId, or clearly reports both separately. | Picks the first party silently; pages the whole workspace despite available filters. |
| Pagination | First filtered response contains a nextCursor; second contains null. | Repeats the exact filters and any updatedSince with the opaque cursor; counts both pages once. | Omits filters, edits/decodes the cursor, or claims completeness after page one. |
| Changed scope | User changes the date range after page one. | Restarts with the new range and no cursor. | Reuses the old cursor with changed filters. |
| Missing dates and spend | Find contracts missing end dates or worth over 25k. | Uses only relevant supported filters, fully pages the candidate set, then checks missing dates/value locally; separates currencies. | Invents isNull/value arguments or applies a date window that removes missing dates. |
| Older credential | An older credential exposes list filters but no event tools. | Uses discovered filters without changing credentials; treats omitted event tools as separately gated and names re-consent or enabling new actions only when needed. | Claims a schema improvement grants a missing tool or invents an event call. |
| Cached discovery | Existing connector shows only the old list arguments. | Refreshes/reconnects discovery, then uses available schema; if still old, reports limitation and uses honest fallback pagination. | Sends undocumented arguments blindly or creates another connection. |
| Structured result | Success has equivalent structuredContent and JSON text. | Uses structuredContent once; falls back to text only when structuredContent is absent. | Concatenates both representations or double-counts records. |
| Unknown write | Updating type fields returns isError with OUTCOME_UNKNOWN. | Reads current state and reconciles before any retry or claim about the write. | Assumes rollback or retries automatically. |
| Malformed success | A success payload lacks a required output field. | Reports a response mismatch; does not invent a value or retry a write. | Treats missing data as an empty portfolio or confirmed write failure. |
| Folder discovery | The root folder page returns a continuation, and a requested destination appears on its second page. | Repeats the same `limit` and parent with `continuation`, then inspects the visible destination before any change. | Sends a contract cursor to the folder call, stops at the first page, or treats an omitted folder as proof it does not exist. |
| Filing changes | The user asks to file several contracts in a visible folder. | States the visible destination path and every affected contract, confirms the batch, moves them, then reads back the results. | Moves records before confirming the destination or claims success without reconciliation. |
| Unfiled audit | A contract result includes `filing.kind` values `unfiled`, `folder`, and `unavailable`. | Completes the pages and classifies only `unfiled` as unfiled. | Sends `folderId: null`, treats `unavailable` as unfiled, or invents a hidden folder ID. |
| Access overview | A user asks who can access a restricted folder. | Uses the folder access overview when discovered and explains that permission changes and folder deletion happen in the app. | Attempts an ACL write through MCP or exposes a hidden folder's existence. |

Keep live tool discovery authoritative. The pinned catalog is an offline review baseline, not proof
that every tenant or credential has the same tool surface.
