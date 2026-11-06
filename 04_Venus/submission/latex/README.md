# LaTeX replica of the Ideathon 2026 Word report template

The class `ideathon2026.cls` reproduces
`00_Common/rules_and_templates/originals_2026-11-05/Ideathon_Template_2026.docx`
as Word renders it on this PC (Word 2024, Microsoft 365 cloud fonts), plus the
figure, table and reference styles that `02_EASA/submission/Team_Beetiful_EASA_Report.docx`
uses. Every number in the class comes from the template's XML (`document.xml`,
`styles.xml`, `numbering.xml`, `header2.xml`, `footer1.xml`, `theme1.xml`,
`settings.xml`) or was measured in Word's PDF output. The source of each value
is written as a comment next to it in the class.

## Files

| File | What it is |
|---|---|
| `ideathon2026.cls` | the class (page, fonts, spacing, headings, contents, cover, header/footer, lists, figures, tables, references) |
| `ideathon2026-linebreak.lua` | Word-style line breaking and interword spaces (loaded by the class) |
| `fonts/` | Montserrat 7.200, the same files Word uses (see "Fonts") |
| `images/cover.png`, `images/page_background.png` | `word/media/image1.png` (cover) and `image2.png` (header/footer band of every page), unchanged |
| `main.tex` | starting point for a report: cover, contents, headings, list, figure, table, citations, references |
| `example_lorem.tex` / `.pdf` | the template's own text 1:1 (cover, contents, all lorem ipsum paragraphs and headings), for the comparison |
| `compare.py` | renders the Word template to PDF with Word and compares it with `example_lorem.pdf` |
| `compare/` | output of `compare.py`: `page_NN.png` (Word / LaTeX / overlay), `report.md`, `text_deviations.csv`, `word_template.pdf` |
| `tests/` | extra checks: line breaking against Word on 150 random paragraphs, references/table/figure against the EASA report (`python tests/run_tests.py`, result in `tests/results.md`) |
| `figures/placeholder.png` | placeholder picture used in `main.tex` |

## How to compile

Open a terminal **in this folder** and run

    latexmk -lualatex main.tex

or, without latexmk, `lualatex main.tex` twice (the second run fills in the
contents page). The class needs **LuaLaTeX** (MiKTeX or TeX Live; tested with
MiKTeX 26.5, LuaHBTeX 1.25.7). It stops with an error under pdfLaTeX or XeLaTeX.

Start a new report by copying the whole folder (class, `.lua` file, `fonts/`,
`images/`) and editing `main.tex`. Compile inside that folder: the fonts are
loaded from `./fonts/`. (LuaTeX could not embed the fonts when they were given
by an absolute path that contains a space, such as `D:/Masaustu/Ideathon 2026/...`;
the relative path avoids this.)

After compiling, check the `.log` for lines with `!` or `.lua:` — if the Lua
file cannot be loaded, LaTeX still makes a PDF, but with TeX's own line breaks.

## How to use it

```latex
\documentclass{ideathon2026}
\reporttitle{LOCK-SENSE}                 % cover title, Montserrat Medium 36
\reportsubtitle{A retrofit canopy-lock alert}   % Montserrat 16
\teamname{Team Beetiful}                 % optional 2nd subtitle line
\challenge{EUROAVIA Ideathon 2026 -- EASA challenge}  % optional 3rd line
\begin{document}
\makecover          % cover page (page 1)
\tableofcontents    % "Table of Contents" page; the body starts on a new page
\section{...}       % Heading 1        "1  Title"
\subsection{...}    % Heading 2        "1.1  Title"
\subsubsection{...} % EA Title 3       "2.1.1  Title"
\paragraph{...}     % Title 4          "2.1.1.1  Title"
...
\begin{thebibliography}{99}  % numbered Heading 1 "References"
\bibitem{key} Author, "Title," ... \url{https://...}
\end{thebibliography}
\end{document}
```

* Body text: just type paragraphs. Use `\cite{key}` for "[1]" (blue `#1F5FBF`
  link, as in the EASA report). `\paragraphspacing{4.5bp}` changes the space
  after body paragraphs (template: 8 bp; the EASA report used 4.5 bp).
