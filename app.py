import html
from urllib.parse import urlparse, parse_qs, unquote

import streamlit as st

from graph import build_graph
from fpdf import FPDF
from history import init_db, save_research, get_all_history, get_history_by_id
import base64
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Agentic AI Research Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTS
# ============================================================

APP_TITLE = "Agentic AI Research Assistant"
APP_SUBTITLE = "Research deeply. Verify intelligently. Write clearly."

STAGE_ORDER = [
    ("planner", "Research Planner", "Breaks your question into focused research tasks."),
    ("search", "Research Agent", "Finds relevant evidence and supporting sources."),
    ("verify", "Verification Agent", "Checks findings against available evidence."),
    ("report", "Report Writer", "Synthesizes verified findings into a final report."),
]

EXAMPLE_QUESTIONS = [
    "What are the economic effects of remote work on urban housing markets?",
    "How is generative AI changing software engineering in 2026?",
    "What are the environmental impacts of electric vehicles?",
]


# ============================================================
# HELPERS
# ============================================================

def safe_text(value):
    """Safely escape dynamic text before inserting into HTML."""
    if value is None:
        return ""
    return html.escape(str(value))


def get_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def image_to_base64(path):
    path = Path(path)

    if not path.exists():
        return ""

    return base64.b64encode(path.read_bytes()).decode("utf-8")


