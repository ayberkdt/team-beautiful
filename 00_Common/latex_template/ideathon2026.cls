%% ideathon2026.cls
%% LaTeX replica of the EUROAVIA Ideathon 2026 Word report template
%% (00_Common/rules_and_templates/originals_2026-11-05/Ideathon_Template_2026.docx).
%%
%% Compile with LuaLaTeX:   latexmk -lualatex main.tex
%%                      or  lualatex main.tex   (twice, for the contents page)
%%
%% All lengths below are in bp (= the "pt" that Word uses, 1/72 inch).
%% Every number comes from the template's styles.xml / document.xml /
%% header2.xml / footer1.xml / theme1.xml or from the Word-made PDF;
%% see README.md for the source of each value.
\NeedsTeXFormat{LaTeX2e}[2023/06/01]
\ProvidesClass{ideathon2026}[2026/11/05 v1.0 EUROAVIA Ideathon 2026 report (Word template replica)]

\RequirePackage{iftex}
\ifluatex\else
  \ClassError{ideathon2026}{This class needs LuaLaTeX}%
    {Compile with: latexmk -lualatex main.tex  (or lualatex main.tex)}
\fi

% ---------------------------------------------------------------- options
\newif\ifideathon@greedyopt \ideathon@greedyopttrue
\DeclareOption{texbreaks}{\ideathon@greedyoptfalse}   % use TeX line breaking
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\RequirePackage{fix-cm}% scalable Computer Modern for the odd bp sizes (math, \verb)
\LoadClass{article}

% folder of this class (fonts/ and images/ live next to it)
% (relative to the current folder when possible: the PDF backend cannot
% embed files whose absolute path contains a space)
\directlua{ideathon2026 = require("ideathon2026-linebreak")}
\edef\ideathon@root{\directlua{tex.sprint(-2, ideathon2026.classroot())}}

% Word-like line breaking and interword spaces (ideathon2026-linebreak.lua);
% loaded before any font so that the space settings reach every font
\newcount\ideathon@greedy
\ifideathon@greedyopt \ideathon@greedy=1 \else \ideathon@greedy=0 \fi

\RequirePackage{fontspec}
\RequirePackage{graphicx}
\RequirePackage{xcolor}
\RequirePackage{array}
\RequirePackage{booktabs}
\RequirePackage{url}

% ---------------------------------------------------------------- page
% w:pgSz w=11906 h=16838 twips; w:pgMar top/bottom 1985, left/right 964 twips
%   -> 595.3 x 841.9 bp, top/bottom 99.25 bp, left/right 48.2 bp.
% Text height: Word puts a line on the page if its line box (top + line
% height) ends above the bottom margin.  TeX tests the baseline, so the
% text height is 643.4 bp minus the body line's part below the baseline
% (3.8227 bp, see \ideathon@D below).
\RequirePackage[paperwidth=595.3bp, paperheight=841.9bp,
  top=99.25bp, textheight=639.5773bp, left=48.2bp, right=48.2bp,
  headheight=0pt, headsep=0pt, footskip=0pt, nomarginpar]{geometry}
\setlength\topskip{0pt}
\setlength\maxdepth{200bp}
\raggedbottom
\setlength\parindent{0pt}
\setlength\parskip{0pt}
\frenchspacing
% Word widow/orphan control (on in Word although styles.xml does not set
% it; measured: a lone first or last line of a paragraph moves pages)
\clubpenalty=10000 \widowpenalty=10000 \displaywidowpenalty=10000
\brokenpenalty=0
\interlinepenalty=0
\lefthyphenmin=64 \righthyphenmin=64 % Word template: no automatic hyphenation
\hyphenpenalty=10000
\exhyphenpenalty=50
\hbadness=10000 \vbadness=10000 \hfuzz=0.5bp
\emergencystretch=0pt
\lineskip=0pt \lineskiplimit=0pt

