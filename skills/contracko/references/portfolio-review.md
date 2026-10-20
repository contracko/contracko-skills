# Portfolio review

## Filter first, then page

`clm_list_contracts` supports `status`, `categoryId`, `counterpartyId`, `query`, `endDateFrom`, `endDateTo`, `noticeDateFrom`, `noticeDateTo`, `updatedSince`, and a valid visible `folderId`. These filters combine with AND. `query` is a literal, trimmed, case-insensitive substring of the title and assigned Party B display or legal name, including historical names. It is not semantic search. `clm_search_contract_documents` searches document text, not these fields.

Use the narrowest supported server criteria first. Then follow `nextCursor` until it is `null`, repeating the same normalized filters and `updatedSince` if used. `limit` may change between calls. Cursors are opaque: never edit one. If any filter changes, restart without a cursor.

For an unsupported value, currency, null-presence, or custom-field filter, first narrow with supported server criteria, then page that entire result before applying the local condition. For a full-workspace audit, page everything. Do not use a date window to find missing dates, because null dates are excluded from that window.

`updatedSince` can combine with business filters. An `updatedSince`-only legacy sync remains unbound, and it is not an end-date filter or renewal window.

The contract payload carries `title`, `status`, `categoryId`, `startDate`, `endDate`, `autoRenewing`, `renewalPeriod*`, `noticePeriod*`, `noticeDate`, `isInNoticePeriod`, `isOpenEnded`, `financialAnnualValue`, `financialValueCurrency`, `liabilitySummary`, `governingLaw`, `jurisdiction`, `partiesSummary`, `customFieldValues`, and `entityStatus`.

Where the filtered set is still too large to page, say so before answering and offer a narrower supported question.

## Calendar: notice, end, annual review

For a date window, use the inclusive `YYYY-MM-DD` `endDateFrom` and `endDateTo` or `noticeDateFrom` and `noticeDateTo` filters, then page the result. For contracts ending OR needing notice, run both queries separately and deduplicate by contract id. Combining both windows in one call requires both to match and would miss contracts.

- `isInNoticePeriod: true` means the window to give notice is open now. The urgent bucket.
- `noticeDate` is the deadline to give notice.
- An end-date window finds renewal candidates. `autoRenewing: true` is the actual renewal status. Do not call a contract definitively already committed without notice-date evidence.
- `endDate` with `autoRenewing: false` is a plain expiry.
- `isOpenEnded: true` has no end date by design, so read it as intentional rather than as missing data.

Sort by `noticeDate`, not `endDate`. The deadline that costs money is the notice one, typically months earlier.

**Get today's date from the environment before comparing anything to it.** Every answer here is date arithmetic against now, and a remembered date is quietly wrong in a way the output never reveals.

Where the contract is not in the workspace at all, [import it first](importing-contracts.md).

## Report: priorities, gaps, vendors

Use `noticeDate` or `endDate` windows for dated buckets, and `status`, `categoryId`, `counterpartyId`, or literal `query` where they narrow the question. Page each resulting set to the end, then bucket. For missing-field, value, currency, or custom-field gaps, page the relevant complete set before filtering locally. Suggested order, drop empty buckets:

1. Notice window open (`isInNoticePeriod`)
2. Notice in the next 90 days
3. Ending soon without auto-renew
4. Auto-renew with notice-date evidence that it is already committed
5. `entityStatus: "pending-review"`
6. Missing `noticeDate` or `endDate` (and not `isOpenEnded`)
7. Missing `financialAnnualValue`
8. [Unfiled contracts](organising-the-workspace.md#folders-and-filing), as a filing gap
9. [Analysis not available](reviewing-ai-analysis.md#audit-risk-and-liability), not "no risk"

Rank inside a bucket by `noticeDate`, then value. Say how many contracts you paged.

For "What do we have with vendor X", first resolve the vendor with `clm_list_parties` using `query` and, when known, `type`. Confirm the user's selection if the results are ambiguous, then use that party's id as `counterpartyId` in `clm_list_contracts` and page that result. For a filing audit, use the [filing-state rules](organising-the-workspace.md#folders-and-filing).

**Check `financialValueCurrency` before adding anything up.** Values are per contract and the currency varies, so a total across mixed currencies is a made-up number. Sum per currency, or convert with a rate you state.

## Compare proposals and versions

There is no playbook tool and no redline-diff tool. Comparison is a table you assemble.

**Two contracts already in Contracko.** Get both records and both analyses. Search each for the contested terms (price, term, notice, liability, termination, data, IP). Table: term | A | B | who is better off, with an `evidenceQuote` on anything that decides the deal.

**Two files not in Contracko.** [Import them](importing-contracts.md), then compare. A vendor A/B belongs as two contracts, not one. For standalone processing instead of filing, apply [product choice](../SKILL.md#choose-the-product).

**Redline vs previous draft.** If the user says these are versions of one agreement, keep them as documents on *one* contract (`clm_add_contract_documents` is a write: follow [related-document intake](importing-contracts.md#add-contract-documents) if they are not attached yet). Read both texts. Analysis is per document, not a diff; you still have to line the clauses up.

Playbook / house-position scoring is app work. Say so and still deliver the A/B table from the documents you have.


## Risk audit

Page the relevant portfolio, then follow [AI analysis and evidence review](reviewing-ai-analysis.md#audit-risk-and-liability) for each contract. Document search is not an exhaustive metadata query. For annual-review events and requested alerts use [notifications](notifications.md).

**Done when:** dates and priorities name the completed result-set count and gaps; comparisons support a choice with quotes. Confirm any requested notifications through [notifications](notifications.md).