def inject_css():
    st.markdown(
        """
        <style>

        /* =====================================================
           GLOBAL
        ===================================================== */

       @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

 :root {
    --bg: #FAF9FC;
    --surface: #FFFFFF;
    --surface-soft: #FCF9FD;
    --border: #E5E1EB;
    --border-strong: #DCD6E2;

    --text: #1E1B2E;
    --text-soft: #5F596B;
    --text-muted: #8B8494;

    --primary: #A21CAF;
    --primary-dark: #86198F;
    --primary-soft: #FCE7F3;
    --primary-border: #F3D6F5;

    --success: #159A69;
    --success-soft: #E9F8F1;

    --warning: #C27B14;
    --warning-soft: #FFF6DF;

    --danger: #D6455D;
    --danger-soft: #FFF0F3;

    --shadow-sm: 0 1px 2px rgba(30, 27, 46, 0.04);
    --shadow-md: 0 10px 30px rgba(30, 27, 46, 0.07);
    --shadow-lg: 0 18px 50px rgba(30, 27, 46, 0.10);

    --radius-sm: 10px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-xl: 26px;
}

        * {
            box-sizing: border-box;
        }

        html, body, [class*="css"] {
            font-family: "Inter", sans-serif;
        }

       .stApp {
    background:
        radial-gradient(
            circle at 50% -10%,
            rgba(192, 38, 211, 0.055),
            transparent 32%
        ),
        var(--bg);
    color: var(--text);
}

        .main .block-container {
            max-width: 1420px;
            padding-top: 0.8rem;
            padding-bottom: 4rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
        }

        /* Hide Streamlit default chrome */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* =====================================================
           SIDEBAR
           ===================================================== */

        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--border);
        }

        section[data-testid="stSidebar"] > div {
            padding: 0;
        }

        .sidebar-brand {
            padding: 26px 22px 22px 22px;
            border-bottom: 1px solid var(--border);
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-icon {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            background: linear-gradient(135deg, #C026D3, #86198F);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 19px;
            font-weight: 800;
            box-shadow: 0 7px 18px rgba(162, 28, 175, 0.22);
        }

        .brand-title {
           font-family: "Space Grotesk", sans-serif;
            font-size: 15px;
            font-weight: 800;
            color: #171923;
            line-height: 1.25;
        }

        .brand-subtitle {
            margin-top: 3px;
            font-size: 11px;
            color: #8a91a3;
            font-weight: 500;
        }

        .sidebar-section {
            padding: 22px 18px 0 18px;
        }

        .sidebar-label {
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            color: #9aa1b1;
            margin: 0 0 10px 4px;
        }

        .model-card {
            background: #fafaff;
            border: 1px solid #e6e5f8;
            border-radius: 13px;
            padding: 13px;
        }

        .model-name {
        font-family: "JetBrains Mono", monospace;
            font-size: 13px;
            font-weight: 700;
            color: #26293a;
        }

        .model-provider {
            font-size: 11px;
            color: #858ca0;
            margin-top: 4px;
        }

        .status-card {
            background: var(--success-soft);
            border: 1px solid #ccefe0;
            border-radius: 13px;
            padding: 12px 13px;
            margin-top: 12px;
        }

        .status-row {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            box-shadow: 0 0 0 4px rgba(21,154,105,0.10);
        }

        .status-title {
            font-size: 12px;
            font-weight: 700;
            color: #167352;
        }

        .status-desc {
            font-size: 10px;
            color: #5d8b78;
            margin-top: 5px;
            line-height: 1.45;
        }

        /* Sidebar button */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            width: 100%;
            min-height: 42px;
            border-radius: 11px;
            border: 1px solid var(--border);
            background: #ffffff;
            color: #3b4050;
            font-family: "Inter", sans-serif;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.18s ease;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
            border-color: #c9c5f7;
            color: var(--primary);
            background: #fafaff;
        }

        /* =====================================================
           TOP BAR
           ===================================================== */

        .topbar {
            min-height: 58px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            margin-bottom: 48px;
        }

        .topbar-left {
            display: flex;
            align-items: center;
            gap: 9px;
        }

        .topbar-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 0 4px rgba(21,154,105,0.08);
        }

        .topbar-text {
            font-size: 11px;
            font-weight: 600;
            color: #72798a;
        }

        .tech-pill {
            padding: 7px 11px;
            border-radius: 8px;
            background: #ffffff;
            border: 1px solid var(--border);
            color: #737b8e;
            font-size: 10px;
            font-weight: 600;
        }

        /* =====================================================
           HERO
           ===================================================== */

        .hero {
            text-align: center;
            max-width: 920px;
            margin: 0 auto;
        }

     .hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 9px;

    padding: 8px 14px;
    border-radius: 999px;

    background: #FDF3FE;
    border: 1px solid #EFCDF2;

    color: #86198F;

    font-family: "Space Grotesk", sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.02em;

    box-shadow: 0 4px 14px rgba(162, 28, 175, 0.07);
}

       .hero-badge-dot {
    width: 8px;
    height: 8px;
    border-radius: 3px;

    background: #C026D3;

    transform: rotate(45deg);

    box-shadow:
        0 0 0 3px rgba(192, 38, 211, 0.10),
        0 0 10px rgba(192, 38, 211, 0.25);
}


       .hero-title {
    margin-top: 22px;
    font-family: "Space Grotesk", sans-serif;
    font-size: 56px !important;
    line-height: 1.02;
    letter-spacing: -0.045em;
    font-weight: 700 !important;
   color: #3F2945 !important;

}

        .hero-title-accent {
         color: #B21DBF;
        }

        .hero-subtitle {
            max-width: 650px;
            margin: 17px auto 0 auto;
            font-family: "Inter", sans-serif;
            font-size: 14px;
            line-height: 1.7;
           color: #6F6878;
        }

        /* =====================================================
           COMPOSER
           ===================================================== */

        .composer-shell {
            max-width: 900px;
            margin: 34px auto 0 auto;
            background: #ffffff;
            border: 1px solid #dedff0;
            border-radius: 20px;
            box-shadow:
                0 20px 55px rgba(40, 43, 75, 0.09),
                0 2px 8px rgba(40, 43, 75, 0.035);
            overflow: hidden;
        }

        .composer-head {
            padding: 18px 20px 8px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .composer-label {
            font-size: 11px;
            font-weight: 700;
            color: #7d8496;
            text-transform: uppercase;
            letter-spacing: 0.09em;
        }

        .composer-mode {
            font-size: 10px;
            color: #949bad;
            font-weight: 600;
        }

        /* Streamlit text area */
        div[data-testid="stTextArea"] {
            padding: 0 20px;
        }

        div[data-testid="stTextArea"] textarea {
            min-height: 145px !important;
            border: none !important;
            background: #ffffff !important;
            box-shadow: none !important;
            resize: none !important;

            color: #1a1d29 !important;
            font-family: "Inter", sans-serif !important;
            font-size: 15px !important;
            line-height: 1.65 !important;
            padding: 12px 0 !important;
        }

        div[data-testid="stTextArea"] textarea::placeholder {
            color: #a5abba !important;
        }

        div[data-testid="stTextArea"] textarea:focus {
            border: none !important;
            box-shadow: none !important;
        }

        /* =====================================================
           CUSTOM TOGGLE + TEXTAREA CONTROL
           ===================================================== */

        /* =====================================================
           DEEP RESEARCH TOGGLE
           ===================================================== */

        /* Deep Research toggle track */
        div.st-emotion-cache-1bkesb7.e15oan337 {
            background-color: #000000 !important;
            border-color: #000000 !important;
        }

        /* Deep Research toggle indicator */
        div.st-emotion-cache-1cnh1um.e15oan338 {
            background-color: #ffffff !important;
            border-color: #ffffff !important;
        }

        /* Text area resize/focus control — black */
        div[data-testid="stTextArea"] textarea {
            outline-color: #000000 !important;
            accent-color: #000000 !important;
        }

        /* Research Question — clean black border */

        div[data-testid="stTextAreaRootElement"] {
            outline: none !important;
            border: 1px solid #000000 !important;
            box-shadow: none !important;
            background: #ffffff !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        div[data-testid="stTextAreaRootElement"]:focus-within {
            outline: none !important;
            border: 1px solid #000000 !important;
            box-shadow: none !important;
        }

        div[data-testid="stTextArea"] textarea:focus {
            outline-color: #000000 !important;
            border-color: #000000 !important;
        }

        .composer-footer {
            border-top: 1px solid #eeeeF4;
            background: #fcfcfe;
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .composer-hints {
            display: flex;
            align-items: center;
            gap: 15px;
            color: #9299aa;
            font-size: 10px;
            font-weight: 500;
        }

        .hint-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .hint-check {
            color: var(--success);
            font-weight: 800;
        }

        /* Main buttons */
        .stButton > button {
            border-radius: 10px;
            border: 1px solid #dedff0;
            background: #ffffff;
            color: #565d70;
            font-family: "Inter", sans-serif;
            font-weight: 600;
            font-size: 11px;
            min-height: 40px;
            transition: all 0.18s ease;
        }

        .stButton > button:hover {
            border-color: #c9c5f7;
            color: var(--primary);
            background: #fafaff;
        }

        /* Main primary submit button */
        div[data-testid="stFormSubmitButton"] button {
            min-height: 43px !important;
            padding: 0 21px !important;
            border: none !important;
            color: #ffffff !important;
           background: linear-gradient(135deg, #C026D3 0%, #A21CAF 100%) !important;
          box-shadow: 0 8px 20px rgba(162, 28, 175, 0.20) !important;
            font-size: 12px !important;
            font-weight: 700 !important;
        }

       div[data-testid="stFormSubmitButton"] button:hover {
    color: #ffffff !important;

    background: linear-gradient(
        135deg,
        #C026D3 0%,
        #A21CAF 100%
    ) !important;

    box-shadow: 0 10px 25px rgba(162, 28, 175, 0.27) !important;

    transform: translateY(-1px);
 }

        /* =====================================================
           SUGGESTIONS
           ===================================================== */

        .suggestions {
            max-width: 900px;
            margin: 25px auto 0 auto;
        }

        .suggestion-title {
            text-align: center;
            font-size: 10px;
            font-weight: 700;
            color: #9299aa;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 11px;
        }

        .suggestion-row {
            display: flex;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        /* =====================================================
           DIVIDERS
           ===================================================== */

        .section-space {
            height: 48px;
        }

        .section-divider {
            height: 1px;
            background: var(--border);
            margin: 36px 0;
        }

        /* =====================================================
           SECTION HEADERS
           ===================================================== */

        .section-header {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            margin-bottom: 18px;
        }

        .section-kicker {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #949bad;
            margin-bottom: 5px;
        }

        .section-title {
         font-family: "Space Grotesk", sans-serif;
            font-size: 22px;
            line-height: 1.2;
            font-weight: 800;
            letter-spacing: -0.025em;
            color: #191c27;
        }

        .section-description {
            font-size: 11px;
            color: #858c9d;
            margin-top: 6px;
        }

     /* =====================================================
   PIPELINE
   ===================================================== */

.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    position: relative;
}

.pipeline-card {
     position: relative !important;
    overflow: hidden !important;
    isolation: isolate;

    min-height: 210px;
    padding: 22px;

    border: 1px solid #E8E1EB;
    border-radius: 18px;

    background: #FFFFFF;

    box-shadow:
        0 2px 6px rgba(30, 27, 46, 0.03),
        0 10px 28px rgba(30, 27, 46, 0.045);

    transition:
        transform 0.18s ease,
        border-color 0.18s ease,
        box-shadow 0.18s ease;
}

.pipeline-card::after {
    display: none;
}

.pipeline-content {
    position: relative !important;
    z-index: 2 !important;

    width: 100%;
}

.pipeline-card:hover {
    transform: translateY(-3px);

    border-color: #E1B9E5;

    box-shadow:
        0 5px 12px rgba(30, 27, 46, 0.04),
        0 16px 34px rgba(162, 28, 175, 0.08);
}

.pipeline-card:hover .pipeline-bg-image {
    transform: scale(1.04);
    opacity: 0.9;
}

/* Agent number */
.pipeline-icon {
    width: 46px;
    height: 46px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin-bottom: 12px;

    border-radius: 13px;

 background: transparent;
 border: none;

    color: #A21CAF;

    box-shadow:
        0 5px 14px rgba(162, 28, 175, 0.08);
}

.pipeline-icon svg {
    width: 28px;
    height: 28px;

    display: block;

    stroke: #A21CAF !important;
}

.pipeline-number {
    width: 32px;
    height: 32px;

    border-radius: 9px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin-bottom: 16px;

    background: rgba(252, 231, 243, 0.92);
    color: #A21CAF;

    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 600;

    border: 1px solid rgba(243, 214, 245, 0.95);

    backdrop-filter: blur(5px);
}

/* Agent title */

.pipeline-name {
    font-family: "Space Grotesk", sans-serif;

    font-size: 15px;
    font-weight: 700;

    line-height: 1.3;

    color: #3F2945;
}

/* Agent description */

.pipeline-desc {
    margin-top: 8px;

    max-width: 230px;

    color: #5F596B;

    font-family: "Inter", sans-serif;
    font-size: 11px;
    font-weight: 500;

    line-height: 1.55;
}

/* Status */

.pipeline-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    margin-top: 15px;

    padding: 4px 9px;

    border-radius: 999px;

    background: #E9F8F1;
    border: 1px solid #D2F0E3;

    color: #159A69;

    font-family: "Inter", sans-serif;
    font-size: 9px;
    font-weight: 600;

    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Small status indicator */

.pipeline-status::before {
    content: "";

    width: 5px;
    height: 5px;

    border-radius: 50%;

    background: #159A69;

    box-shadow: 0 0 0 3px rgba(21, 154, 105, 0.08);
}

/* Active state */

.pipeline-card.active {
    border-color: #E1B9E5;

    background: linear-gradient(
        145deg,
        #FFFFFF 0%,
        #FDF4FE 100%

    );

    box-shadow:
        0 8px 25px rgba(162, 28, 175, 0.08);
}

.pipeline-card.active .pipeline-number {
    background: #FCE7F3;
    color: #A21CAF;
    border-color: #F3D6F5;
}

.pipeline-card.active .pipeline-status {
    background: #FCE7F3;
    border-color: #F3D6F5;
    color: #A21CAF;
}

.pipeline-card.active .pipeline-status::before {
    background: #C026D3;
}

/* Completed state */

.pipeline-card.complete {
    border-color: #D4EEE4;
}

.pipeline-card.complete .pipeline-number {
    background: #E9F8F1;
    color: #159A69;
    border-color: #D2F0E3;
}

.pipeline-card.complete .pipeline-status {
    color: #159A69;
}

        /* =====================================================
           METRIC CARDS
           ===================================================== */

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin: 18px 0 30px 0;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 17px 18px;
            box-shadow: var(--shadow-sm);
        }

        .metric-label {
            font-size: 9px;
            color: #8b92a3;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
        }

        .metric-value {
            margin-top: 8px;
          font-family: "Space Grotesk", sans-serif;
            font-size: 25px;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #1b1e29;
        }

        .metric-note {
            margin-top: 4px;
            font-size: 9px;
            color: #9aa0af;
        }

        /* =====================================================
           REPORT
           ===================================================== */

        .report-card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 19px;
            box-shadow: var(--shadow-md);
            overflow: hidden;
        }

        .report-header {
            padding: 22px 24px;
            border-bottom: 1px solid var(--border);
            background:
                linear-gradient(
                    180deg,
                    #ffffff 0%,
                    #fbfbfe 100%
                );
        }

        .report-label {
            display: inline-flex;
            padding: 5px 8px;
            border-radius: 6px;
            background: var(--primary-soft);
            color: var(--primary);
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .report-title {
            margin-top: 10px;
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 20px;
            line-height: 1.35;
            font-weight: 800;
            color: #181b27;
        }

        .report-meta {
            margin-top: 8px;
            font-size: 10px;
            color: #9299aa;
        }

        .report-body {
            padding: 26px;
        }

        .report-body h1,
        .report-body h2,
        .report-body h3 {
            font-family: "Plus Jakarta Sans", sans-serif;
            color: #20232f;
        }

        .report-body p {
            color: #4f5668;
            line-height: 1.8;
            font-size: 13px;
        }

        .report-body li {
            color: #4f5668;
            line-height: 1.75;
            font-size: 13px;
        }

        /* =====================================================
           QUALITY / SOURCES
           ===================================================== */

        .info-card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 17px;
            padding: 19px;
            height: 100%;
            box-shadow: var(--shadow-sm);
        }

        .info-card-title {
            font-size: 12px;
            font-weight: 800;
            color: #272b38;
            margin-bottom: 15px;
        }

        .quality-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 9px 0;
            border-bottom: 1px solid #f0f1f5;
        }

        .quality-row:last-child {
            border-bottom: none;
        }

        .quality-label {
            font-size: 10px;
            color: #747c8f;
        }

        .quality-value {
            font-size: 10px;
            font-weight: 700;
            color: #2e3342;
        }

        .quality-good {
            color: var(--success);
        }

        .source-item {
            padding: 13px 0;
            border-bottom: 1px solid #f0f1f5;
        }

        .source-item:last-child {
            border-bottom: none;
        }

        .source-domain {
            font-size: 9px;
            color: var(--primary);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .source-title {
            margin-top: 4px;
            font-size: 11px;
            line-height: 1.5;
            font-weight: 600;
            color: #333847;
        }

        .source-link {
        font-family: "JetBrains Mono", monospace;
            margin-top: 4px;
            font-size: 9px;
            color: #969dad;
            overflow-wrap: anywhere;
        }

        .source-link a {
            color: inherit;
            text-decoration: none;
        }

        .source-link a:hover {
            color: var(--primary);
        }

        /* =====================================================
           METHODOLOGY
           ===================================================== */

        .methodology-card {
            background: linear-gradient(135deg, #FDF7FE 0%, #FFFFFF 100%);

         border: 1px solid #F0D8F3;
            border-radius: 18px;
            padding: 22px;
        }

        .methodology-title {
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 15px;
            font-weight: 800;
            color: #27293a;
        }

        .methodology-text {
            margin-top: 7px;
            font-size: 11px;
            color: #777e91;
            line-height: 1.7;
        }

        .agent-tags {
            display: flex;
            gap: 7px;
            flex-wrap: wrap;
            margin-top: 14px;
        }

        .agent-tag {
            padding: 6px 9px;
            border-radius: 7px;
            background: #ffffff;
            border: 1px solid #e2e0f7;
            color: #666d81;
            font-size: 9px;
            font-weight: 600;
        }

        /* =====================================================
           EMPTY STATE
           ===================================================== */

        .empty-card {
            margin-top: 25px;
            padding: 34px;
            text-align: center;
            background: #ffffff;
            border: 1px dashed #dfe2eb;
            border-radius: 18px;
        }

        .empty-icon {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: var(--primary-soft);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 12px auto;
            font-size: 18px;
            font-weight: 800;
        }

        .empty-title {
            font-size: 13px;
            font-weight: 700;
            color: #343846;
        }

        .empty-text {
            margin-top: 5px;
            font-size: 10px;
            color: #939aaa;
        }

        /* =====================================================
           RESPONSIVE
           ===================================================== */

        @media (max-width: 1000px) {
            .main .block-container {
                padding-left: 1.2rem;
                padding-right: 1.2rem;
            }

            .pipeline-grid,
            .metric-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

      @media (max-width: 700px) {
    .topbar {
        margin-bottom: 30px;
    }


    .hero-title {
        font-size: 44px !important;
    }
     .pipeline-grid,
                .metric-grid {
                    grid-template-columns: 1fr;
}

            }

            .composer-footer {
                display: block;
            }

            .composer-hints {
                margin-bottom: 10px;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TOP BAR
# ============================================================

def render_topbar():
    st.html(
        """
        <div class="topbar">
            <div class="topbar-left">
                <div class="topbar-dot"></div>
                <div class="topbar-text">System Ready</div>
            </div>

            <div class="tech-pill">
                LangGraph&nbsp;&nbsp;·&nbsp;&nbsp;Gemini
            </div>
        </div>
        """
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    with st.sidebar:

        st.html(
            """
            <div class="sidebar-brand">
                <div class="brand-row">
                    <div class="brand-icon">✦</div>

                    <div>
                        <div class="brand-title">
                            Agentic Research
                        </div>

                        <div class="brand-subtitle">
                            Multi-agent research engine
                        </div>
                    </div>
                </div>
            </div>
            """
        )

        st.html(
            """
            <div class="sidebar-section">
                <div class="sidebar-label">
                    AI Configuration
                </div>

                <div class="model-card">
                    <div class="model-name">
                        Gemini 2.5 Flash
                    </div>

                    <div class="model-provider">
                        Google Generative AI
                    </div>
                </div>

                <div class="status-card">
                    <div class="status-row">
                        <div class="status-dot"></div>
                        <div class="status-title">
                            All systems operational
                        </div>
                    </div>

                    <div class="status-desc">
                        Planner, search, verification and report
                        agents are connected.
                    </div>
                </div>
            </div>
            """
        )

        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

        st.html(
            """
            <div class="sidebar-section">
                <div class="sidebar-label">
                    Workspace
                </div>
            </div>
            """
        )

        if st.button(
            "＋  New Research",
            use_container_width=True,
            key="new_research",
        ):
            st.session_state["submitted_question"] = ""
            st.session_state["final_state"] = None
            st.session_state["run_status"] = {}
            st.rerun()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        st.html(
            """
            <div class="sidebar-section">
                <div class="sidebar-label">
                    Pipeline
                </div>
            </div>
            """
        )

        st.html(
            """
            <div style="
                padding: 0 18px 20px 18px;
                font-size: 10px;
                color: #8b92a3;
                line-height: 1.8;
            ">
                <div>01&nbsp;&nbsp; Research Planning</div>
                <div>02&nbsp;&nbsp; Web Research</div>
                <div>03&nbsp;&nbsp; Fact Verification</div>
                <div>04&nbsp;&nbsp; Report Generation</div>
            </div>
            """
        )


# ============================================================
# HERO
# ============================================================

def render_hero():
    st.html(
        """
        <div class="hero">

            <div class="hero-badge">
                <span class="hero-badge-dot"></span>
                Multi-Agent Research Engine
            </div>

            <div class="hero-title">
                Research anything.<br>
                <span class="hero-title-accent">
                    Understand everything.
                </span>
            </div>

            <div class="hero-subtitle">
                Ask a complex research question and let a coordinated
                team of AI agents plan, investigate, verify and
                synthesize the evidence into a structured report.
            </div>

        </div>
        """
    )


# ============================================================
# COMPOSER
# ============================================================

if "deep_research" not in st.session_state:
    st.session_state.deep_research = False


def render_composer():

    st.html(
        """
        <div class="composer-shell">

            <div class="composer-head">
                <div class="composer-label">
                    Research Question
                </div>
            </div>

        </div>
        """
    )

    deep_research = st.toggle(
        "Deep research mode",
        value=st.session_state.get("deep_research", False),
    )

    st.session_state.deep_research = deep_research

    with st.form("research_form", clear_on_submit=False):

        question = st.text_area(
            "Research Question",
            value=st.session_state.get("submitted_question", ""),
            placeholder=(
                "Ask a complex question...\n\n"
                "Example: What are the economic effects of remote "
                "work on urban housing markets?"
            ),
            height=155,
            label_visibility="collapsed",
        )

        st.html(
            """
            <div class="composer-footer">
                <div class="composer-hints">
                    <div class="hint-item">
                        <span class="hint-check">✓</span>
                        Multi-agent analysis
                    </div>

                    <div class="hint-item">
                        <span class="hint-check">✓</span>
                        Source verification
                    </div>

                    <div class="hint-item">
                        <span class="hint-check">✓</span>
                        Structured report
                    </div>
                </div>
            </div>
            """
        )

        submit = st.form_submit_button(
            "✦  Start Research",
            use_container_width=True,
        )

    return question, submit, deep_research


# ============================================================
# SUGGESTIONS
# ============================================================

def render_suggestions():
    st.html(
        """
        <div class="suggestions">
            <div class="suggestion-title">
                Try a research question
            </div>
        </div>
        """
    )

    cols = st.columns(3)

    for index, question in enumerate(EXAMPLE_QUESTIONS):

        with cols[index]:

            short_question = question

            if len(short_question) > 70:
                short_question = short_question[:67] + "..."

            if st.button(
                short_question,
                key=f"suggestion_{index}",
                use_container_width=True,
            ):
                st.session_state["submitted_question"] = question
                st.rerun()


# ============================================================
# PIPELINE
# ============================================================

def render_pipeline(statuses, deep_research=False):

    image_paths = {
        "planner": "agents/planner.png",
        "search": "agents/research.png",
        "verify": "agents/verification.png",
        "report": "agents/report.png",
    }

    images = {}

    for key, path in image_paths.items():
        image_data = image_to_base64(path)

        if image_data:
            images[key] = f"data:image/png;base64,{image_data}"
        else:
            images[key] = ""

    st.html(
        """
        <div class="section-space"></div>

        <div class="section-header">
            <div>
                <div class="section-kicker">
                    Execution Pipeline
                </div>

                <div class="section-title">
                    Four agents. One research workflow.
                </div>

                <div class="section-description">
                    Each stage contributes a specific part of the
                    research process.
                </div>
            </div>
        </div>
        """
    )

    # Research mode indicator
    if deep_research:

        mode_label = "Deep Research"
        mode_description = (
            "Independent research pass enabled for broader "
            "source coverage and evidence cross-checking."
        )

    else:

        mode_label = "Standard Research"
        mode_description = (
            "Single research pass focused on targeted "
            "evidence collection."
        )

    st.html(
        f"""
        <div class="info-card" style="margin-bottom: 18px;">

            <div class="info-card-title">
                Research Mode
            </div>

            <div class="quality-row">

                <div class="quality-label">
                    Mode
                </div>

                <div class="quality-value quality-good">
                    {safe_text(mode_label)}
                </div>

            </div>

            <div style="
                margin-top: 8px;
                font-size: 13px;
                line-height: 1.5;
                opacity: 0.75;
            ">
                {safe_text(mode_description)}
            </div>

        </div>
        """
    )

    cards = []

    for index, (key, name, description) in enumerate(STAGE_ORDER):

        status = statuses.get(key, "Waiting")

        if status == "Complete":
            css_class = "complete"

        elif status == "Running":
            css_class = "active"

        else:
            css_class = ""

        image_data = images.get(key, "")

        image_html = ""

        if image_data:

            image_html = f"""
                <img
                    class="pipeline-bg-image"
                    src="{image_data}"
                    alt=""
                    style="
                        position:absolute;
                        inset:0;
                        width:100%;
                        height:100%;
                        object-fit:cover;
                        object-position:center;
                        display:block;
                        z-index:0;
                    "
                >
            """

        cards.append(
            f"""
            <div class="pipeline-card {css_class}">

                {image_html}

                <div
                    style="
                        position:absolute;
                        inset:0;
                        z-index:1;
                        background:linear-gradient(
                            110deg,
                            rgba(255,255,255,0.94) 0%,
                            rgba(255,255,255,0.72) 48%,
                            rgba(255,255,255,0.28) 100%
                        );
                        pointer-events:none;
                    "
                ></div>

                <div class="pipeline-content">

                    <div class="pipeline-number">
                        {index + 1:02d}
                    </div>

                    <div class="pipeline-name">
                        {safe_text(name)}
                    </div>

                    <div class="pipeline-desc">
                        {safe_text(description)}
                    </div>

                    <div class="pipeline-status">
                        {safe_text(status)}
                    </div>

                </div>

            </div>
            """
        )

    st.html(
        f"""
        <div class="pipeline-grid">
            {''.join(cards)}
        </div>
        """
    )


# ============================================================
# METRICS
# ============================================================

def compute_metrics(state):

    sub_questions = state.get("sub_questions", []) or []
    findings = state.get("findings", []) or []
    verifications = state.get("verifications", []) or []

    sources = []

    for finding in findings:
        for source in finding.get("sources", []) or []:
            url = source.get("url")

            if url:
                sources.append(url)

    unique_sources = list(dict.fromkeys(sources))

    verified_count = 0

    if isinstance(verifications, list):
        verified_count = len(verifications)

    return {
        "sub_questions": len(sub_questions),
        "findings": len(findings),
        "sources": len(unique_sources),
        "verifications": verified_count,
    }


def render_metrics(state):

    metrics = compute_metrics(state)

    cards = [
        (
            "Research Tasks",
            metrics["sub_questions"],
            "Planner-generated questions",
        ),
        (
            "Findings",
            metrics["findings"],
            "Research observations",
        ),
        (
            "Sources",
            metrics["sources"],
            "Unique evidence sources",
        ),
        (
            "Verified",
            metrics["verifications"],
            "Verification results",
        ),
    ]

    html_cards = []

    for label, value, note in cards:
        html_cards.append(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    {safe_text(label)}
                </div>

                <div class="metric-value">
                    {safe_text(value)}
                </div>

                <div class="metric-note">
                    {safe_text(note)}
                </div>
            </div>
            """
        )

    st.html(
        f"""
        <div class="metric-grid">
            {''.join(html_cards)}
        </div>
        """
    )


