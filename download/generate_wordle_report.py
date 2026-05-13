#!/usr/bin/env python3
"""Generate Wordle Analyzer Competitive Feature Research Report PDF."""

import os, sys, hashlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, CondPageBreak, Image
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import SimpleDocTemplate

# ━━ Color Palette (auto-generated) ━━
ACCENT       = colors.HexColor('#1e95bd')
TEXT_PRIMARY  = colors.HexColor('#201f1d')
TEXT_MUTED    = colors.HexColor('#8d8981')
BG_SURFACE   = colors.HexColor('#e6e4e1')
BG_PAGE      = colors.HexColor('#f1efed')

TABLE_HEADER_COLOR = ACCENT
TABLE_HEADER_TEXT  = colors.white
TABLE_ROW_EVEN     = colors.white
TABLE_ROW_ODD      = BG_SURFACE

# ━━ Font Registration ━━
pdfmetrics.registerFont(TTFont('LiberationSerif', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerif-Bold', '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSans', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSans-Bold', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))
registerFontFamily('LiberationSerif', normal='LiberationSerif', bold='LiberationSerif-Bold')
registerFontFamily('LiberationSans', normal='LiberationSans', bold='LiberationSans-Bold')
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans')

# ━━ Page Setup ━━
PAGE_W, PAGE_H = A4
LEFT_MARGIN = 1.0 * inch
RIGHT_MARGIN = 1.0 * inch
TOP_MARGIN = 0.8 * inch
BOTTOM_MARGIN = 0.8 * inch
CONTENT_WIDTH = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN

# ━━ Styles ━━
styles = getSampleStyleSheet()

cover_title_style = ParagraphStyle(
    'CoverTitle', fontName='LiberationSerif', fontSize=36, leading=44,
    alignment=TA_CENTER, textColor=ACCENT, spaceAfter=20
)
cover_subtitle_style = ParagraphStyle(
    'CoverSubtitle', fontName='LiberationSerif', fontSize=16, leading=22,
    alignment=TA_CENTER, textColor=TEXT_MUTED, spaceAfter=10
)
cover_meta_style = ParagraphStyle(
    'CoverMeta', fontName='LiberationSerif', fontSize=12, leading=16,
    alignment=TA_CENTER, textColor=TEXT_MUTED
)

h1_style = ParagraphStyle(
    'H1Style', fontName='LiberationSerif', fontSize=22, leading=28,
    textColor=ACCENT, spaceBefore=18, spaceAfter=10
)
h2_style = ParagraphStyle(
    'H2Style', fontName='LiberationSerif', fontSize=16, leading=22,
    textColor=TEXT_PRIMARY, spaceBefore=14, spaceAfter=8
)
h3_style = ParagraphStyle(
    'H3Style', fontName='LiberationSerif', fontSize=13, leading=18,
    textColor=ACCENT, spaceBefore=10, spaceAfter=6
)
body_style = ParagraphStyle(
    'BodyStyle', fontName='LiberationSerif', fontSize=10.5, leading=17,
    alignment=TA_JUSTIFY, textColor=TEXT_PRIMARY, spaceAfter=6
)
body_left_style = ParagraphStyle(
    'BodyLeftStyle', fontName='LiberationSerif', fontSize=10.5, leading=17,
    alignment=TA_LEFT, textColor=TEXT_PRIMARY, spaceAfter=4
)
bullet_style = ParagraphStyle(
    'BulletStyle', fontName='LiberationSerif', fontSize=10.5, leading=17,
    alignment=TA_LEFT, textColor=TEXT_PRIMARY, spaceAfter=3,
    leftIndent=18, bulletIndent=6
)
link_style = ParagraphStyle(
    'LinkStyle', fontName='LiberationSerif', fontSize=10, leading=15,
    alignment=TA_LEFT, textColor=ACCENT, spaceAfter=3
)
caption_style = ParagraphStyle(
    'CaptionStyle', fontName='LiberationSerif', fontSize=9, leading=13,
    alignment=TA_CENTER, textColor=TEXT_MUTED, spaceBefore=3, spaceAfter=6
)
toc_h1_style = ParagraphStyle(
    'TOCH1', fontName='LiberationSerif', fontSize=13, leftIndent=20,
    spaceBefore=4, spaceAfter=2
)
toc_h2_style = ParagraphStyle(
    'TOCH2', fontName='LiberationSerif', fontSize=11, leftIndent=40,
    spaceBefore=2, spaceAfter=2
)
header_cell_style = ParagraphStyle(
    'HeaderCell', fontName='LiberationSerif', fontSize=10, leading=14,
    alignment=TA_CENTER, textColor=colors.white
)
cell_style = ParagraphStyle(
    'CellStyle', fontName='LiberationSerif', fontSize=9.5, leading=14,
    alignment=TA_LEFT, textColor=TEXT_PRIMARY
)
cell_center_style = ParagraphStyle(
    'CellCenter', fontName='LiberationSerif', fontSize=9.5, leading=14,
    alignment=TA_CENTER, textColor=TEXT_PRIMARY
)

# ━━ TocDocTemplate ━━
class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            level = getattr(flowable, 'bookmark_level', 0)
            text = getattr(flowable, 'bookmark_text', '')
            key = getattr(flowable, 'bookmark_key', '')
            self.notify('TOCEntry', (level, text, self.page, key))

def add_heading(text, style, level=0):
    key = 'h_%s' % hashlib.md5(text.encode()).hexdigest()[:8]
    p = Paragraph('<a name="%s"/>%s' % (key, text), style)
    p.bookmark_name = text
    p.bookmark_level = level
    p.bookmark_text = text
    p.bookmark_key = key
    return p

H1_ORPHAN_THRESHOLD = (PAGE_H - TOP_MARGIN - BOTTOM_MARGIN) * 0.15

def add_major_section(text, style):
    return [
        CondPageBreak(H1_ORPHAN_THRESHOLD),
        add_heading(text, style, level=0),
    ]

def make_table(data, col_widths, caption_text=None):
    """Create a styled table with optional caption."""
    t = Table(data, colWidths=col_widths, hAlign='CENTER')
    row_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
        ('GRID', (0, 0), (-1, -1), 0.5, TEXT_MUTED),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        bg = TABLE_ROW_EVEN if i % 2 == 1 else TABLE_ROW_ODD
        row_styles.append(('BACKGROUND', (0, i), (-1, i), bg))
    t.setStyle(TableStyle(row_styles))
    elements = [Spacer(1, 18), t]
    if caption_text:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(caption_text, caption_style))
    elements.append(Spacer(1, 18))
    return elements

# ━━ Build Document ━━
OUTPUT_PATH = '/home/z/my-project/download/Wordle_Analyzer_Feature_Research_Report.pdf'

doc = TocDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    leftMargin=LEFT_MARGIN,
    rightMargin=RIGHT_MARGIN,
    topMargin=TOP_MARGIN,
    bottomMargin=BOTTOM_MARGIN,
    title='Wordle Analyzer Competitive Feature Research Report',
    author='Z.ai',
    creator='Z.ai',
)

story = []

# ━━ COVER PAGE ━━
story.append(Spacer(1, 2.2 * inch))
story.append(Paragraph('<b>Wordle Analyzer</b>', cover_title_style))
story.append(Paragraph('<b>Competitive Feature Research Report</b>', ParagraphStyle(
    'CoverTitle2', fontName='LiberationSerif', fontSize=28, leading=36,
    alignment=TA_CENTER, textColor=TEXT_PRIMARY, spaceAfter=30
)))
story.append(Spacer(1, 0.5 * inch))
story.append(Paragraph('Comprehensive Analysis of 30+ Similar Projects, Tools, and Open-Source Repositories', cover_subtitle_style))
story.append(Spacer(1, 0.3 * inch))
story.append(Paragraph('Feature Suggestions for wordleanalyzer.dev Homepage Enhancement', cover_subtitle_style))
story.append(Spacer(1, 1.0 * inch))
story.append(Paragraph('Prepared for: Wordle Analyzer Development Team', cover_meta_style))
story.append(Paragraph('Date: May 14, 2026', cover_meta_style))
story.append(Paragraph('Generated by: Z.ai Research', cover_meta_style))
story.append(PageBreak())

