# Notifications

A notification hangs off an event. List first: `clm_list_contract_events`.

**System events** (`notice`, `end`, `open_ended_review`) already exist. You do not create them. Renewal alerts target `end`. Attach a notification with `clm_create_event_reminders`, `anchorType: "system"`, and that `systemType`.

**Custom events** (a review meeting, an option window, an insurance expiry) are created with `clm_create_contract_events`: `title`, `date` as `YYYY-MM-DD`, optional recurrence (`recurrenceInterval` and `recurrenceUnit` together), optional nested `reminders` (max 25 per event). Batches are max 100 events or notifications, each item independent.

**Annual review.** On an open-ended contract, use the `open_ended_review` system event. Otherwise create a custom event, or fall back to a review custom field / the anniversary of `startDate`. Say which rule you used.

Contracko emails each notification to its recipient when it falls due. Before creating or changing one, say who will be emailed and when. Deleting a notification, or its event, stops that email.

A notification needs `offsetValue`, `offsetUnit` (`days` | `weeks` | `months` | `quarters` | `years`), `offsetDirection` (`before` | `on` | `after`), and `recipient` (`{ "type": "contract_owner" }` or `{ "type": "user", "userId" }`). `on` requires `offsetValue: 0`. Optional `message`.

Mutations need `idempotencyKey` (8–128 characters). Update and delete need `expectedUpdatedAt` as a UTC timestamp ending in `Z`. Changing notifications on a custom event advances that event's version: relist before you replace its notification set. Deleting an event deletes its notifications; deleting a notification leaves the event.

For missing tools, follow [recovery](../SKILL.md#errors).

Follow [core bulk confirmation](../SKILL.md#write-safely). Read back requested notifications before claiming they were created.


For the dates to target, follow [notice and end-date calendar review](portfolio-review.md#calendar-notice-end-annual-review).