# ============================================================
# REPORT
# ============================================================

def build_report_markdown(report: dict, question: str) -> str:
    """
    Converts the structured final_report dict into a clean Markdown string.
    Used both for on-screen display and for the Markdown export (Step 8).
    """
    lines = []

    title = report.get("title") or "Research Report"
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Research question:** {question}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append(report.get("executive_summary", ""))
    lines.append("")

    for section in report.get("sections", []):
        lines.append(f"## {section.get('heading', '')}")
        lines.append(section.get("content", ""))
        lines.append("")

    lines.append("## Confidence & Limitations")
    lines.append(report.get("confidence_notes", ""))
    lines.append("")

    sources = report.get("sources", [])

    if sources:
        lines.append("## Sources")
        seen = set()

        for src in sources:
            url = src.get("url")

            if url and url not in seen:
                seen.add(url)
                lines.append(f"- [{src.get('title', url)}]({url})")

        lines.append("")

    return "\n".join(lines)


def clean_pdf_source_url(url):
    """
    Cleans Google grounding redirect URLs and returns the
    actual source URL when available.
    """
    if not url:
        return ""

    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        for key in ("url", "u", "target", "dest", "destination", "link"):
            if key in query and query[key]:
                return unquote(query[key][0])

        return url

    except Exception:
        return url