# ━━ TABLE OF CONTENTS ━━
story.append(Paragraph('<b>Table of Contents</b>', ParagraphStyle(
    'TOCTitle', fontName='LiberationSerif', fontSize=22, leading=28,
    alignment=TA_CENTER, textColor=ACCENT, spaceAfter=20
)))
toc = TableOfContents()
toc.levelStyles = [toc_h1_style, toc_h2_style]
story.append(toc)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 1: EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════
story.extend(add_major_section('<b>1. Executive Summary</b>', h1_style))
story.append(Paragraph(
    'This report presents a comprehensive competitive analysis of the Wordle Analyzer tool landscape, '
    'encompassing over 30 web-based tools, open-source GitHub repositories, browser extensions, and mobile '
    'applications. The research was conducted to identify feature gaps, innovative capabilities, and strategic '
    'opportunities for enhancing the wordleanalyzer.dev homepage. Each project was evaluated for its unique '
    'features, algorithms, user interface design, and the specific capabilities that could be adapted or '
    'improved upon for our platform.',
    body_style
))
story.append(Paragraph(
    'The analysis reveals that while several tools offer basic post-game analysis and word suggestions, '
    'very few combine comprehensive analysis with an intuitive, free user experience. The NYT WordleBot remains '
    'the gold standard but is paywalled, creating a significant opportunity for free alternatives. Key differentiating '
    'features that are underrepresented in the market include skill/luck scoring, entropy visualization, unused clue '
    'detection, longitudinal performance tracking, and multi-variant game support. This report identifies the most '
    'impactful features to add, organized by priority level, with specific references to the source projects that '
    'inspire each recommendation.',
    body_style
))

# ══════════════════════════════════════════════════════════════════════
# SECTION 2: WEB-BASED TOOLS
# ══════════════════════════════════════════════════════════════════════
story.extend(add_major_section('<b>2. Web-Based Competitive Tools</b>', h1_style))
story.append(Paragraph(
    'This section covers the major web-based Wordle analysis and solver tools discovered during our research. '
    'Each tool is described with its URL, complete feature list, and the specific features we recommend '
    'incorporating into wordleanalyzer.dev.',
    body_style
))

