# Job and pack stages

Every job the user decides to go for gets a slug (`ba-acme`) and a history of stages in `profile/ledger.jsonl`. Its current stage is its latest line. `/track` adds a line; `/queue` shows where everything stands.

| Stage | Meaning | Who moves it |
|---|---|---|
| `queued` | The user wants a pack for this job. | the user, at triage |
| `drafted` | The kit has made the pack (CV, letter, fit note). Nothing has been checked by the user yet. | the kit |
| `reviewed` | The user has read and edited the pack and says it's ready. | **the user only** |
| `sent` | The user sent it themselves. The line records a hash of each file sent. | **the user only** |
| `screen` | A first call or screening stage. | the user, or a source document |
| `interview` | Any interview after the screen. Say which round in `note`. | |
| `offer` | An offer was made. | |
| `accepted` | The user accepted. | |
| `declined` | The employer said no, at any stage. Say at which in `note`. | |
| `silent` | Sent, with no response after 14 days. | asked of the user |
| `killed` | The user decided not to send it. The reason in `note` is the most useful line in the ledger. | the user |
| `lapsed` | Drafted, never sent, no decision (drift, or the ad closed). | asked of the user |
| `withdrawn` | The user pulled out after sending. | the user |

The pack's own `PACK.md` shows `status: drafted|reviewed|sent`, mirrored from the ledger.

Rules:

- **The kit never moves a pack to `reviewed` or `sent` by itself.** Those lines are always in the user's voice, with their words in `said`.
- **The kit never sends anything.** `sent` is recorded after the user has sent it.
- **Never edit the ledger.** A correction is a new line whose `note` says what it corrects.
- **Silent at 14 days.** `/queue` lists sent packs older than 14 days with no later line and asks before marking them silent.
- **Drafted and not sent piles up.** `/queue` says plainly when there are more drafted packs than sent ones.