def build_report_pdf(report: dict, question: str) -> bytes:
    """
    Converts the structured final_report dict into a Unicode-safe PDF.
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Unicode font
    font_path = r"C:\Windows\Fonts\arial.ttf"
    pdf.add_font("ArialUnicode", "", font_path)

    pdf.add_page()

    def write_heading(text, size=14):
        pdf.set_font("ArialUnicode", "", size)
        pdf.multi_cell(0, 8, str(text))
        pdf.ln(2)

    def write_body(text, size=11):
        pdf.set_font("ArialUnicode", "", size)
        pdf.multi_cell(0, 6, str(text))
        pdf.ln(3)

    title = report.get("title") or "Research Report"
    write_heading(title, size=16)

    write_body(f"Research question: {question}")

    write_heading("Executive Summary", size=13)
    write_body(report.get("executive_summary", ""))

    for section in report.get("sections", []):
        write_heading(section.get("heading", ""), size=13)
        write_body(section.get("content", ""))

    write_heading("Confidence & Limitations", size=13)
    write_body(report.get("confidence_notes", ""))

    sources = report.get("sources", [])

    if sources:
        write_heading("Sources", size=13)

        seen = set()

        for src in sources:
            url = src.get("url")

            if not url:
                continue

            clean_url = clean_pdf_source_url(url)

            if not clean_url or clean_url in seen:
                continue

            seen.add(clean_url)

            title = src.get("title") or clean_url

            write_body(
                f"- {title}: {clean_url}",
                size=10
            )

    return bytes(pdf.output())


def render_report(state):

    final_report = state.get("final_report")

    if not final_report or not isinstance(final_report, dict):
        st.html(
            """
            <div class="empty-card">
                <div class="empty-icon">✦</div>

                <div class="empty-title">
                    Your research report will appear here
                </div>

                <div class="empty-text">
                    Start a research task above to activate the
                    multi-agent pipeline.
                </div>
            </div>
            """
        )
        return

    question = state.get("main_question", "Research Report")

    report_markdown = build_report_markdown(
        final_report,
        question
    )

    # Decide report label based on verification results
    verifications = state.get("verifications", []) or []

    if verifications:
        report_label = "Verified Research"
        report_meta = (
            "Generated through the planner → search → "
            "verification → report workflow"
        )
    else:
        report_label = "Research Report"
        report_meta = (
            "Generated through the planner → search → "
            "report workflow"
        )

    st.html(
        f"""
        <div class="section-header">
            <div>
                <div class="section-kicker">
                    Final Output
                </div>

                <div class="section-title">
                    Research Report
                </div>
            </div>
        </div>

        <div class="report-card">

            <div class="report-header">

                <div class="report-label">
                    {safe_text(report_label)}
                </div>

                <div class="report-title">
                    {safe_text(final_report.get("title", question))}
                </div>

                <div class="report-meta">
                    {safe_text(report_meta)}
                </div>

            </div>

            <div class="report-body">
        """
    )

    st.markdown(report_markdown)

    st.html(
        """
            </div>
        </div>
        """
    )

    st.download_button(
        label="⬇ Download Markdown",
        data=report_markdown,
        file_name="research_report.md",
        mime="text/markdown",
        use_container_width=False,
    )

    pdf_bytes = build_report_pdf(
        final_report,
        question
    )

    st.download_button(
        label="⬇ Download PDF",
        data=pdf_bytes,
        file_name="research_report.pdf",
        mime="application/pdf",
        use_container_width=False,
    )


# ============================================================
# QUALITY
# ============================================================

def render_quality(state):

    findings = state.get("findings", []) or []
    verifications = state.get("verifications", []) or []

    source_count = 0

    for finding in findings:
        source_count += len(
            finding.get("sources", []) or []
        )

    st.html(
        """
        <div class="section-space"></div>

        <div class="section-header">
            <div>
                <div class="section-kicker">
                    Evidence & Quality
                </div>

                <div class="section-title">
                    Research quality overview
                </div>
            </div>
        </div>
        """
    )

    col1, col2 = st.columns(2)

    # -------------------------
    # Verification Status
    # -------------------------
    with col1:

        verified_label = (
            "Available"
            if verifications
            else "Not available"
        )

        st.html(
            f"""
            <div class="info-card">

                <div class="info-card-title">
                    Verification Status
                </div>

                <div class="quality-row">
                    <div class="quality-label">
                        Verification records
                    </div>

                    <div class="quality-value">
                        {len(verifications)}
                    </div>
                </div>

                <div class="quality-row">
                    <div class="quality-label">
                        Evidence references
                    </div>

                    <div class="quality-value">
                        {source_count}
                    </div>
                </div>

                <div class="quality-row">
                    <div class="quality-label">
                        Verification pipeline
                    </div>

                    <div class="quality-value quality-good">
                        {verified_label}
                    </div>
                </div>

            </div>
            """
        )

    # -------------------------
    # Verification Notes
    # -------------------------
    with col2:

        notes = []

        for verification in verifications:

            if not isinstance(verification, dict):
                continue

            verdict = verification.get("verdict")
            confidence = verification.get("confidence")
            relevance = verification.get("source_relevance_notes")
            agreement = verification.get("agreement_notes")
            flagged = verification.get("flagged_claims")

            note_parts = []

            if verdict:
                note_parts.append(
                    f"Verdict: {verdict}"
                )

            if confidence:
                note_parts.append(
                    f"Confidence: {confidence}"
                )

            if relevance:
                note_parts.append(
                    f"Source relevance: {relevance}"
                )

            if agreement:
                note_parts.append(
                    f"Agreement: {agreement}"
                )

            if flagged:

                if isinstance(flagged, list):
                    flagged_text = "; ".join(
                        str(item) for item in flagged
                    )
                else:
                    flagged_text = str(flagged)

                note_parts.append(
                    f"Flagged claims: {flagged_text}"
                )

            if note_parts:
                notes.append(
                    " | ".join(note_parts)
                )

        st.html(
            """
            <div class="info-card">

                <div class="info-card-title">
                    Verification Notes
                </div>
            """
        )

        if notes:

            for note in notes[:5]:
                st.markdown(
                    f"- {note}"
                )

        else:

            st.markdown(
                "Verification details will appear here after "
                "the verification agent completes its work."
            )

        st.html(
            """
            </div>
            """
        )


# ============================================================
# SOURCES
# ============================================================

def render_sources(state):

    findings = state.get("findings", []) or []

    source_map = {}

    def clean_source_url(url):

        if not url:
            return ""

        url = str(url).strip()

        # Try to extract the original URL from common
        # redirect/query parameters used by search systems.
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        redirect_keys = [
            "url",
            "u",
            "target",
            "dest",
            "destination",
            "link",
        ]

        for key in redirect_keys:

            values = params.get(key)

            if values:
                candidate = unquote(values[0])

                if candidate.startswith(
                    ("http://", "https://")
                ):
                    return candidate

        return url

    for finding in findings:

        for source in finding.get("sources", []) or []:

            raw_url = source.get("url")

            if not raw_url:
                continue

            url = clean_source_url(raw_url)

            if not url:
                continue

            if url not in source_map:

                source_map[url] = {
                    "title": source.get(
                        "title",
                        "Source"
                    ),
                    "url": url,
                }

    sources = list(source_map.values())

    st.html(
        """
        <div class="section-space"></div>

        <div class="section-header">
            <div>
                <div class="section-kicker">
                    Evidence
                </div>

                <div class="section-title">
                    Sources used in the research
                </div>

                <div class="section-description">
                    Links collected by the research agent.
                </div>
            </div>
        </div>
        """
    )

    if not sources:

        st.html(
            """
            <div class="empty-card">

                <div class="empty-icon">
                    ⌕
                </div>

                <div class="empty-title">
                    No sources available yet
                </div>

                <div class="empty-text">
                    Sources will appear after the research agent
                    completes its search.
                </div>

            </div>
            """
        )

        return

    source_html = []

    for source in sources:

        url = source["url"]
        title = source["title"]
        domain = get_domain(url)

        safe_url = html.escape(
            url,
            quote=True
        )

        safe_title = html.escape(
            str(title)
        )

        safe_domain = html.escape(
            str(domain)
        )

        source_html.append(
            f"""
            <div class="source-item">

                <div class="source-domain">
                    {safe_domain}
                </div>

                <div class="source-title">
                    {safe_title}
                </div>

                <div class="source-link">

                    <a
                        href="{safe_url}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Open source ↗
                    </a>

                </div>

            </div>
            """
        )

    st.html(
        f"""
        <div class="info-card">
            {''.join(source_html)}
        </div>
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