# --- 2.1 NYT WordleBot ---
story.append(add_heading('<b>2.1 NYT WordleBot</b>', h2_style, level=1))
story.append(Paragraph('URL: https://www.nytimes.com/interactive/2022/upshot/wordle-bot.html', link_style))
story.append(Paragraph('Type: Post-game analyzer (Paywalled - requires NYT subscription)', body_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Skill score (0-99) and Luck score (0-99) for each guess and overall game, mathematically separating decision quality from outcomes',
    'Step-by-step comparison showing what the bot would have guessed at each turn versus your actual guess',
    'Screenshot upload capability for automatic parsing of completed Wordle games',
    'Rolling 14-day average tracking of skill, luck, and number of steps across multiple games',
    '90-day game history window to review past game performance and identify improvement patterns',
    'Remaining solutions counter showing how many possible answers remained after each guess',
    'Opening word recommendation engine, currently recommending TRACE (previously SLATE)',
    'Hard mode analysis with separate strategy recommendations and compliance checking',
    'Word frequency weighting that considers how common or uncommon suggested words are',
    'Population comparison benchmarks showing how your performance compares to NYT average players',
    'Guess efficiency metrics quantifying how many answers your guess eliminated versus the optimal guess',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Skill and Luck Scoring System:</b> This is the single most impactful feature to add. No free tool currently offers this capability. Implementing a 0-99 skill/luck decomposition for each guess would immediately position wordleanalyzer.dev as the premier free alternative to the paywalled WordleBot.',
    '<b>Longitudinal Tracking:</b> Rolling averages and game history over time. Only the NYT WordleBot offers this (paywalled). A free dashboard showing 14-day rolling skill/luck averages would be highly compelling and drive repeat visits.',
    '<b>Per-Guess Efficiency Metrics:</b> Show exactly how many answers each guess eliminated compared to the optimal guess. This educational feature helps players understand why certain guesses are better than others.',
    '<b>Opening Word Recommendation Engine:</b> A dedicated section ranking the best starting words with explanations of why each is strong (information gain, letter coverage, positional frequency).',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.2 Wordle Analyzer (wordle-analyzer.com) ---
story.append(add_heading('<b>2.2 Wordle Analyzer (wordle-analyzer.com)</b>', h2_style, level=1))
story.append(Paragraph('URL: https://wordle-analyzer.com', link_style))
story.append(Paragraph('Creator: Jake Archibald (Google Chrome developer) | Open Source: Yes', body_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Post-game guess input with the correct answer to receive full analysis of your play',
    'Hard mode toggle to switch analysis between normal and hard mode constraints',
    'Interactive guess grid with visual tile-by-tile color-coded input matching the Wordle aesthetic',
    'Remaining words display after each guess showing the complete list of possible answers that were still viable',
    'Per-guess analysis table showing how many possible answers remained before and after each guess, how many were eliminated, and the percentage of possibilities eliminated',
    'Unused clue detection that highlights information in your guess that you did not use, such as yellow letters you failed to reposition in subsequent guesses',
    'AI comparison showing what an optimal bot would have guessed in your situation side-by-side with your actual play',
    'Spoiler warning before revealing answer information in shared links',
    'Shareable analysis links allowing you to generate a URL to share your complete analysis with others',
    'Dark mode auto-detected from system preference',
    'Progress bar visualization showing the reduction in remaining words as a visual gauge',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Unused Clue Detection:</b> This is an exceptionally valuable feature that wordle-analyzer.com is currently the only tool offering. Implementing and improving upon it (e.g., "you had a yellow A in row 2 but did not try it in position 3 in row 3") would differentiate our tool significantly.',
    '<b>Shareable Analysis URLs with Spoiler Warning:</b> The ability to share your game analysis via a link (with spoiler protection) creates social virality and drives traffic. This is a proven growth mechanism.',
    '<b>Side-by-Side Player vs. Bot Comparison:</b> Showing your actual guesses next to what the optimal bot would have played at each step is the most engaging way to present analysis and makes the tool genuinely educational.',
    '<b>Progress Bar for Word Elimination:</b> A simple visual progress bar showing what percentage of remaining words each guess eliminates makes the analysis immediately understandable even for non-technical users.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.3 ConnectionsSolver ---
story.append(add_heading('<b>2.3 ConnectionsSolver Wordle Analyzer and Bot</b>', h2_style, level=1))
story.append(Paragraph('URL: https://connectionssolver.com/wordle-analyzer', link_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Dual mode: Wordle Analyzer mode provides a ranked list of suggestions, and Wordle Bot mode provides a guided step-by-step optimal path to the answer',
    'AI-powered analysis that calculates the best statistical move to narrow down possibilities at each step',
    'Step-by-step bot walkthrough from optimal starting word to final answer, explaining the strategy at each stage',
    'Color-coded letter input system for marking letters as green, yellow, or gray',
    'Mobile responsive design that works well on phones and tablets',
    'Cross-puzzle ecosystem including Connections answers, Letter Boxed answers, and archive tools',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Dual Analyzer + Bot Mode:</b> Offering both a "rate my game" mode (post-game analysis) and a "bot guide" mode (step-by-step optimal path) in a single interface gives users two compelling reasons to visit. The bot mode is particularly engaging for players actively working through a puzzle.',
    '<b>AI-Powered Natural Language Commentary:</b> Instead of just showing raw metrics, provide conversational analysis like "Your second guess was solid - it eliminated 89% of remaining words, but you got unlucky that the A was already ruled out." This makes analysis accessible and engaging for all skill levels.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.4 Yuval's WordleBot ---
story.append(add_heading('<b>2.4 Yuval Ben-Hayun WordleBot</b>', h2_style, level=1))
story.append(Paragraph('URL: https://ybenhayun.github.io/wordlebot', link_style))
story.append(Paragraph('GitHub: https://github.com/ybenhayun/wordlebot', link_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Configurable word length from 3 to 11 letters (not just the standard 5-letter Wordle)',
    'Configurable maximum guesses from 3 to 21',
    'Answer source selection between "Most Likely Answers" (official list only) and "All Possible Answers" (extended word list)',
    'Support for 13+ game variants: Standard Wordle, Antiwordle, Xordle, Fibble, Warmle, Hardle, Woodle/Word500, Wordle Peaks, Thirdle, Dordle, Quordle, Octordle, Spotle',
    'Ranked best starting words showing top 10 guesses with expected guesses metric (e.g., SALET = 3.421 average)',
    'Hard mode support with separate hard mode rankings',
    'Live bot simulation mode to watch the bot solve interactively',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Multi-Variant Game Support:</b> Supporting Dordle, Quordle, Octordle, and other popular Wordle variants would dramatically expand our addressable audience. Yuval\'s tool is the only one supporting 13+ variants, and many players regularly play these spin-off games.',
    '<b>Expected Guesses Metric:</b> Showing the mathematical expected number of guesses for each suggested word (e.g., "SALET: 3.42 avg") provides concrete data for players to compare strategies, rather than just ranking words abstractly.',
    '<b>Configurable Word Length:</b> Supporting 3-11 letter word lengths opens the tool to players of Wordle variants like Hello Wordl and other custom-length games. This is a genuinely unique feature.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.5 WordleBot.net ---
story.append(add_heading('<b>2.5 WordleBot.net (Calcle)</b>', h2_style, level=1))
story.append(Paragraph('URL: https://wordlebot.net', link_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Wordle Calcle mode: enter guesses with color-coded tiles and get optimal next guess recommendations',
    'Double-click to batch apply colors: double-click a color to lock it, double-click a letter to cycle through colors',
    'Hard mode support with constraint enforcement',
    'Partial word entry capability allowing calculations without filling in the complete word',
    'Likely versus unlikely word list toggle to view both probable answers and extended valid words',
    'Featured Wordle Games section curating alternative Wordle games (Custom Wordle, Betweenle, Phonenumble)',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Double-Click Color Cycling:</b> Making the color assignment UI faster with double-click to batch-apply colors significantly improves the user experience, especially for power users who analyze multiple games daily.',
    '<b>Partial Word Entry:</b> Allowing analysis even when the complete word grid is not filled in gives users flexibility and makes the tool more useful mid-game, not just post-game.',
    '<b>Game Discovery Hub:</b> A curated section featuring alternative Wordle games and variants positions the site as a comprehensive destination for Wordle enthusiasts, not just a single-purpose tool.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.6 Wordle Tools ---
story.append(add_heading('<b>2.6 Wordle Tools (Comprehensive Suite)</b>', h2_style, level=1))
story.append(Paragraph('URL: https://wordletools.azurewebsites.net', link_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Moredle: Post-game analysis similar to Scoredle but with additional information depth',
    'Griddle: Alternative front end with a Wordle-like grid and on-screen keyboard for interactive input',
    'Even Moredle: Combines Moredle analysis with bot comparison showing what multiple bots would do',
    'Game Difficulty Scorecard: Generates a difficulty rating for any historical Wordle puzzle',
    'Score Card: Ranking scorecard for any potential starter word evaluated across multiple metrics',
    'Starter Ranking: Top starter words ranked by 5 different scoring metrics or overall composite',
    'Second String: Ranks second-guess words by any combination of 5 metrics',
    'Solver: Solves any Wordle using 5 different solving methods',
    'Pattern Matcher: Find solutions matching specific letter patterns',
    'Letter Stats: Comprehensive letter frequency statistics for strategy optimization',
    'Double Trouble: Identifies words with double (or more) letters that commonly trip up players',
    'Pillars of Doom: Identifies particularly troublesome patterns and associated words',
    'NYT Word List Change Checker: Detects if NYT has modified its word lists between updates',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Game Difficulty Scorecard:</b> This is a unique and highly shareable feature. Allowing users to enter any date or word and see a difficulty rating (with explanation of why it was hard or easy) creates engaging, shareable content. No other free tool offers this.',
    '<b>5-Method Solver Comparison:</b> Showing how different algorithmic approaches (entropy, frequency, positional, minimax, hybrid) would solve the same puzzle side-by-side is both educational and fascinating for technically-minded users.',
    '<b>Pillars of Doom Analysis:</b> Identifying common trap patterns (like -IGHT words where NIGHT, LIGHT, RIGHT, MIGHT, FIGHT, TIGHT, SIGHT, EIGHT are all possible) and teaching players how to navigate them is a unique content feature that no one else offers in a consumer-friendly way.',
    '<b>Starter Word Ranking by Multiple Metrics:</b> Instead of just one "best word," provide a multi-dimensional ranking showing the best opener for average speed, worst-case safety, hard mode, and other criteria. This is more useful than a single recommendation.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.7 Scoredle ---
story.append(add_heading('<b>2.7 Scoredle</b>', h2_style, level=1))
story.append(Paragraph('URL: https://scoredle.com', link_style))
story.append(Paragraph('Creators: Brandon Wallace, Kyle Wallace, Rhett Rainen', body_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Rate your Wordle guesses: enter guesses and answer to see how well you played',
    'Share functionality to share your Scoredle analysis results with friends and on social media',
    'Scoodle variant for Woodle (a Wordle variant) at woodle.scoredle.com',
    'Clear and reset functionality for analyzing multiple games',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Feature:</b>', body_left_style))
story.append(Paragraph(
    '<b>Share Results Feature:</b> Scoredle pioneered the "rate my game and share" concept. Adding a share '
    'button that generates an emoji-grid summary of the analysis (similar to how Wordle shares are shared, but '
    'with analysis metrics included) creates social virality and drives organic traffic to wordleanalyzer.dev.',
    body_style
))

# --- 2.8 The Word Finder ---
story.append(add_heading('<b>2.8 The Word Finder Wordle Solver</b>', h2_style, level=1))
story.append(Paragraph('URL: https://www.thewordfinder.com/wordle-solver', link_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Best Possible Letters suggestion: recommends which letters are most likely to appear next (not just words, but individual letter recommendations)',
    'Green/Yellow/Gray letter input sections with position-specific filtering',
    'Letter position filters for specifying which positions letters are in or not in',
    'Hard mode enforcement ensuring every yellow letter appears in future guesses',
    'Frequency heatmaps (2025 update) where letters glow hotter by appearance odds, providing an intuitive visual representation of letter likelihood',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Best Possible Letters Suggestion:</b> Recommending not just which words to guess, but which individual letters are most likely to appear, is a unique and underrepresented feature. This helps players who want to think for themselves but need guidance on which letters to probe.',
    '<b>Frequency Heatmap Visualization:</b> A visual heatmap showing letter frequency by position (which letters are most common in position 1, position 2, etc.) among remaining possible answers is both beautiful and informative. This goes beyond simple word lists to provide strategic insight.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.9 Word.tips ---
story.append(add_heading('<b>2.9 Word.tips Wordle Answer Finder</b>', h2_style, level=1))
story.append(Paragraph('URL: https://word.tips/wordle', link_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Progressive hint system with multiple levels of increasing specificity: hint 1 is vague, hint 2 is moderate, hint 3 is specific, giving players control over how much help they receive',
    'Past Wordle answers archive: complete searchable database of all historical Wordle answers',
    'Word frequency sorting: results sorted by how common or frequent words are in English usage',
    'Daily puzzle commentary and difficulty analysis updated each day',
    'Common letter frequency statistics and strategy advice',
    'Word definitions integrated with suggestions so players can verify word meanings',
    'Mobile app available for iOS and Android as a dedicated solver application',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Progressive Hint System:</b> Multiple hint levels (vague, moderate, specific) for players who want some help but not the full answer is a brilliant UX feature that respects different play styles. This could be a dedicated "hint mode" button that progressively reveals more information.',
    '<b>Past Wordle Answers Archive:</b> A searchable database of all historical Wordle answers is excellent for SEO (people search for past answers) and serves as a reference tool. This drives organic search traffic.',
    '<b>Word Frequency Ranking:</b> Sorting suggestions by how common the word is in English helps players prioritize guessing familiar words first, which is a practical and user-friendly approach.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.10 Jonathan Olson ---
story.append(add_heading('<b>2.10 Jonathan Olson Optimal Wordle Solver</b>', h2_style, level=1))
story.append(Paragraph('URL: https://jonathanolson.net/wordle-solver', link_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Interactive decision tree: click a starting guess and see the optimal path from there',
    'Click letters to change colors, matching your result, then get the next optimal guess',
    'Three optimization strategies: Fastest Average (SALET at 3.421 avg), Fewest 5+ Guesses (minimizes worst case), and Hard Mode',
    'Pre-computed decision trees loaded entirely client-side for instant results',
    'Thumbnail options showing alternative guesses below the main suggestion',
    'Mathematically proven optimal at approximately 3.42 guesses per win',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Interactive Decision Tree Visualization:</b> Showing the full decision tree for a game, where each node represents a guess and branches represent possible outcomes, is a powerful educational tool. Players can explore "what if" scenarios by clicking different branches.',
    '<b>Multiple Optimization Strategies:</b> Let users choose between "fastest average," "safest worst case," and "hard mode" strategies. Different play styles benefit from different optimization goals, and offering this choice adds depth.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.11 HelpWordle ---
story.append(add_heading('<b>2.11 HelpWordle.com</b>', h2_style, level=1))
story.append(Paragraph('URL: https://helpwordle.com', link_style))
story.append(Paragraph('<b>Key Features:</b>', body_left_style))
for feat in [
    'Four input categories: Correct letters (green), Present letters (yellow), Excluded letters (gray), and uniquely "Letters not in specific position" (red boxes for position-specific exclusions)',
    'Daily hints updated for each day\'s puzzle',
    'Expert tips and strategies section covering strong opening words, avoiding reusing eliminated letters, letter repetition warnings, the Y strategy when E is eliminated, and strategic elimination techniques',
    'FAQ section with best starting words and whether plural words are valid',
]:
    story.append(Paragraph(feat, bullet_style, bulletText='\xe2\x80\xa2'))
story.append(Paragraph('<b>Suggested Features for wordleanalyzer.dev:</b>', body_left_style))
for s in [
    '<b>Position-Specific Exclusion Input:</b> The "letters not in specific position" red box is a 4th input category beyond green/yellow/gray that no other tool offers. This handles the nuanced case where a letter is known to be in the word (yellow) but you also know which position it is NOT in. Adding this filter improves suggestion accuracy.',
    '<b>Built-in Strategy Education:</b> A dedicated strategy tips section with expert advice on opening words, common patterns, and advanced techniques transforms the tool from a solver into a learning platform. This content also boosts SEO significantly.',
]:
    story.append(Paragraph(s, bullet_style, bulletText='\xe2\x80\xa2'))

# --- 2.12 Additional Notable Web Tools ---
story.append(add_heading('<b>2.12 Additional Notable Web Tools</b>', h2_style, level=1))

addl_tools = [
    ('Wordle Calculator', 'https://wordlecalculator.digital', 'Longitudinal tracking with streak trends, safest vs. riskiest play style analysis, average guesses calculation over time. Suggest adding: play style categorization and streak probability tracking.'),
    ('Engaging Data Wordle Stats', 'https://engaging-data.com/wordle-guess-distribution', 'Community-level difficulty metrics showing global guess distribution per puzzle, per-puzzle difficulty ranking, historical difficulty comparison. Suggest adding: global player comparison and puzzle difficulty timeline.'),
    ('Wordle Analyser (Azure)', 'https://wordleanalyser.azurewebsites.net', 'On-screen QWERTY keyboard input, color-cycling boxes for mobile-friendly interaction, "Only wordle words" toggle, matching words counter. Suggest adding: on-screen keyboard for mobile input and "official words only" filter.'),
    ('WordleSolver.app', 'https://wordlesolver.app', 'Entropy scoring for each suggestion, explicit Dordle/Quordle/Octordle support, dark mode. Suggest adding: entropy bits display per suggestion and multi-game variant support.'),
    ('Wordle Stats Explorer (Chrome Extension)', 'https://chromewebstore.google.com/detail/wordle-stats-explorer/ighphnklonadnnfcfjccgmggddnhbaek', 'Automatic game tracking, full statistics dashboard, game history timeline, performance trends. Created by Mark Russinovich (Microsoft). Suggest adding: browser extension for automatic game detection and performance trend charts.'),
    ('Collins Dictionary Wordle Helper', 'https://www.collinsdictionary.com/us/games/wordle-helper', 'Dictionary-backed solver with authoritative word lists, word definitions integration. Suggest adding: word definitions alongside suggestions so players can verify word meanings before guessing.'),
    ('MSU Wordle Analysis', 'https://cse.msu.edu/~ofria/Wordle/index-word.html', 'Sortable word analysis table with every word ranked by multiple metrics including ExpectedWords, MaximumWords, and Information (bits). The most comprehensive mathematical analysis. Suggest adding: bits of information display and worst-case metric.'),
    ('Wordle Leaderboard', 'https://www.wordleleaderboard.com', 'Discord bot integration for social tracking, global and server leaderboards, player comparison. Suggest adding: social leaderboards and friend comparison features.'),
]

for name, url, desc in addl_tools:
    story.append(Paragraph(f'<b>{name}</b>', h3_style))
    story.append(Paragraph(f'URL: {url}', link_style))
    story.append(Paragraph(desc, body_style))

# ══════════════════════════════════════════════════════════════════════
# SECTION 3: GITHUB OPEN-SOURCE PROJECTS
# ══════════════════════════════════════════════════════════════════════
story.extend(add_major_section('<b>3. GitHub Open-Source Projects</b>', h1_style))
story.append(Paragraph(
    'This section covers notable open-source Wordle solver and analyzer projects found on GitHub. '
    'These projects reveal the algorithmic approaches, performance optimizations, and innovative features '
    'that could be adapted for wordleanalyzer.dev. Each project is described with its repository URL, '
    'key algorithms, and actionable feature suggestions.',
    body_style
))

# --- 3.1 ybenhayun/wordlebot ---
story.append(add_heading('<b>3.1 ybenhayun/wordlebot</b>', h2_style, level=1))
story.append(Paragraph('GitHub: https://github.com/ybenhayun/wordlebot', link_style))
story.append(Paragraph('Live Site: https://ybenhayun.github.io/wordlebot', link_style))
story.append(Paragraph('Stars: 300+', body_style))
story.append(Paragraph('<b>Algorithm:</b> Custom bucketing approach that groups possible answers into buckets based on tile colors for each guess/answer pair. Uses weighted average of bucket sizes, calculates odds of game ending next turn, computes an adjusted score to rank top 50 candidates, then recursively maps each of those 50 words to every possible answer to find the word with the lowest average total guesses.', body_style))
story.append(Paragraph('<b>Performance:</b> 3.4212 avg guesses (normal mode), 3.5119 avg guesses (hard mode), 100% success rate.', body_style))
story.append(Paragraph('<b>Suggested Features:</b> Multi-variant game support (13+ variants) and configurable word length (3-11 letters) are unique differentiators. The recursive bucketing algorithm could be adapted to provide a "bot path" feature.', body_style))

# --- 3.2 P4ST4S/next-wordle-bot ---
story.append(add_heading('<b>3.2 P4ST4S/next-wordle-bot</b>', h2_style, level=1))
story.append(Paragraph('GitHub: https://github.com/P4ST4S/next-wordle-bot', link_style))
story.append(Paragraph('<b>Algorithm:</b> Shannon Entropy-based optimal solver. Selects the guess that maximizes expected information gain at each step using information theory.', body_style))
story.append(Paragraph('<b>Tech Stack:</b> Next.js 16, React 19 with Web Workers for high-performance computation keeping the UI responsive during heavy calculations.', body_style))
story.append(Paragraph('<b>Suggested Feature:</b> Web Worker offloading for heavy entropy calculations. When computing optimal suggestions across thousands of words, using Web Workers prevents UI freezes and provides a smooth, responsive user experience. This is essential for any real-time solver feature.', body_style))

# --- 3.3 deedy/wordle-solver ---
story.append(add_heading('<b>3.3 deedy/wordle-solver</b>', h2_style, level=1))
story.append(Paragraph('GitHub: https://github.com/deedy/wordle-solver', link_style))
story.append(Paragraph('<b>Key Features:</b> 5 modes (play, show, solve, save, eval), decision tree generation for the entire solution set, custom dictionary support, custom word lengths, hard mode support. Performance: 100% accuracy on all 2,315 candidates, 3.65 avg guesses with SOARE opener.', body_style))
story.append(Paragraph('<b>Suggested Feature:</b> Decision Tree Generation. The ability to generate and visualize a complete decision tree for any starting word would be a unique and powerful feature. Users could explore different opening strategies by seeing the full tree of optimal play branching from each starting word.', body_style))

# --- 3.4 80Ltrumpet/wordlyzer ---
story.append(add_heading('<b>3.4 80Ltrumpet/wordlyzer</b>', h2_style, level=1))
story.append(Paragraph('GitHub: https://github.com/80Ltrumpet/wordlyzer', link_style))
story.append(Paragraph('<b>Key Features:</b> Fully self-contained single HTML file with zero dependencies, shows number of possible remaining words next to each guess row, keyboard shortcuts (Enter to reveal words, Backspace to delete, Escape to clear), customizable word list via included Python script.', body_style))
story.append(Paragraph('<b>Suggested Feature:</b> Real-time remaining word count display next to each guess row. This simple but powerful feedback mechanism shows users exactly how much progress each guess made toward narrowing down the answer. It is intuitive and requires no mathematical background to understand.', body_style))

# --- 3.5 EpiSci/WordleBot ---
story.append(add_heading('<b>3.5 EpiSci/WordleBot</b>', h2_style, level=1))
story.append(Paragraph('GitHub: https://github.com/EpiSci/WordleBot', link_style))
story.append(Paragraph('<b>Algorithm:</b> Shannon Entropy maximization. 3.5 avg guesses, 0 losses. Generates histogram of guess distribution using matplotlib for visual analysis across all possible games.', body_style))
story.append(Paragraph('<b>Suggested Feature:</b> Automated guess distribution visualization. Showing a histogram of how many guesses the bot needs across all possible Wordle answers gives users a benchmark for their own performance and demonstrates the tool\'s effectiveness.', body_style))

# --- 3.6 nkoppel/OptimalWordleSolver ---
story.append(add_heading('<b>3.6 nkoppel/OptimalWordleSolver</b>', h2_style, level=1))
story.append(Paragraph('GitHub: https://github.com/nkoppel/OptimalWordleSolver', link_style))
story.append(Paragraph('<b>Algorithm:</b> Exact dynamic programming and exhaustive brute-force optimization. Finds provably optimal solutions with the best known average of 3.4212 guesses. Never requires more than 5 guesses.', body_style))
story.append(Paragraph('<b>Suggested Feature:</b> Provable optimality badge. Displaying "This suggestion is mathematically proven optimal" next to the bot\'s recommendations adds authority and trustworthiness. Users want to know they are getting the best possible advice.', body_style))

# --- 3.7 sejaldua/wordle-analysis ---
story.append(add_heading('<b>3.7 sejaldua/wordle-analysis</b>', h2_style, level=1))
story.append(Paragraph('GitHub: https://github.com/sejaldua/wordle-analysis', link_style))
story.append(Paragraph('Live Tool: https://share.streamlit.io/sejaldua/wordle-analysis/main/app.py', link_style))
story.append(Paragraph('<b>Algorithm:</b> Compares multiple solving heuristics head-to-head: weighted average tile scores, max-size prioritization, max-entropy approach. Includes letter frequency heatmaps by position and exploratory data analysis.', body_style))
story.append(Paragraph('<b>Suggested Feature:</b> Letter Frequency Heatmap by Position. A visual heatmap showing which letters are most common at each position (1st through 5th) among remaining possible answers is both beautiful and strategically valuable. This visual representation makes complex frequency data immediately understandable.', body_style))

# --- 3.8 Additional GitHub Projects ---
story.append(add_heading('<b>3.8 Additional GitHub Projects</b>', h2_style, level=1))

github_tools = [
    ('fkodom/wordle', 'https://github.com/fkodom/wordle', '"Fastest Wordle solver in the West" with 99.83% success rate and less than 10ms per guess. Suggest: performance benchmarking display showing algorithm speed.'),
    ('mckoss/wordle-guesser', 'https://github.com/mckoss/wordle-guesser', 'Minimax algorithm that minimizes maximum possible set of remaining words. Best first guess: ROATE (195 max remaining). Suggest: minimax worst-case safety strategy as an alternative mode.'),
    ('dfm/wordle', 'https://github.com/dfm/wordle', 'Rust-based solver with automated browser play via Chrome WebDriver. Suggest: browser extension concept for automated real-time analysis during gameplay.'),
    ('claytonwramsey/wordle_simd', 'https://github.com/claytonwramsey/wordle_simd', 'Hardware-accelerated solver using CPU SIMD instructions in C++. Suggest: demonstrate algorithmic sophistication with speed benchmarks on the homepage.'),
    ('woctezuma/3b1b-wordle-solver', 'https://github.com/woctezuma/3b1b-wordle-solver', 'Direct implementation of 3Blue1Brown\'s famous information theory video. Suggest: educational content explaining the entropy approach with links to the 3B1B video.'),
    ('mattdodge/wordle-utils', 'https://github.com/mattdodge/wordle-utils', 'Pip-installable Python package (pip install wordle-utils) with helper functions, word lists, and analysis tools. Suggest: API endpoint allowing developers to integrate wordleanalyzer.dev analysis into their own tools.'),
]

for name, url, desc in github_tools:
    story.append(Paragraph(f'<b>{name}</b>', h3_style))
    story.append(Paragraph(f'GitHub: {url}', link_style))
    story.append(Paragraph(desc, body_style))

# ══════════════════════════════════════════════════════════════════════
# SECTION 4: FEATURE COMPARISON MATRIX
# ══════════════════════════════════════════════════════════════════════
story.extend(add_major_section('<b>4. Feature Comparison Matrix</b>', h1_style))
story.append(Paragraph(
    'The following matrix compares the key features across the most significant competitive tools. '
    'A checkmark indicates the feature is present, while an empty cell indicates it is not available. '
    'This comparison highlights both the feature gaps in the current market and the opportunities for '
    'wordleanalyzer.dev to differentiate itself by combining the best features from multiple tools.',
    body_style
))

# Feature comparison table
comp_data = [
    [Paragraph('<b>Feature</b>', header_cell_style),
     Paragraph('<b>NYT Bot</b>', header_cell_style),
     Paragraph('<b>wordle-analyzer</b>', header_cell_style),
     Paragraph('<b>ConnSolver</b>', header_cell_style),
     Paragraph('<b>Yuval</b>', header_cell_style),
     Paragraph('<b>wordlebot.net</b>', header_cell_style),
     Paragraph('<b>Wordle Tools</b>', header_cell_style),
     Paragraph('<b>Free?</b>', header_cell_style)],
]

features = [
    ('Post-game Analysis', 'Yes', 'Yes', 'Yes', 'No', 'No', 'Yes', 'Mostly'),
    ('Real-time Solver', 'No', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'),
    ('Skill/Luck Scores', 'Yes', 'No', 'No', 'No', 'No', 'No', 'N/A'),
    ('Bot Step-by-Step', 'Yes', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'),
    ('Hard Mode Support', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'Yes', 'Yes'),
    ('Multi-variant Games', 'No', 'No', 'No', 'Yes (13+)', 'No', 'No', 'Yes'),
    ('Entropy Display', 'Yes', 'No', 'No', 'No', 'No', 'No', 'Yes'),
    ('Screenshot Upload', 'Yes', 'No', 'No', 'No', 'No', 'No', 'No'),
    ('Longitudinal Tracking', 'Yes', 'No', 'No', 'No', 'No', 'No', 'No'),
    ('Shareable Analysis', 'No', 'Yes', 'No', 'No', 'No', 'No', 'Yes'),
    ('Unused Clue Detection', 'No', 'Yes', 'No', 'No', 'No', 'No', 'Yes'),
    ('Difficulty Scorecard', 'No', 'No', 'No', 'No', 'No', 'Yes', 'Yes'),
    ('Multiple Algorithms', 'No', 'No', 'No', 'No', 'No', 'Yes (5)', 'Yes'),
]

for feat_name, *vals in features:
    row = [Paragraph(feat_name, cell_style)]
    for v in vals:
        row.append(Paragraph(v, cell_center_style))
    comp_data.append(row)

cw = [CONTENT_WIDTH * 0.22] + [CONTENT_WIDTH * 0.097] * 6 + [CONTENT_WIDTH * 0.098]
story.extend(make_table(comp_data, cw, 'Table 1: Feature Comparison Across Major Competitors'))

# ══════════════════════════════════════════════════════════════════════
# SECTION 5: PRIORITY-RANKED FEATURE SUGGESTIONS
# ══════════════════════════════════════════════════════════════════════
story.extend(add_major_section('<b>5. Priority-Ranked Feature Suggestions</b>', h1_style))
story.append(Paragraph(
    'Based on the comprehensive analysis of all 30+ projects and tools, the following features are '
    'ranked by their potential impact on user acquisition, engagement, and differentiation. Each feature '
    'includes the source project that inspired it and the rationale for its priority level.',
    body_style
))

# --- HIGH PRIORITY ---
story.append(add_heading('<b>5.1 High Priority (Major Differentiators)</b>', h2_style, level=1))

high_features = [
    ('Skill and Luck Scoring (0-99 Scale)',
     'NYT WordleBot',
     'No free tool currently offers skill/luck decomposition. This is the single most requested feature '
     'in Wordle analysis communities. Implementing a 0-99 scale that mathematically separates decision quality '
     '(skill) from outcome randomness (luck) would immediately position wordleanalyzer.dev as the definitive '
     'free alternative to the paywalled WordleBot. This feature alone would drive significant organic traffic '
     'from Reddit, Twitter, and Wordle communities where users frequently express frustration about the paywall.'),

    ('Unused Clue Detection',
     'wordle-analyzer.com',
     'This feature identifies when a player has information from a previous guess (like a yellow letter) that '
     'they failed to use optimally in a subsequent guess. wordle-analyzer.com is the only tool offering this, '
     'and it is one of the most educational features possible. Improving on it with specific suggestions '
     '("You had a yellow A in row 2 - consider trying it in position 3 next") would make our tool the '
     'best post-game learning platform available.'),

    ('Entropy / Information Bits Display',
     'MSU Wordle Analysis, barapatte.com, joey.sh',
     'Showing how many bits of information each guess provided is a powerful analytical metric that no '
     'consumer-friendly tool currently offers in an accessible way. Visualizing this as a bar chart or '
     'gauge next to each guess ("Your second guess provided 3.2 bits of information - optimal would have been '
     '4.1 bits") makes the abstract concept of information theory tangible and educational.'),

    ('Game Difficulty Scorecard',
     'Wordle Tools (wordletools.azurewebsites.net)',
     'Allowing users to see a difficulty rating for any puzzle (based on factors like letter frequency, '
     'common trap patterns, and number of similar words) is a unique and highly shareable feature. A '
     '"Today\'s puzzle difficulty: 7.2/10 (Harder than 73% of all Wordles)" badge is inherently viral on '
     'social media and gives users a reason to visit even when they have not played yet.'),

    ('Longitudinal Performance Tracking',
     'NYT WordleBot (paywalled), Wordle Calculator',
     'Tracking skill, luck, and average guesses over time with rolling 14-day averages and trend lines '
     'gives users a powerful reason to return daily. This transforms wordleanalyzer.dev from a one-time '
     'tool into a daily habit platform. Implementing a simple local storage-based dashboard with no '
     'account required would lower the barrier to adoption while still providing significant value.'),
]

for i, (name, source, rationale) in enumerate(high_features, 1):
    story.append(Paragraph(f'<b>{i}. {name}</b>', h3_style))
    story.append(Paragraph(f'Source: {source}', link_style))
    story.append(Paragraph(rationale, body_style))

# --- MEDIUM PRIORITY ---
story.append(add_heading('<b>5.2 Medium Priority (Strong Feature Enhancements)</b>', h2_style, level=1))

med_features = [
    ('Progressive Hint System',
     'word.tips',
     'Multiple hint levels (vague, moderate, specific) for players who want some help without seeing the full answer. This respects different play styles and makes the tool useful for a broader audience, from complete beginners to experienced players seeking a subtle nudge.'),

    ('Side-by-Side Player vs. Bot Comparison Table',
     'wordle-analyzer.com, NYT WordleBot',
     'Showing your actual guesses next to what the optimal bot would have played at each step is the most engaging way to present post-game analysis. This visual comparison format makes the analysis immediately understandable and genuinely educational, even for users who are not interested in mathematical metrics.'),

    ('Letter Frequency Heatmap by Position',
     'sejaldua/wordle-analysis, The Word Finder',
     'A visual heatmap showing which letters are most common at each of the 5 positions among remaining possible answers is both beautiful and strategically valuable. This visual representation makes complex frequency data immediately understandable and helps players make more informed guesses.'),

    ('Multiple Strategy Comparison',
     'Wordle Tools, deedy/wordle-solver',
     'Showing how different algorithmic approaches (entropy-maximizing, max-elimination, frequency-based, minimax) would have performed on the same game side-by-side is educational and appeals to technically-minded users. It also demonstrates the sophistication of the analysis engine.'),

    ('Best Possible Letters Suggestion',
     'The Word Finder (thewordfinder.com)',
     'Recommending not just which words to guess but which individual letters are most likely to appear among remaining answers. This helps players who want to think for themselves but need strategic guidance on which letters to probe. It is a more subtle and educational form of assistance than simply giving word suggestions.'),

    ('Hard Mode Analysis Toggle',
     'wordle-analyzer.com, ybenhayun/wordlebot',
     'Adding a hard mode toggle that adjusts all analysis, suggestions, and scoring for hard mode constraints is an expected feature that many tools support but several major ones do not. Hard mode players are often the most engaged users and providing dedicated analysis for their play style increases retention.'),
]

for i, (name, source, rationale) in enumerate(med_features, 1):
    story.append(Paragraph(f'<b>{i}. {name}</b>', h3_style))
    story.append(Paragraph(f'Source: {source}', link_style))
    story.append(Paragraph(rationale, body_style))

# --- NICE TO HAVE ---
story.append(add_heading('<b>5.3 Nice to Have (Polish and Extended Features)</b>', h2_style, level=1))

nice_features = [
    ('Shareable Analysis URLs with Spoiler Warning',
     'wordle-analyzer.com',
     'Generate shareable links to your game analysis with a spoiler warning page. Creates social virality and drives organic traffic.'),

    ('Past Wordle Answers Archive',
     'word.tips, multiple sites',
     'Searchable database of all historical Wordle answers. Excellent for SEO and serves as a reference tool that drives organic search traffic.'),

    ('On-Screen QWERTY Keyboard',
     'Wordle Analyser (Azure), Wordle Tools',
     'Mobile-friendly on-screen keyboard for input instead of relying on the device keyboard. Essential for a smooth mobile experience.'),

    ('Dark Mode',
     'wordle-analyzer.com, wordlebot.net',
     'Auto-detected from system preference. Expected by modern web users and particularly important for Wordle players who often play in the evening.'),

    ('Multi-Variant Game Support (Dordle, Quordle, Octordle)',
     'ybenhayun/wordlebot, WordleHelper.com',
     'Supporting popular Wordle spin-offs expands the addressable audience significantly. Many players regularly play Dordle and Quordle and need analysis tools for those games too.'),

    ('Position-Specific Exclusion Input',
     'HelpWordle.com',
     'A fourth input category beyond green/yellow/gray for "letters known to not be in a specific position." Handles the nuanced case where a letter is confirmed present but a specific position is ruled out.'),

    ('Word Definitions Integration',
     'word.tips, Collins Dictionary',
     'Show word definitions alongside suggestions so players can verify word meanings before guessing. Particularly helpful for uncommon valid words.'),

    ('Browser Extension for Auto-Detection',
     'Wordle Stats Explorer (Chrome Extension)',
     'A browser extension that automatically detects and analyzes Wordle games as you play, eliminating the need for manual input. This would be a powerful growth channel through the Chrome Web Store.'),
]

for i, (name, source, rationale) in enumerate(nice_features, 1):
    story.append(Paragraph(f'<b>{i}. {name}</b>', h3_style))
    story.append(Paragraph(f'Source: {source}', link_style))
    story.append(Paragraph(rationale, body_style))

# ══════════════════════════════════════════════════════════════════════
# SECTION 6: GREEN-FIELD OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════════
story.extend(add_major_section('<b>6. Green-Field Opportunities (Features Nobody Offers Yet)</b>', h1_style))
story.append(Paragraph(
    'These are features that no existing tool currently offers, representing completely untapped opportunities '
    'for wordleanalyzer.dev to pioneer new capabilities and establish first-mover advantage. These features '
    'were identified by analyzing the gap between what users want (based on community discussions on Reddit, '
    'Twitter, and Wordle forums) and what any tool currently provides.',
    body_style
))

greenfield = [
    ('Real-Time Analysis During Play',
     'All current tools require either finishing the game first or switching to a separate tab. A browser '
     'extension or overlay that analyzes your game in real-time as you type each letter would be revolutionary. '
     'It could show remaining word count, best next guess, and elimination percentage as you play, without '
     'requiring any manual input after setup. This represents the biggest UX innovation opportunity in the space.'),

    ('Strategy Simulator ("What If" Replay)',
     'Allow users to replay any game with different opening words to see how it would have played out. '
     '"What if I had opened with CRANE instead of SLATE?" This turns analysis from retrospective scoring '
     'into an interactive learning experience. Players could test alternative strategies on the same puzzle '
     'and directly compare outcomes, making the tool genuinely educational rather than merely evaluative.'),

    ('Personalized Strategy Coaching',
     'Based on a user\'s game history, identify specific patterns and weaknesses. For example: "You tend to '
     'struggle with words containing J, X, Z - try opening with words that probe these letters earlier" or '
     '"Your third guess consistently underperforms - consider using words that maximize letter coverage rather '
     'than guessing likely answers." This level of personalized analysis does not exist anywhere and would be '
     'a powerful retention driver.'),

    ('ELO-Style Skill Rating System',
     'A true skill rating that accounts for puzzle difficulty, not just average guesses. A player who solves '
     'a hard puzzle in 4 guesses should rate higher than one who solves an easy puzzle in 3. An ELO-style '
     'system that adjusts ratings based on puzzle difficulty creates a competitive and engaging meta-game '
     'beyond just solving the daily Wordle.'),

    ('Word Pattern Trap Analysis',
     'Identify and teach about common trap patterns where multiple similar words exist. For example, words '
     'ending in -IGHT are common traps because there are 8 possibilities (NIGHT, LIGHT, RIGHT, MIGHT, FIGHT, '
     'TIGHT, SIGHT, EIGHT). A dedicated section teaching players how to navigate these traps with strategic '
     'elimination guesses would be uniquely valuable educational content.'),

    ('Multi-Language Wordle Analysis',
     'Support for Wordle in Spanish, French, German, and other languages. The global Wordle phenomenon extends '
     'far beyond English, and no analysis tool currently serves non-English players. This would open entirely '
     'new markets with minimal competition.'),

    ('Guess Quality 2D Spectrum',
     'Instead of just a skill/luck score, show a 2D visualization where each guess is plotted on a spectrum '
     'of "Conservative vs. Aggressive" and "Lucky vs. Unlucky." This gives players a nuanced understanding '
     'of their play style beyond simple numerical scores, making the analysis more engaging and shareable.'),

    ('Streak Probability Calculator',
     'Given a user\'s play style and historical performance, calculate the probability of maintaining their '
     'current streak for various time periods. "Given your play style, your probability of maintaining a '
     '100-day streak is 23%." This creates engaging, personalized content that players would share on social media.'),
]

for i, (name, desc) in enumerate(greenfield, 1):
    story.append(Paragraph(f'<b>{i}. {name}</b>', h3_style))
    story.append(Paragraph(desc, body_style))

# ══════════════════════════════════════════════════════════════════════
# SECTION 7: IMPLEMENTATION PRIORITY ROADMAP
# ══════════════════════════════════════════════════════════════════════
story.extend(add_major_section('<b>7. Implementation Priority Roadmap</b>', h1_style))
story.append(Paragraph(
    'The following roadmap organizes the recommended features into implementation phases based on '
    'impact, complexity, and dependencies. Phase 1 features should be implemented first as they provide '
    'the highest return on investment with moderate development effort.',
    body_style
))

roadmap_data = [
    [Paragraph('<b>Phase</b>', header_cell_style),
     Paragraph('<b>Feature</b>', header_cell_style),
     Paragraph('<b>Source Project</b>', header_cell_style),
     Paragraph('<b>Impact</b>', header_cell_style),
     Paragraph('<b>Effort</b>', header_cell_style)],

    [Paragraph('1', cell_center_style), Paragraph('Skill/Luck Scoring', cell_style),
     Paragraph('NYT WordleBot', cell_style), Paragraph('Very High', cell_center_style), Paragraph('Medium', cell_center_style)],

    [Paragraph('1', cell_center_style), Paragraph('Unused Clue Detection', cell_style),
     Paragraph('wordle-analyzer.com', cell_style), Paragraph('Very High', cell_center_style), Paragraph('Medium', cell_center_style)],

    [Paragraph('1', cell_center_style), Paragraph('Player vs. Bot Comparison', cell_style),
     Paragraph('wordle-analyzer.com', cell_style), Paragraph('High', cell_center_style), Paragraph('Low', cell_center_style)],

    [Paragraph('1', cell_center_style), Paragraph('Remaining Words Count per Row', cell_style),
     Paragraph('80Ltrumpet/wordlyzer', cell_style), Paragraph('High', cell_center_style), Paragraph('Low', cell_center_style)],

    [Paragraph('2', cell_center_style), Paragraph('Entropy Bits Display', cell_style),
     Paragraph('MSU, joey.sh', cell_style), Paragraph('High', cell_center_style), Paragraph('Medium', cell_center_style)],

    [Paragraph('2', cell_center_style), Paragraph('Game Difficulty Scorecard', cell_style),
     Paragraph('Wordle Tools', cell_style), Paragraph('High', cell_center_style), Paragraph('Medium', cell_center_style)],

    [Paragraph('2', cell_center_style), Paragraph('Letter Frequency Heatmap', cell_style),
     Paragraph('sejaldua/wordle-analysis', cell_style), Paragraph('Medium', cell_center_style), Paragraph('Medium', cell_center_style)],

    [Paragraph('2', cell_center_style), Paragraph('Hard Mode Toggle', cell_style),
     Paragraph('wordle-analyzer.com', cell_style), Paragraph('Medium', cell_center_style), Paragraph('Low', cell_center_style)],

    [Paragraph('3', cell_center_style), Paragraph('Longitudinal Tracking Dashboard', cell_style),
     Paragraph('NYT WordleBot', cell_style), Paragraph('Very High', cell_center_style), Paragraph('High', cell_center_style)],

    [Paragraph('3', cell_center_style), Paragraph('Progressive Hint System', cell_style),
     Paragraph('word.tips', cell_style), Paragraph('Medium', cell_center_style), Paragraph('Medium', cell_center_style)],

    [Paragraph('3', cell_center_style), Paragraph('Shareable Analysis URLs', cell_style),
     Paragraph('wordle-analyzer.com', cell_style), Paragraph('Medium', cell_center_style), Paragraph('Medium', cell_center_style)],

    [Paragraph('4', cell_center_style), Paragraph('Multi-Variant Support', cell_style),
     Paragraph('ybenhayun/wordlebot', cell_style), Paragraph('High', cell_center_style), Paragraph('High', cell_center_style)],

    [Paragraph('4', cell_center_style), Paragraph('Browser Extension', cell_style),
     Paragraph('Wordle Stats Explorer', cell_style), Paragraph('High', cell_center_style), Paragraph('High', cell_center_style)],

    [Paragraph('4', cell_center_style), Paragraph('Strategy Simulator', cell_style),
     Paragraph('Green-field', cell_style), Paragraph('Very High', cell_center_style), Paragraph('High', cell_center_style)],
]

roadmap_cw = [CONTENT_WIDTH * 0.08, CONTENT_WIDTH * 0.28, CONTENT_WIDTH * 0.27, CONTENT_WIDTH * 0.17, CONTENT_WIDTH * 0.14]
story.extend(make_table(roadmap_data, roadmap_cw, 'Table 2: Feature Implementation Roadmap by Phase'))

# ══════════════════════════════════════════════════════════════════════
# SECTION 8: SUMMARY OF ALL PROJECTS
# ══════════════════════════════════════════════════════════════════════
story.extend(add_major_section('<b>8. Complete Project Reference Table</b>', h1_style))
story.append(Paragraph(
    'The following table provides a complete reference of all projects analyzed in this report, '
    'including their URLs and the primary feature suggestion derived from each.',
    body_style
))

ref_data = [
    [Paragraph('<b>Project Name</b>', header_cell_style),
     Paragraph('<b>URL</b>', header_cell_style),
     Paragraph('<b>Primary Suggestion</b>', header_cell_style)],
]

all_projects = [
    ('NYT WordleBot', 'nytimes.com/interactive/2022/upshot/wordle-bot.html', 'Skill/Luck Scoring + Longitudinal Tracking'),
    ('wordle-analyzer.com', 'wordle-analyzer.com', 'Unused Clue Detection + Shareable URLs'),
    ('ConnectionsSolver', 'connectionssolver.com/wordle-analyzer', 'Dual Analyzer + Bot Mode'),
    ('Yuval WordleBot', 'ybenhayun.github.io/wordlebot', 'Multi-Variant Support + Configurable Length'),
    ('WordleBot.net', 'wordlebot.net', 'Double-Click Color Cycling + Game Hub'),
    ('Wordle Tools', 'wordletools.azurewebsites.net', 'Difficulty Scorecard + 5-Method Comparison'),
    ('Scoredle', 'scoredle.com', 'Share Results Feature'),
    ('The Word Finder', 'thewordfinder.com/wordle-solver', 'Best Letters Suggestion + Heatmap'),
    ('Word.tips', 'word.tips/wordle', 'Progressive Hints + Answers Archive'),
    ('J. Olson Solver', 'jonathanolson.net/wordle-solver', 'Decision Tree + Multi-Strategy'),
    ('HelpWordle', 'helpwordle.com', 'Position-Specific Exclusion + Strategy Tips'),
    ('Wordle Calculator', 'wordlecalculator.digital', 'Play Style Analysis + Streak Tracking'),
    ('Engaging Data', 'engaging-data.com/wordle-guess-distribution', 'Global Difficulty Comparison'),
    ('Wordle Analyser (Azure)', 'wordleanalyser.azurewebsites.net', 'On-Screen Keyboard + Word Filter'),
    ('WordleSolver.app', 'wordlesolver.app', 'Entropy Scoring + Multi-Game Support'),
    ('Wordle Stats Explorer', 'Chrome Web Store', 'Auto Game Tracking + Trends'),
    ('Collins Dictionary Helper', 'collinsdictionary.com/us/games/wordle-helper', 'Dictionary Definitions'),
    ('MSU Wordle Analysis', 'cse.msu.edu/~ofria/Wordle', 'Information Bits + Worst-Case Metric'),
    ('Wordle Leaderboard', 'wordleleaderboard.com', 'Social Leaderboards + Discord Bot'),
    ('P4ST4S/next-wordle-bot', 'github.com/P4ST4S/next-wordle-bot', 'Web Worker Computation'),
    ('deedy/wordle-solver', 'github.com/deedy/wordle-solver', 'Decision Tree Generation'),
    ('80Ltrumpet/wordlyzer', 'github.com/80Ltrumpet/wordlyzer', 'Remaining Word Count per Row'),
    ('EpiSci/WordleBot', 'github.com/EpiSci/WordleBot', 'Guess Distribution Histogram'),
    ('nkoppel/OptimalWordleSolver', 'github.com/nkoppel/OptimalWordleSolver', 'Provable Optimality Badge'),
    ('sejaldua/wordle-analysis', 'github.com/sejaldua/wordle-analysis', 'Letter Frequency Heatmap'),
    ('fkodom/wordle', 'github.com/fkodom/wordle', 'Speed Benchmarking Display'),
    ('mckoss/wordle-guesser', 'github.com/mckoss/wordle-guesser', 'Minimax Worst-Case Strategy'),
    ('dfm/wordle', 'github.com/dfm/wordle', 'Automated Browser Play Concept'),
    ('3b1b-wordle-solver', 'github.com/woctezuma/3b1b-wordle-solver', 'Educational Entropy Content'),
    ('wordle-utils', 'github.com/mattdodge/wordle-utils', 'Developer API Endpoint'),
]

for name, url, suggestion in all_projects:
    ref_data.append([
        Paragraph(name, cell_style),
        Paragraph(url, cell_style),
        Paragraph(suggestion, cell_style),
    ])

ref_cw = [CONTENT_WIDTH * 0.22, CONTENT_WIDTH * 0.42, CONTENT_WIDTH * 0.32]
story.extend(make_table(ref_data, ref_cw, 'Table 3: Complete Project Reference with Primary Feature Suggestions'))

# ══════════════════════════════════════════════════════════════════════
# BUILD
# ══════════════════════════════════════════════════════════════════════
doc.multiBuild(story)
print(f"PDF generated successfully at: {OUTPUT_PATH}")