% ---------------------------------------------------------------- colours
% theme1.xml (clrScheme "Office"); the template text is black (dk1).
\definecolor{ideathonText}{HTML}{000000}
\definecolor{ideathonAccent1}{HTML}{4472C4}
\definecolor{ideathonDarkTwo}{HTML}{44546A}
\definecolor{ideathonHyperlink}{HTML}{0563C1}% theme hlink
\definecolor{ideathonLink}{HTML}{1F5FBF}% citations/URLs in Team_Beetiful_EASA_Report.docx

% ---------------------------------------------------------------- fonts
% theme1.xml fontScheme "Ideathon": major = Montserrat Medium,
% minor = Montserrat.  The files in fonts/ are the Montserrat 7.200 files
% that Microsoft 365 downloads (CloudFonts cache) and that Word embedded in
% its PDF.  Word features: body text kern on (w:kern 2), ligatures
% "standardContextual"; heading/TOC styles: kern 0, ligatures none.
% Word's synthetic bold strokes the outline with width size/35;
% luaotfload strokes with FakeBold*size/100, so FakeBold = 100/35.
\def\ideathon@fontpath{\ideathon@root fonts/}
\setmainfont{Montserrat-Regular.ttf}[
  Path=\ideathon@fontpath,
  BoldFont=Montserrat-Bold.ttf,
  ItalicFont=Montserrat-Italic.ttf,
  BoldItalicFont=Montserrat-BoldItalic.otf,
  Ligatures={TeX,Common}, Kerning=On]
\setsansfont{Montserrat-Regular.ttf}[
  Path=\ideathon@fontpath,
  BoldFont=Montserrat-Bold.ttf,
  ItalicFont=Montserrat-Italic.ttf,
  BoldItalicFont=Montserrat-BoldItalic.otf,
  Ligatures={TeX,Common}, Kerning=On]
% Montserrat Medium as Word uses it in titles (kern on)
\newfontfamily\ideathon@mediumfont{Montserrat-Medium.ttf}[
  Path=\ideathon@fontpath,
  ItalicFont=Montserrat-MediumItalic.ttf,
  BoldFont=Montserrat-Medium.ttf, BoldFeatures={FakeBold=2.857143},
  BoldItalicFont=Montserrat-MediumItalic.ttf,
  BoldItalicFeatures={FakeBold=2.857143},
  Ligatures={TeX,Common}, Kerning=On]
% headings (Heading1/2, EA Title 3, Title 4, TOC heading): Medium + Word
% synthetic bold, kern 0, no ligatures
\newfontfamily\ideathon@headfont{Montserrat-Medium.ttf}[
  Path=\ideathon@fontpath, FakeBold=2.857143,
  ItalicFont=Montserrat-MediumItalic.ttf,
  Ligatures={TeX,NoCommon}, Kerning=Off]
% contents entries (TOC1..4 runs: Montserrat Medium, not bold, kern 0)
\newfontfamily\ideathon@tocfont{Montserrat-Medium.ttf}[
  Path=\ideathon@fontpath, Ligatures={TeX,NoCommon}, Kerning=Off]