* Starred headings (`\section*{}`) are unnumbered but still go into the
  contents. `\section[short]{long}` gives a short contents entry.
* Lists: `itemize` (Symbol-font bullet, text at 17.85 bp, 3 bp after each
  item, as in the EASA report) and `enumerate`.
* Figures: `\begin{figure}[tb] \includegraphics[width=\linewidth]{file}
  \caption{...} \end{figure}`. Caption under the picture, Montserrat 9,
  "**Figure 1.** text", left aligned.
* Tables: `\begin{table}[tb] \caption{...}` then a `tabular` with the
  column types `L{w}`, `R{w}`, `C{w}` (left/right/centred, wrapping). `w`
  is the column width *including* the cell margins, like Word's column
  width; widths that add up to `498.9bp` fill the text width. Rules:
  `\toprule`, `\midrule`, `\bottomrule` (booktabs). Header cells:
  `\thead{...}`. Cell text is Montserrat 7.5 with 1 bp above and below.
* Straight double quotes: LaTeX turns `"` into a curly quote; write
  `\textquotedbl{}` for a straight one, or ``` ``...'' ``` for curly quotes.
* Class option `texbreaks` (`\documentclass[texbreaks]{ideathon2026}`) turns
  the Word line breaking off and uses TeX's own (usually nicer, but the lines
  then break differently from Word). `\ideathongreedyoff` / `\ideathongreedyon`
  do the same for a part of the document.
* `\settocstops{22bp}{44bp}{55bp}{77bp}` sets where the heading text starts in
  the contents for levels 1-4.

## What the class reproduces (and where the value comes from)

| Item | Value | Source |
|---|---|---|
| Page | 595.3 x 841.9 bp (A4) | `w:pgSz` 11906 x 16838 twips |
| Margins | top/bottom 99.25 bp (35.0 mm), left/right 48.2 bp (17.0 mm) | `w:pgMar` 1985 / 964 twips |
| Fonts | body Montserrat Regular 11; titles Montserrat Medium | `theme1.xml` font scheme "Ideathon" (major Montserrat Medium, minor Montserrat), run fonts in `document.xml` |
| Line spacing | 259/240 x single; single = (968+251)/1000 em; body line 14.4707 bp | `w:spacing line=259 lineRule=auto` (docDefaults), font OS/2 typo metrics |
| Paragraph spacing | body 8 bp after; between paragraphs Word uses max(after, before) | `w:after=160`; measured (body to Heading 2 = 14 bp, not 22) |
| Heading 1 | Medium 24, synthetic bold, 18 before / 6 after, number + text at 21.6 bp | `Heading1` style, `numbering.xml` level 0 (ind 432 hanging 432) |
| Heading 2 | Medium 18, synthetic bold, 14 / 12, text at 28.8 bp | `Heading2`, level 1 (576/576) |
| EA Title 3 | Medium 14, synthetic bold, 8 / 6, number at 14.2 bp, text at the next default tab (70.8 bp) | `EATitle3`, level 2 (firstLine 284, num tab 510), default tab 708 twips |
| Title 4 | Medium 14, synthetic bold, 8 / 6, number at 25.5 bp, text at 70.8 bp | `Title4`, level 3 (firstLine 510) |
| Synthetic bold | outline stroked with width size/35 (Word); `FakeBold=2.857` (luaotfload strokes FakeBold x size/100) | measured in Word PDF text render mode / line width |
| Kerning, ligatures | on in body text, off in headings and contents entries | `w:kern 2` / `w14:ligatures` in docDefaults; `kern 0`, ligatures none in heading/TOC styles |
| Colours | text black; theme accent1 #4472C4, hlink #0563C1 (defined as `ideathonAccent1`, `ideathonHyperlink`); citations/URLs #1F5FBF | `theme1.xml`; EASA document.xml |
| Header | image2.png 595.4 x 842.15 bp at (-0.1, -0.2) on every page, behind the text | `header2.xml` VML watermark, centred on the margins |
| Footer | page number, Montserrat 11, right aligned at the right margin, baseline 790.42 bp | `footer1.xml` PAGE field; baseline measured |
| Cover | image1.png at (0, 13.5) bp, 595.15 x 841.85 bp, in front of the text; white text boxes 412.25 x 45.6 and 412.25 x 33 bp at (119.3, 279.41) and (119.3, 331.0); title Medium 36 and subtitle Regular 16 at baselines 318.17 / 350.45 bp, x 126.5 bp | anchors in `document.xml` (EMU to bp), text box insets 7.2/3.6 bp; baselines measured |
| Contents | title Medium 26 synthetic bold, 18/6; entries Medium 11, 5 bp after, indents 0/11/22/33 bp, text at 22/44/55/77 bp, dot leader to the right tab 498.4 bp, page number Montserrat 11 | `TOCHeading`-like paragraph, `TOC1-4` styles, tab stops in the cached TOC |
| Widow/orphan control | on (2 lines minimum) | Word default; measured: pagination identical on the 80-paragraph holdout test |
| Hyphenation | none; break after an explicit "-" | no `autoHyphenation` in `settings.xml` |
| Captions, tables, references | as in the EASA report: captions 9 bp; table text 7.5 bp, rules 1.44/0.48 bp; references 8.5 bp, hanging indent 22.7 bp, 2.5 bp after | EASA `document.xml` + PDF |