def render_methodology():

    st.html(
        """
        <div class="section-space"></div>

        <div class="methodology-card">

            <div class="methodology-title">
                How this research assistant works
            </div>

            <div class="methodology-text">
                Instead of asking a single model to answer the entire
                question at once, the system separates research into
                specialized stages. Each agent has a focused job,
                while LangGraph coordinates the complete workflow.
            </div>

            <div class="agent-tags">
                <div class="agent-tag">
                    Research Planner
                </div>

                <div class="agent-tag">
                    Search Agent
                </div>

                <div class="agent-tag">
                    Verification Agent
                </div>

                <div class="agent-tag">
                    Report Writer
                </div>

                <div class="agent-tag">
                    LangGraph
                </div>

                <div class="agent-tag">
                    Gemini
                </div>
            </div>

        </div>
        """
    )


# ============================================================
# PIPELINE EXECUTION
# ============================================================

def is_valid_research_question(question: str) -> bool:
    """
    Checks whether the user entered a meaningful research question.
    Prevents unnecessary API calls for greetings or very short inputs.
    """

    if not question:
        return False

    question = question.strip()

    if len(question) < 10:
        return False

    invalid_inputs = {
        "hi",
        "hello",
        "hey",
        "how are you",
        "how r u",
        "good morning",
        "good afternoon",
        "good evening",
        "thanks",
        "thank you",
    }

    if question.lower() in invalid_inputs:
        return False

    return True


