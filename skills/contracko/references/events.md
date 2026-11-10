# Events

A client that supports MCP Events can subscribe to Contracko events and be notified when something happens, instead of checking again and again. ChatGPT supports Events and delivers them by webhook, for example into Work chats. A client without Events support keeps using the normal status tools, and nothing changes for it.

## Subscribe or poll

- **Subscribe** for work that takes a while or lands later: an import or AI extraction finishing, an upcoming contract date, a reminder being sent.
- **Poll** only when the client cannot subscribe: check once with the status tools, following [after intake is accepted](importing-contracts.md#after-intake-is-accepted).
- **Never do both** for the same work.
- An event carries identifiers and status only. After one arrives, read the details with the normal tools, such as `clm_get_contract` or `clm_get_import_status`.

## Current events

| Event | Fires when |
|---|---|
| `contract.import.progress` | an import moves forward |
| `contract.import.completed` | an import finishes |
| `contract.import.failed` | an import fails |
| `contract.extraction.completed` | AI extraction on a contract finishes |
| `contract.extraction.failed` | AI extraction on a contract fails |
| `contract.event.upcoming` | a contract date is coming up |
| `contract.notification.sent` | a reminder notification was sent |

More long-running tasks will gain events. Do not promise which or when.

## Subscriptions

A subscription lasts up to seven days. Refresh it before it lapses if the work needs to run longer. Delivery only includes what the connection can read: events for contracts outside its access are not sent.

For the first message to the user after intake, and for reminders, follow [importing contracts](importing-contracts.md#after-intake-is-accepted) and [notifications](notifications.md). Events change how you wait, not what you tell the user.
