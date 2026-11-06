# 02_EASA/submission — what we hand in

| File | What | Made by |
|---|---|---|
| `Team_Beetiful_EASA_Report.docx` | **the report** in the organisers' Word template: cover, contents, body p. 3–7 (5 pages), references p. 8 | `python -I 02_EASA/scripts/easa_report_docx.py` |
| `Team_Beetiful_EASA_Report.pdf` | the same, exported by Word, for reading | same command |
| `EASA_LOCK-SENSE_4min.pptx` | the 4:00 talk deck (speaker notes = `kit/02_talk_4min.md`) | `python -I 02_EASA/scripts/easa_deck.py` |
| `EASA_LOCK-SENSE_4min.ux_denetim.md` | UX audit of the deck | by hand after each deck build |

**Where the report text lives:** `../kit/03_report_draft.md`. The report command rebuilds the docx from it every time,
so edit the draft and rerun. Once the team starts editing the docx in Word, stop running the command, or it overwrites
those edits.

The command prints three checks: `number check vs tradeoffs.json` (every §5 number still matches the latest
trade-off run), the page count (`body pages … of 5`), and the files written.