def run_pipeline(question, deep_research=False):

    

    graph = build_graph()

    initial_state = {
        "main_question": question,
        "sub_questions": [],
        "key_topics": [],
        "findings": [],
        "verifications": [],
        "final_report": "",
        "deep_research": deep_research,
    }

    final_state = initial_state.copy()

    statuses = {
        "planner": "Waiting",
        "search": "Waiting",
        "verify": "Waiting",
        "report": "Waiting",
    }

    # Actual node names from graph.py
    stage_map = {
        "planner": "planner",
        "search": "search",
        "verify": "verify",
        "report": "report",
    }

    progress_placeholder = st.empty()

    def render_progress(current_stage=None):

        rows = []

        for key, name, description in STAGE_ORDER:

            status = statuses.get(key, "Waiting")

            if status == "Complete":
                icon = "✓"

            elif status == "Running":
                icon = "●"

            else:
                icon = "○"

            rows.append(
                f"""
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    padding:9px 0;
                    border-bottom:1px solid #f0edf3;
                ">
                    <span style="
                        font-size:11px;
                        color:#4f5668;
                    ">
                        <b style="color:#A21CAF;">
                            {icon}
                        </b>
                        &nbsp;
                        {safe_text(name)}
                    </span>

                    <span style="
                        font-size:9px;
                        color:#8b8494;
                        font-weight:700;
                        text-transform:uppercase;
                    ">
                        {status}
                    </span>
                </div>
                """
            )

        if current_stage:
            current_text = f"Running {current_stage}..."
        else:
            current_text = "Preparing research pipeline..."

        if deep_research:
            mode_text = "Deep Research enabled"
        else:
            mode_text = "Standard Research"

        progress_placeholder.html(
            f"""
            <div style="
                max-width:900px;
                margin:20px auto 25px auto;
                padding:20px 22px;
                background:#ffffff;
                border:1px solid #E5E1EB;
                border-radius:17px;
                box-shadow:0 8px 25px rgba(30,27,46,0.05);
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">

                    <div style="
                        font-size:13px;
                        font-weight:800;
                        color:#272b38;
                    ">
                        Research in progress
                    </div>

                    <div style="
                        font-size:9px;
                        font-weight:700;
                        color:#A21CAF;
                        text-transform:uppercase;
                    ">
                        {safe_text(mode_text)}
                    </div>

                </div>

                <div style="
                    font-size:10px;
                    color:#8b8494;
                    margin-top:5px;
                    margin-bottom:10px;
                ">
                    {safe_text(current_text)}
                </div>

                {''.join(rows)}

            </div>
            """
        )

    try:

        render_progress()

        for update in graph.stream(
            initial_state,
            stream_mode="updates",
        ):

            for node_name, node_state in update.items():

                if isinstance(node_state, dict):
                    final_state.update(node_state)

                stage = stage_map.get(node_name)

                if not stage:
                    continue

                current_index = next(
                    i
                    for i, item in enumerate(STAGE_ORDER)
                    if item[0] == stage
                )

                for index, item in enumerate(STAGE_ORDER):

                    key = item[0]

                    if index < current_index:
                        statuses[key] = "Complete"

                    elif index == current_index:
                        statuses[key] = "Running"

                    else:
                        statuses[key] = "Waiting"

                current_name = next(
                    item[1]
                    for item in STAGE_ORDER
                    if item[0] == stage
                )

                render_progress(current_name)

                statuses[stage] = "Complete"

        for key in statuses:
            statuses[key] = "Complete"

        render_progress("Research completed")

        return final_state, statuses

    except Exception:
        progress_placeholder.empty()
        raise