### Word-style line breaking

Word fills each line with as many words as fit and then stretches the spaces;
TeX normally optimises the whole paragraph. To get Word's line breaks,
`ideathon2026-linebreak.lua` decides the breaks first-fit and only lets TeX
justify the lines. Measured on 450 Word lines: Word also *compresses* spaces
in justified lines; it keeps the last word on the line when the line fits with
the spaces shrunk by up to about 25 % **and** the overflow is at most about
0.37 of that word's width. The Lua file uses 25.05 % and 0.365. With these
values the LaTeX lines are identical to Word's on the template (all lines),
on the 70 paragraphs the constants were tuned on (529/529 lines) and on 80 new
paragraphs (464/468 lines = 99.1 %, same page breaks); see `tests/results.md`.
Left-aligned paragraphs (captions, references) are never compressed, as in Word.

### Fonts

`fonts/` holds the Montserrat 7.200 TrueType files that Microsoft 365
downloads to `%LOCALAPPDATA%\Microsoft\FontCache\4\CloudFonts\Montserrat`
(Word embedded these in its PDF; Montserrat is not installed in
`C:\Windows\Fonts`). Montserrat is under the SIL Open Font License, which
allows copying and modifying. The only change: the PostScript-name record
was set to the name Word writes into its PDFs (`Montserrat`, `Montserrat
Medium`, `Montserrat,Bold`, `Montserrat,Italic`), so PDF font lists read the
same. `Montserrat-BoldItalic.otf` (same version, from MiKTeX) is only used for
bold italic, which the template does not use.

## Comparison (`python compare.py`)

`compare.py` copies the template .docx to a temp folder, opens it read-only in
Word (COM) and exports `compare/word_template.pdf`, then compares it page by
page with `example_lorem.pdf` at 100 dpi and word by word (font, size, x of the
first glyph, baseline) with PyMuPDF. Options: `--no-word` reuses the Word PDF,
`--compile` runs latexmk first, `--pages 8:1` compares chosen pages,
`--word-pdf`, `--latex`, `--out`.

Result of the last run (`compare/report.md`, 5 Word pages vs 5 LaTeX pages):

| page | changed px % | changed px %, +-1 px tolerant | words W/L | matched | max dx mm | max dy mm | mean dx / dy mm | max d size pt | words > 1 mm or > 0.5 pt |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 cover | 0.06 | 0.01 | 3/3 | 3 | 0.13 | 0.00 | 0.11 / 0.00 | 0.04 | 0 |
| 2 contents | 0.48 | 0.18 | 39/35 | 31 | 3.86 | 0.04 | 0.29 / 0.02 | 0.04 | 2 |
| 3 | 3.77 | 1.29 | 449/449 | 449 | 0.13 | 0.07 | 0.03 / 0.03 | 0.04 | 0 |
| 4 | 3.69 | 1.24 | 431/431 | 431 | 0.14 | 0.06 | 0.03 / 0.03 | 0.04 | 0 |
| 5 | 2.24 | 0.84 | 286/286 | 286 | 0.13 | 0.05 | 0.03 / 0.03 | 0.04 | 0 |