% Word's bullet comes from the Symbol font (U+F0B7)
\IfFontExistsTF{symbol.ttf}
  {\newfontface\ideathon@symbolfont{symbol.ttf}
   \def\ideathon@bullet{{\ideathon@symbolfont\symbol{"F0B7}}}}
  {\def\ideathon@bullet{\textbullet}}

% ---------------------------------------------------------------- line model
% Word line height with w:lineRule="auto" w:line="259": 259/240 x the font's
% single line height; Montserrat 7.200 (USE_TYPO_METRICS) single line =
% (968 + 251)/1000 em.  Baseline = line top + 0.968 em.
%   A = 0.968 x size (part above the baseline)
%   B = line height, D = B - A (part below the baseline)
% Spacing between two paragraphs = max(space after, space before), as
% measured in the Word PDF (Heading 2 after body text: 14 bp, not 8+14).
\newdimen\ideathon@A \newdimen\ideathon@B \newdimen\ideathon@D
\newdimen\ideathon@after
\newdimen\ideathon@prevD \newdimen\ideathon@lastd
\newif\ifideathon@model \ideathon@modeltrue
\newif\ifideathon@keepnext
\def\ideathongreedyon{\ideathon@greedy=1 }
\def\ideathongreedyoff{\ideathon@greedy=0 }

% \ideathon@style{font switch}{size}{a|s}{space after}
%   a = Word "auto" 259/240 multiple (Normal style), s = single (240)
\def\ideathon@style#1#2#3#4{%
  #1%
  \ideathon@A=\dimexpr #2*968/1000\relax
  \if a#3\ideathon@B=\dimexpr #2*315721/240000\relax
  \else  \ideathon@B=\dimexpr #2*1219/1000\relax\fi
  \ideathon@D=\dimexpr\ideathon@B-\ideathon@A\relax
  \fontsize{#2}{\ideathon@B}\selectfont
  \ideathon@after=#4\relax}

\def\ideathon@parbefore{%
  \ifideathon@model
    \ifdim\prevdepth>-1000\p@
      \ifdim\prevdepth=\ideathon@lastd
        \prevdepth=\dimexpr\prevdepth+\ideathon@D-\ideathon@prevD\relax
      \else
        \prevdepth=\ideathon@D
      \fi
    \fi
  \fi}
\def\ideathon@parbegin{%
  \ifideathon@model\vrule\@height\ideathon@A\@depth\z@\@width\z@\fi}
\def\ideathon@parafter{%
  \ifideathon@model
    \global\ideathon@lastd=\prevdepth
    \global\ideathon@prevD=\ideathon@D
    \ifideathon@keepnext\nobreak\fi
    \addvspace{\ideathon@after}%
  \fi}
\AddToHook{para/before}{\ideathon@parbefore}
\AddToHook{para/begin}{\ideathon@parbegin}
\AddToHook{para/after}{\ideathon@parafter}

% Normal paragraph: Montserrat 11, justified, 8 bp after (w:after 160)
\newdimen\ideathon@bodyafter \ideathon@bodyafter=8bp
\def\ideathon@body{%
  \ideathon@style{\normalfont}{11bp}{a}{\ideathon@bodyafter}}
\renewcommand\normalsize{\fontsize{11bp}{14.4707bp}\selectfont
  \abovedisplayskip 6bp \belowdisplayskip 6bp
  \abovedisplayshortskip 3bp \belowdisplayshortskip 3bp}
\renewcommand\small{\fontsize{9bp}{11.8396bp}\selectfont}
\renewcommand\footnotesize{\fontsize{9bp}{11.8396bp}\selectfont}
\renewcommand\scriptsize{\fontsize{7.5bp}{9.8663bp}\selectfont}
\renewcommand\large{\fontsize{14bp}{18.4172bp}\selectfont}
\renewcommand\Large{\fontsize{18bp}{23.6793bp}\selectfont}
\renewcommand\LARGE{\fontsize{24bp}{31.5724bp}\selectfont}
\renewcommand\huge{\fontsize{26bp}{34.2034bp}\selectfont}
\renewcommand\Huge{\fontsize{36bp}{47.3582bp}\selectfont}
\AtBeginDocument{\ideathon@body}

% \paragraphspacing{<dimen>}: space after body paragraphs (template: 8bp;
% the EASA report used 4.5bp)
\newcommand\paragraphspacing[1]{\global\ideathon@bodyafter=#1\relax
  \ideathon@after=#1\relax}

% ---------------------------------------------------------------- tabs
% Word default tab stops every 708 twips = 35.4 bp (settings.xml).
\newdimen\ideathon@deftab \ideathon@deftab=35.4bp
\newbox\ideathon@numbox
% \ideathon@tabto{start}{stop list}: typeset \box\ideathon@numbox at
% "start" (already there) and move to the next tab stop after its end.
\def\ideathon@tabto#1#2{%
  \dimen@=\dimexpr#1+\wd\ideathon@numbox\relax
  \dimen@ii=\maxdimen
  \@tempdimb=\z@ % last explicit stop: Word uses default stops only after it
  \edef\ideathon@stops{#2}%
  \ifx\ideathon@stops\@empty\else
    \@for\ideathon@s:=\ideathon@stops\do{%
      \ifdim\ideathon@s>\@tempdimb \@tempdimb=\ideathon@s\fi
      \ifdim\ideathon@s>\dimen@
        \ifdim\ideathon@s<\dimen@ii \dimen@ii=\ideathon@s\fi\fi}%
  \fi
  \ifdim\dimen@ii=\maxdimen
    \ifdim\@tempdimb>\dimen@ \@tempdimb=\@tempdimb \else \@tempdimb=\dimen@\fi
    \@tempcnta=\numexpr\@tempdimb/\ideathon@deftab\relax
    \@tempdima=\dimexpr\ideathon@deftab*\@tempcnta\relax
    \ifdim\@tempdima>\@tempdimb\else\advance\@tempdima\ideathon@deftab\fi
    \dimen@ii=\@tempdima
  \fi
  \box\ideathon@numbox
  \hskip\dimexpr\dimen@ii-\dimen@\relax}

% ---------------------------------------------------------------- headings
% numbering.xml abstractNum 0 + styles.xml:
%  level  style       size  before after  number at  stops      wrap at
%  1      Heading1    24    18     6      0          21.6       21.6
%  2      Heading2    18    14     12     0          28.8,56.7  28.8
%  3      EATitle3    14    8      6      14.2       25.5       0
%  4      Title4      14    8      6      25.5       -          0
% All: Montserrat Medium (run override) + bold (style) = Word synthetic
% bold, black, justified, keep with next.
\setcounter{secnumdepth}{4}
\setcounter{tocdepth}{4}
\renewcommand\theparagraph{\thesubsubsection.\arabic{paragraph}}
\def\ideathon@hdef#1#2#3#4#5#6#7{%
  \@namedef{ideathon@h@size#1}{#2}%
  \@namedef{ideathon@h@before#1}{#3}%
  \@namedef{ideathon@h@after#1}{#4}%
  \@namedef{ideathon@h@start#1}{#5}%
  \@namedef{ideathon@h@stops#1}{#6}%
  \@namedef{ideathon@h@wrap#1}{#7}}
\ideathon@hdef{1}{24bp}{18bp}{6bp}{0bp}{21.6bp}{21.6bp}
\ideathon@hdef{2}{18bp}{14bp}{12bp}{0bp}{28.8bp,56.7bp}{28.8bp}
\ideathon@hdef{3}{14bp}{8bp}{6bp}{14.2bp}{25.5bp}{0bp}
\ideathon@hdef{4}{14bp}{8bp}{6bp}{25.5bp}{}{0bp}
\def\ideathon@counter#1{\ifcase#1\or section\or subsection\or
  subsubsection\or paragraph\fi}

% \ideathon@heading{level}{star?}{toc text}{title}
\def\ideathon@heading#1#2#3#4{%
  \par
  \begingroup
    \ideathon@style{\ideathon@headfont}%
      {\@nameuse{ideathon@h@size#1}}{a}{\@nameuse{ideathon@h@after#1}}%
    \addvspace{\@nameuse{ideathon@h@before#1}}%
    \ideathon@keepnexttrue
    \leftskip=\@nameuse{ideathon@h@wrap#1}\relax
    \rightskip=\z@ \parfillskip=\z@ plus 1fil\relax
    \if#2s%
      \noindent\hskip-\leftskip\hskip\@nameuse{ideathon@h@start#1}\relax
      \phantomsection
      \addcontentsline{toc}{\ideathon@counter{#1}}{#3}%
    \else
      \refstepcounter{\ideathon@counter{#1}}%
      \noindent\hskip-\leftskip\hskip\@nameuse{ideathon@h@start#1}\relax
      \setbox\ideathon@numbox\hbox{\csname the\ideathon@counter{#1}\endcsname}%
      \ideathon@tabto{\@nameuse{ideathon@h@start#1}}{\@nameuse{ideathon@h@stops#1}}%
      \addcontentsline{toc}{\ideathon@counter{#1}}%
        {\protect\numberline{\csname the\ideathon@counter{#1}\endcsname}#3}%
    \fi
    #4\par
  \endgroup}
\RenewDocumentCommand\section{s o m}{%
  \IfBooleanTF{#1}{\ideathon@heading{1}{s}{\IfValueTF{#2}{#2}{#3}}{#3}}%
                  {\ideathon@heading{1}{n}{\IfValueTF{#2}{#2}{#3}}{#3}}}
\RenewDocumentCommand\subsection{s o m}{%
  \IfBooleanTF{#1}{\ideathon@heading{2}{s}{\IfValueTF{#2}{#2}{#3}}{#3}}%
                  {\ideathon@heading{2}{n}{\IfValueTF{#2}{#2}{#3}}{#3}}}
\RenewDocumentCommand\subsubsection{s o m}{%
  \IfBooleanTF{#1}{\ideathon@heading{3}{s}{\IfValueTF{#2}{#2}{#3}}{#3}}%
                  {\ideathon@heading{3}{n}{\IfValueTF{#2}{#2}{#3}}{#3}}}
\RenewDocumentCommand\paragraph{s o m}{%
  \IfBooleanTF{#1}{\ideathon@heading{4}{s}{\IfValueTF{#2}{#2}{#3}}{#3}}%
                  {\ideathon@heading{4}{n}{\IfValueTF{#2}{#2}{#3}}{#3}}}

% ---------------------------------------------------------------- contents
% Title paragraph: Montserrat Medium 26 bold (synthetic), 18 before /
% 6 after, kern 0.  Entries (TOC1..TOC4): Montserrat Medium 11, 5 bp after
% (w:after 100), indents 0/11/22/33 bp; text tab stops 22/44/55/77 bp (the
% values in the template's TOC); dot leader + page number at the right tab
% 9968 twips = 498.4 bp, in Montserrat 11.  Word puts leader dots on a
% 2.4 bp grid.
\renewcommand\contentsname{Table of Contents}
\def\ideathon@tocdef#1#2#3{%
  \@namedef{ideathon@toc@ind#1}{#2}\@namedef{ideathon@toc@stop#1}{#3}}
\ideathon@tocdef{1}{0bp}{22bp}
\ideathon@tocdef{2}{11bp}{44bp}
\ideathon@tocdef{3}{22bp}{55bp}
\ideathon@tocdef{4}{33bp}{77bp}
\newcommand\settocstops[4]{\ideathon@tocdef{1}{0bp}{#1}%
  \ideathon@tocdef{2}{11bp}{#2}\ideathon@tocdef{3}{22bp}{#3}%
  \ideathon@tocdef{4}{33bp}{#4}}
\renewcommand\tableofcontents{%
  \par
  \begingroup
    \ideathon@style{\ideathon@headfont}{26bp}{a}{6bp}%
    \addvspace{18bp}\ideathon@keepnexttrue
    \noindent\contentsname\par
  \endgroup
  \@starttoc{toc}%
  \clearpage}
\def\ideathon@tocline#1#2#3{% level, entry, page
  \par
  \begingroup
    \ideathon@style{\normalfont}{11bp}{a}{5bp}%
    \leftskip=\@nameuse{ideathon@toc@ind#1}\relax
    \rightskip=\z@ \parfillskip=\z@
    \def\numberline##1{%
      \setbox\ideathon@numbox\hbox{\ideathon@tocfont ##1}%
      \ideathon@tabto{\@nameuse{ideathon@toc@ind#1}}%
                     {\@nameuse{ideathon@toc@stop#1}}}%
    \noindent{\ideathon@tocfont #2}%
    \nobreak\leaders\hbox to 2.4bp{.\hss}\hfill
    \nobreak\hbox{#3}\hskip 0.5bp\relax\par
  \endgroup}
\renewcommand*\l@section[2]{\ideathon@tocline{1}{#1}{#2}}
\renewcommand*\l@subsection[2]{\ideathon@tocline{2}{#1}{#2}}
\renewcommand*\l@subsubsection[2]{\ideathon@tocline{3}{#1}{#2}}
\renewcommand*\l@paragraph[2]{\ideathon@tocline{4}{#1}{#2}}

% ---------------------------------------------------------------- page decoration
% header2.xml (default header, all pages): picture watermark image2.png,
% 595.4 x 842.15 pt, centred on the margins -> drawn at x=-0.1, y=-0.2.
% footer1.xml: PAGE field, right aligned, Montserrat 11; baseline measured
% at 790.42 bp from the top in the Word PDF; right edge = right margin.
% The page number also exists on the cover (hidden under the cover image,
% exactly like in Word).
\newif\ifideathon@decoration \ideathon@decorationtrue
\setlength\unitlength{1bp}
\pagestyle{empty}
\AddToHook{shipout/background}{%
  \setlength\unitlength{1bp}%
  \ifideathon@decoration
    \put(-0.1,-841.95){\includegraphics[width=595.4bp,height=842.15bp]%
      {\ideathon@root images/page_background.png}}%
  \fi
  \put(547.1,-790.42){\llap{\normalfont\fontsize{11bp}{13.409bp}%
    \selectfont\thepage}}}

% ---------------------------------------------------------------- cover
% document.xml: image1.png anchored 0 / -1089025 EMU from paragraph 1
% (= y 13.5 bp), 7558405 x 10691495 EMU = 595.15 x 841.85 bp, in front of
% the text.  Two text boxes (white fill, no line, insets 7.2/3.6 bp):
%   title    x 119.3  y 279.41  412.25 x 45.6 bp, Montserrat Medium 36
%   subtitle x 119.3  y 331.0   412.25 x 33.0 bp, Montserrat 16
% Baselines measured in the Word PDF: 318.17 and 350.45 bp.
\def\ideathon@title{Title}
\def\ideathon@subtitle{Subtitle}
\def\ideathon@team{}
\def\ideathon@challenge{}
\newcommand\reporttitle[1]{\gdef\ideathon@title{#1}}
\newcommand\reportsubtitle[1]{\gdef\ideathon@subtitle{#1}}
\newcommand\teamname[1]{\gdef\ideathon@team{#1}}
\newcommand\challenge[1]{\gdef\ideathon@challenge{#1}}
\newdimen\ideathon@titleextra
\newcount\ideathon@titlelines
\newdimen\ideathon@subextra
\newcount\ideathon@sublines
\newcommand\makecover{%
  \begingroup
    \global\setbox\ideathon@covertitle\vtop{\hsize=397.85bp \ideathon@modelfalse
      \ideathon@mediumfont\fontsize{36bp}{47.3582bp}\selectfont
      \raggedright\noindent\ideathon@title\par
      \global\ideathon@titlelines=\prevgraf}%
    % if the title wraps, push the subtitle box down by the extra lines
    % (Word would let the text run out of its fixed-size text box)
    \global\ideathon@titleextra=\dimexpr47.3582bp*(\ideathon@titlelines-1)\relax
    \global\setbox\ideathon@coversub\vtop{\hsize=397.85bp \ideathon@modelfalse
      \normalfont\fontsize{16bp}{21.0525bp}\selectfont
      \raggedright\noindent\ideathon@subtitle
      \ifx\ideathon@team\@empty\else\newline\ideathon@team\fi
      \ifx\ideathon@challenge\@empty\else\newline\ideathon@challenge\fi\par
      \global\ideathon@sublines=\prevgraf}%
    \global\ideathon@subextra=\dimexpr21.0525bp*(\ideathon@sublines-1)\relax
  \endgroup
  \AddToHookNext{shipout/foreground}{\ideathon@drawcover}%
  \thispagestyle{empty}\null\clearpage}
\newbox\ideathon@covertitle \newbox\ideathon@coversub
\def\ideathon@drawcover{%
  \setlength\unitlength{1bp}%
  \put(0,-855.35){\includegraphics[width=595.15bp,height=841.85bp]%
    {\ideathon@root images/cover.png}}%
  \put(119.3,-325.01){\textcolor{white}{\rule{412.25bp}{45.6bp}}}%
  \put(119.3,-364){\raisebox{-\dimexpr\ideathon@titleextra+\ideathon@subextra\relax}{%
    \textcolor{white}{\rule{412.25bp}{\dimexpr33bp+\ideathon@subextra\relax}}}}%
  \put(126.5,-318.17){\box\ideathon@covertitle}%
  \put(126.5,-350.45){\raisebox{-\ideathon@titleextra}{\box\ideathon@coversub}}}

% ---------------------------------------------------------------- lists
% Bullets as in Team_Beetiful_EASA_Report.docx (numbering.xml abstractNum
% 1): Symbol bullet at 0, text at 357 twips = 17.85 bp, 3 bp after.
\newdimen\ideathon@itemafter \ideathon@itemafter=3bp
\renewenvironment{itemize}{%
  \par
  \list{\ideathon@bullet}{%
    \leftmargin=17.85bp \labelwidth=17.85bp \labelsep=0pt
    \itemindent=0pt \listparindent=0pt \rightmargin=0pt
    \topsep=0pt \partopsep=0pt \itemsep=0pt \parsep=0pt
    \def\makelabel##1{\hbox to 17.85bp{##1\hfil}}}%
  \ideathon@after=\ideathon@itemafter}
  {\endlist}
\renewenvironment{enumerate}{%
  \par
  \advance\@enumdepth\@ne
  \edef\@enumctr{enum\romannumeral\the\@enumdepth}%
  \list{\csname label\@enumctr\endcsname}{%
    \usecounter{\@enumctr}%
    \leftmargin=17.85bp \labelwidth=17.85bp \labelsep=0pt
    \itemindent=0pt \listparindent=0pt \rightmargin=0pt
    \topsep=0pt \partopsep=0pt \itemsep=0pt \parsep=0pt
    \def\makelabel##1{\hbox to 17.85bp{##1\hfil}}}%
  \ideathon@after=\ideathon@itemafter}
  {\endlist}

% ---------------------------------------------------------------- figures, tables
% As in Team_Beetiful_EASA_Report.docx (the filled report made from this
% template); values measured in its Word PDF:
%  * caption: Montserrat 9, "Figure 1." / "Table 1." bold, rest regular,
%    left aligned, Word line spacing (11.84 bp pitch);
%  * figure: picture, then caption; picture bottom to caption line top
%    3.2 bp (picture paragraph 2 bp after + Word's line box);
%  * table: caption above, 4 bp (w:after 80) from caption line bottom to
%    the top rule;
%  * floats keep 12 bp (w:topFromText / bottomFromText 240) from the text.
\setlength\textfloatsep{12bp plus 0bp minus 0bp}
\setlength\floatsep{12bp plus 0bp minus 0bp}
\setlength\intextsep{12bp plus 0bp minus 0bp}
\setlength\abovecaptionskip{0pt}
\setlength\belowcaptionskip{0pt}
% let floats use most of a page; float-only pages start at the top
\renewcommand\topfraction{0.9}
\renewcommand\bottomfraction{0.9}
\renewcommand\textfraction{0.05}
\renewcommand\floatpagefraction{0.8}
\setcounter{topnumber}{3}
\setcounter{bottomnumber}{3}
\setcounter{totalnumber}{4}
\setlength\@fptop{0pt}
\setlength\@fpsep{12bp}
\setlength\@fpbot{0pt plus 1fil}
\renewcommand\figurename{Figure}
\renewcommand\tablename{Table}
\newdimen\ideathon@figcapgap \ideathon@figcapgap=3.2bp
\newdimen\ideathon@tabcapgap \ideathon@tabcapgap=4bp
\long\def\@makecaption#1#2{%
  \par
  \removelastskip
  \ifx\@captype\ideathon@figtype \vskip\ideathon@figcapgap \fi
  \nointerlineskip
  \begingroup
    \ideathon@style{\normalfont}{9bp}{a}{0bp}%
    \raggedright
    \noindent\vrule\@height\ideathon@A\@depth\z@\@width\z@
    {\bfseries #1.} #2\vrule\@height\z@\@depth\ideathon@D\@width\z@\par
  \endgroup
  \ifx\@captype\ideathon@figtype\else\vskip\ideathon@tabcapgap\nointerlineskip\fi}
\def\ideathon@figtype{figure}
% inside floats the paragraph model is off: the picture line is exactly
% as high as the picture, as in Word
\g@addto@macro\@floatboxreset{\ideathon@modelfalse\centering}

% Tables (EASA report): cell text Montserrat 7.5, single line spacing
% (9.1425 bp), 1 bp before and after each cell paragraph, cell margins
% 57 twips = 2.85 bp, rules 1.44 bp (top, bottom) and 0.48 bp (below the
% header) as Word draws them.  One-line row = 1 + 9.1425 + 1 bp.
\setlength\heavyrulewidth{1.44bp}
\setlength\lightrulewidth{0.48bp}
\setlength\cmidrulewidth{0.48bp}
\setlength\aboverulesep{0pt}
\setlength\belowrulesep{0pt}
\setlength\cmidrulesep{0pt}
\setlength\tabcolsep{2.85bp}
\newcommand\tablefont{%
  \fontsize{7.5bp}{9.1425bp}\selectfont
  \setbox\strutbox\hbox{\vrule\@height\dimexpr7.5bp*968/1000+1bp\relax
    \@depth\dimexpr9.1425bp-7.5bp*968/1000+1bp\relax\@width\z@}%
  \renewcommand\arraystretch{1}%
  \setlength\extrarowheight{0pt}}
\AddToHook{env/tabular/begin}{\ideathon@modelfalse}
\AddToHook{env/tabular*/begin}{\ideathon@modelfalse}
\def\ideathon@tabtype{table}
\g@addto@macro\@floatboxreset{\ifx\@captype\ideathon@tabtype\tablefont\fi}
% column types with the width Word would show for the column (cell
% margins included), e.g.  L{67.5bp} = w:tcW 1350
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{\dimexpr#1-2\tabcolsep\relax}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{\dimexpr#1-2\tabcolsep\relax}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{\dimexpr#1-2\tabcolsep\relax}}
% table header cells in bold: \thead{...}
\providecommand\thead[1]{\textbf{#1}}

% ---------------------------------------------------------------- references
% As in Team_Beetiful_EASA_Report.docx: numbered Heading 1 "References",
% entries Montserrat 8.5, "[n]" + tab at 454 twips = 22.7 bp, hanging
% indent 22.7 bp, 2.5 bp after, URLs in #1F5FBF.
\renewcommand\refname{References}
\renewenvironment{thebibliography}[1]{%
  \section{\refname}%
  \list{\@biblabel{\@arabic\c@enumiv}}{%
    \leftmargin=22.7bp \labelwidth=22.7bp \labelsep=0pt
    \itemindent=0pt \listparindent=0pt \rightmargin=0pt
    \topsep=0pt \partopsep=0pt \itemsep=0pt \parsep=0pt
    \def\makelabel##1{\hbox to 22.7bp{##1\hfil}}%
    \usecounter{enumiv}\let\p@enumiv\@empty
    \renewcommand\theenumiv{\@arabic\c@enumiv}}%
  \ideathon@style{\normalfont}{8.5bp}{a}{2.5bp}%
  \raggedright
  \sloppy\clubpenalty0\widowpenalty0\sfcode`\.\@m}
  {\def\@noitemerr{\@latex@warning{Empty `thebibliography' environment}}%
   \endlist}
\urlstyle{same}
% Word breaks URLs only after a hyphen (seen in the EASA reference list)
\def\UrlBreaks{\do\-}\def\UrlBigBreaks{}
\mathchardef\UrlBigBreakPenalty=10000 % no break after ":" etc.

% ---------------------------------------------------------------- hyperref
\RequirePackage[pdfborder={0 0 0}, colorlinks=true, linkcolor=black,
  citecolor=ideathonLink, urlcolor=ideathonLink, bookmarksnumbered=true,
  pdfcreator={LaTeX ideathon2026.cls}]{hyperref}
\AtBeginDocument{\hypersetup{pdftitle={\ideathon@title}, pdfauthor={\ideathon@team}}}

\endinput