# ============================================================
# APP INITIALIZATION
# ============================================================

init_db()
inject_css()
render_sidebar()

if "submitted_question" not in st.session_state:
    st.session_state["submitted_question"] = ""

if "final_state" not in st.session_state:
    st.session_state["final_state"] = None

if "run_status" not in st.session_state:
    st.session_state["run_status"] = {}

render_topbar()
render_hero()


# ============================================================
# START RESEARCH
# ============================================================

question, submit, deep_research = render_composer()
render_suggestions()

if submit:

    question = question.strip()

    if not is_valid_research_question(question):

        st.warning(
            "Please enter a meaningful research question "
            "before starting research."
        )

    else:

        st.session_state["submitted_question"] = question

        st.markdown(
            "<div style='height:30px'></div>",
            unsafe_allow_html=True,
        )

        try:

            with st.spinner(
                "Your research agents are working..."
            ):

                result = run_pipeline(
                    question,
                    deep_research
                )

            if result is None:
                st.stop()

            final_state, statuses = result

            st.session_state["final_state"] = final_state
            st.session_state["run_status"] = statuses

            save_research(
                question,
                final_state
            )

            st.rerun()

        except Exception as e:

            st.error("Research pipeline failed.")

            error_text = str(e).upper()

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                st.warning(
                    "The Gemini API rate limit or quota was reached. "
                    "Please wait and try again later."
                )

            elif "API KEY" in error_text or "UNAUTHENTICATED" in error_text:

                st.warning(
                    "The Gemini API key appears to be invalid or "
                    "not configured correctly. Please check your .env file."
                )

            elif "TIMEOUT" in error_text or "DEADLINE" in error_text:

                st.warning(
                    "The research request timed out. "
                    "Please try again."
                )

            elif "CONNECTION" in error_text or "NETWORK" in error_text:

                st.warning(
                    "A network connection problem occurred while "
                    "accessing the research service. Please try again."
                )

            else:

                st.warning(
                    "An unexpected error occurred while running the "
                    "research pipeline. Please try again."
                )

            st.caption(
                "Technical error details are shown below for debugging."
            )

            st.exception(e)



# ============================================================
# RESULTS
# ============================================================

final_state = st.session_state.get("final_state")

if final_state:

    render_pipeline(
        st.session_state.get("run_status", {}),
        final_state.get("deep_research", False)
    )

    render_metrics(final_state)

    render_report(final_state)

    render_quality(final_state)

    render_sources(final_state)

    render_methodology()

else:

    st.html(
        """
        <div class="section-space"></div>

        <div class="section-header">
            <div>
                <div class="section-kicker">
                    Agent Architecture
                </div>

                <div class="section-title">
                    Built for deeper research
                </div>

                <div class="section-description">
                    A coordinated workflow designed to separate
                    planning, discovery, verification and synthesis.
                </div>
            </div>
        </div>
        """
    )