All matched words have the same font after normalising the name (raw names
differ only for Montserrat Medium, see below). Line by line (text of each
printed line, 11 pt and smaller): all 94 body lines on pages 3-5 are identical
to Word's; of the 7 contents lines, 5 differ only in the number of leader dots
(`tests/run_tests.py` uses the same line extraction). I also looked at every side-by-side image and
at 300-400 dpi crops of the cover title, header band, footer, contents and
headings: no visible difference except item 1 below.

Extra checks (`python tests/run_tests.py`, `tests/results.md`): EASA reference
list [1]-[5] 12/12 lines identical with the same baselines; EASA Table 1 rules
and row baselines within 0.15 bp of Word; picture-to-caption distance 11.91 bp
(Word 11.90 bp).

## What still differs (measured)

1. **Contents, entry "1.1 Title 2": text 3.86 mm further right** (92.2 bp
   instead of 81.26 bp). The template's cached contents uses a 33 bp tab for
   this one entry and 44 bp for the other level-2 entries ("2.1", "2.2"); the
   class uses 44 bp for all. (When Word itself updates the contents of the
   template, it moves all level 2-4 texts to 48/60/72 bp — measured on a
   Word-updated copy.) Use `\settocstops` to change the stops.
2. **PDF font name of Montserrat Medium**: Word writes `Montserrat Medium`,
   LuaTeX writes `Montserrat-Medium` (it replaces the space). Same font file.
   `Montserrat` and `Montserrat,Bold` are identical.
3. **Font size in the PDF: 11.00 vs 11.04 pt** (16 vs 15.96, 14 vs 14.04,
   26 vs 26.04). Word lays out at 11 pt but draws glyphs on a 0.12 pt size
   grid. Positions are not affected (word starts within 0.14 mm); inside a
   long word Word's glyphs drift up to about 0.2 pt (0.07 mm).
4. **Line positions: up to 0.07 mm** (mean 0.03 mm). Word rounds line tops
   to a 0.12 pt grid (line pitch alternates 14.52/14.40 bp, mean 14.475 bp);
   LaTeX uses a constant 14.4707 bp. Together with item 3 this is most of the
   1.2 % "tolerant" pixel difference on the text pages (sub-pixel shifts at
   100 dpi); there is no visible difference.
5. **Line breaking outside the template text**: 2 of about 930 keep/wrap
   decisions differed on the 80-paragraph holdout set (99.1 % identical lines).
   The rule is empirical (fitted to Word's output), so a near-threshold line
   can still break differently in a new text.
6. **Contents leader dots**: Word puts dots on a 2.4 bp grid counted from the
   page edge, LaTeX from the margin (0.2 bp offset); the dot count can differ
   by one.
7. **Cover with a long title**: Word's title box has a fixed height, so a
   two-line title runs over the subtitle. The class moves the subtitle down
   instead. With a one-line title the cover is identical.
8. **Inline tables**: the EASA report put tables in the text flow (4 bp gap
   after the table); LaTeX tables float with 12 bp to the text, like the EASA
   figures. The caption and table geometry itself matches (see above).
9. **Not measured against Word**: footnotes, equations, bold italic, headings
   that wrap to two lines, two headings directly after each other (the class
   applies the measured max(after, before) rule), very long URLs without a
   hyphen (Word may break them anywhere; the class only breaks after "-").
10. The three empty paragraphs at the end of the template are not reproduced
    (they print nothing).

## Rebuilding the comparison

    latexmk -lualatex example_lorem.tex
    python compare.py            # needs Word, PyMuPDF, Pillow, numpy, pywin32
    python tests/run_tests.py    # line-breaking and EASA checks
