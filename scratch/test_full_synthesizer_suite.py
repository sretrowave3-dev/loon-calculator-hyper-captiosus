import re
import urllib.request
import urllib.parse
import ssl
import json
import html
import sys

sys.stdout.reconfigure(encoding='utf-8')

class DirectSolutionSynthesizer:
    
    @classmethod
    def synthesize_direct_solution(cls, prompt: str) -> dict:
        p = prompt.strip()
        low = p.lower()

        # 1. Math / Arithmetic / Percentage
        math_sol = cls._try_solve_math(p, low)
        if math_sol:
            return math_sol

        # 2. Unit Conversions
        unit_sol = cls._try_solve_units(p, low)
        if unit_sol:
            return unit_sol

        # 3. Coding / Programming Solutions
        code_sol = cls._try_solve_coding(p, low)
        if code_sol:
            return code_sol

        # 4. Factual Knowledge Consensus Extraction (Web + Wiki)
        return cls._solve_factual_query(p)

    @classmethod
    def _try_solve_math(cls, prompt: str, low: str) -> dict:
        # A. Percentage
        m_pct = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|percent(?:age)?)\s*(?:of)?\s*(\d+(?:\.\d+)?)', low)
        if m_pct:
            pct = float(m_pct.group(1))
            val = float(m_pct.group(2))
            res = (pct / 100.0) * val
            return {
                "type": "math",
                "direct_solution": f"{pct:g}% of {val:g} = {res:.6g}",
                "detail": f"Calculation: ({pct:g} / 100) × {val:g} = {res:.6g}",
                "steps": [
                    f"Formula: Result = (P / 100) × Base",
                    f"Substitute: ({pct:g} / 100) × {val:g}",
                    f"Final Value: {res:.6g}"
                ]
            }

        # B. Percentage off / discount
        m_disc = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:off|discount)\s*(?:of|on)?\s*(\d+(?:\.\d+)?)', low)
        if m_disc:
            pct = float(m_disc.group(1))
            val = float(m_disc.group(2))
            savings = (pct / 100.0) * val
            final_p = val - savings
            return {
                "type": "math",
                "direct_solution": f"{pct:g}% off {val:g} = {final_p:.6g} (Savings: {savings:.6g})",
                "detail": f"Discount Amount: {savings:.6g} | Final Price: {val:g} - {savings:.6g} = {final_p:.6g}",
                "steps": [
                    f"Calculate discount: {val:g} × {pct:g}% = {savings:.6g}",
                    f"Subtract from original: {val:g} - {savings:.6g} = {final_p:.6g}"
                ]
            }

        # C. Simple Arithmetic evaluation
        clean_arith = re.sub(r'^(?:what\s+is|calculate|eval|compute|solve|find)\s+', '', prompt, flags=re.I).rstrip('?').strip()
        if re.match(r'^[0-9\s.+\-*/^()%]+$', clean_arith) and any(op in clean_arith for op in '+-*/^%'):
            try:
                py_expr = clean_arith.replace('^', '**')
                val = eval(py_expr, {'__builtins__': {}}, {})
                if isinstance(val, (int, float)):
                    return {
                        "type": "math",
                        "direct_solution": f"{clean_arith} = {val:.10g}",
                        "detail": f"Exact evaluated numerical value: {val:.10g}",
                        "steps": [
                            f"Expression: {clean_arith}",
                            f"Evaluation: {val:.10g}"
                        ]
                    }
            except Exception:
                pass

        # D. Linear equation solver: e.g. 3x + 5 = 20 or 2x - 4 = 10
        m_eq = re.search(r'([+-]?\s*\d*(?:\.\d+)?)\s*\*?\s*x\s*([+-]\s*\d+(?:\.\d+)?)\s*=\s*([+-]?\s*\d+(?:\.\d+)?)', clean_arith, re.I)
        if m_eq:
            try:
                a_str = m_eq.group(1).replace(' ', '')
                if not a_str or a_str == '+':
                    a = 1.0
                elif a_str == '-':
                    a = -1.0
                else:
                    a = float(a_str)
                b = float(m_eq.group(2).replace(' ', ''))
                c = float(m_eq.group(3).replace(' ', ''))
                if abs(a) > 1e-12:
                    x_sol = (c - b) / a
                    return {
                        "type": "math",
                        "direct_solution": f"x = {x_sol:.6g}",
                        "detail": f"Solving {a:g}x + ({b:g}) = {c:g}  ==>  {a:g}x = {c - b:g}  ==>  x = {x_sol:.6g}",
                        "steps": [
                            f"Original Equation: {a:g}x + ({b:g}) = {c:g}",
                            f"Subtract constant {b:g} from both sides: {a:g}x = {c - b:g}",
                            f"Divide by coefficient {a:g}: x = {x_sol:.6g}"
                        ]
                    }
            except Exception:
                pass

        return None

    @classmethod
    def _try_solve_units(cls, prompt: str, low: str) -> dict:
        conversions = [
            (r'(\d+(?:\.\d+)?)\s*(?:km|kilometers?)\s*(?:to|in)\s*(?:miles?|mi)', 0.621371, "km", "miles"),
            (r'(\d+(?:\.\d+)?)\s*(?:miles?|mi)\s*(?:to|in)\s*(?:km|kilometers?)', 1.60934, "miles", "km"),
            (r'(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)\s*(?:to|in)\s*(?:lbs?|pounds?)', 2.20462, "kg", "lbs"),
            (r'(\d+(?:\.\d+)?)\s*(?:lbs?|pounds?)\s*(?:to|in)\s*(?:kg|kilograms?)', 0.453592, "lbs", "kg"),
            (r'(\d+(?:\.\d+)?)\s*(?:meters?|m)\s*(?:to|in)\s*(?:feet|ft)', 3.28084, "meters", "feet"),
            (r'(\d+(?:\.\d+)?)\s*(?:feet|ft)\s*(?:to|in)\s*(?:meters?|m)', 0.3048, "feet", "meters"),
            (r'(\d+(?:\.\d+)?)\s*(?:inches?|in)\s*(?:to|in)\s*(?:cm|centimeters?)', 2.54, "inches", "cm"),
            (r'(\d+(?:\.\d+)?)\s*(?:cm|centimeters?)\s*(?:to|in)\s*(?:inches?|in)', 0.393701, "cm", "inches"),
            (r'(\d+(?:\.\d+)?)\s*(?:gb|gigabytes?)\s*(?:to|in)\s*(?:mb|megabytes?)', 1024.0, "GB", "MB"),
            (r'(\d+(?:\.\d+)?)\s*(?:mb|megabytes?)\s*(?:to|in)\s*(?:kb|kilobytes?)', 1024.0, "MB", "KB"),
            (r'(\d+(?:\.\d+)?)\s*(?:gb|gigabytes?)\s*(?:to|in)\s*(?:bytes?)', 1073741824.0, "GB", "bytes"),
        ]
        for pat, factor, u_from, u_to in conversions:
            m = re.search(pat, low)
            if m:
                val = float(m.group(1))
                res = val * factor
                return {
                    "type": "unit",
                    "direct_solution": f"{val:g} {u_from} = {res:.6g} {u_to}",
                    "detail": f"Conversion Factor: 1 {u_from} = {factor:g} {u_to}",
                    "steps": [
                        f"Formula: Value in {u_to} = (Value in {u_from}) × {factor:g}",
                        f"Calculation: {val:g} × {factor:g} = {res:.6g} {u_to}"
                    ]
                }

        # Temperature
        m_c2f = re.search(r'(\d+(?:\.\d+)?)\s*(?:c|celsius)\s*(?:to|in)\s*(?:f|fahrenheit)', low)
        if m_c2f:
            c = float(m_c2f.group(1))
            f = (c * 9.0 / 5.0) + 32.0
            return {
                "type": "unit",
                "direct_solution": f"{c:g} °C = {f:.4g} °F",
                "detail": f"Formula: (°C × 9/5) + 32 = °F",
                "steps": [f"({c:g} × 1.8) + 32 = {f:.4g} °F"]
            }

        m_f2c = re.search(r'(\d+(?:\.\d+)?)\s*(?:f|fahrenheit)\s*(?:to|in)\s*(?:c|celsius)', low)
        if m_f2c:
            f = float(m_f2c.group(1))
            c = (f - 32.0) * 5.0 / 9.0
            return {
                "type": "unit",
                "direct_solution": f"{f:g} °F = {c:.4g} °C",
                "detail": f"Formula: (°F - 32) × 5/9 = °C",
                "steps": [f"({f:g} - 32) × 5/9 = {c:.4g} °C"]
            }

        return None

    @classmethod
    def _try_solve_coding(cls, prompt: str, low: str) -> dict:
        is_code = bool(re.search(r'\b(?:write|code|create|generate|implement|script|program|algorithm)\b', low) and
                       re.search(r'\b(?:python|c|cpp|java|javascript|function|algorithm|stack|queue|sort|search|tree|fibonacci|prime|factorial)\b', low))
        if not is_code and not any(k in low for k in ("quicksort", "binary search", "mergesort", "bubblesort", "linked list", "fibonacci", "factorial")):
            return None

        # Check catalog
        if "quicksort" in low:
            code = (
                "def quicksort(arr):\n"
                "    if len(arr) <= 1:\n"
                "        return arr\n"
                "    pivot = arr[len(arr) // 2]\n"
                "    left = [x for x in arr if x < pivot]\n"
                "    middle = [x for x in arr if x == pivot]\n"
                "    right = [x for x in arr if x > pivot]\n"
                "    return quicksort(left) + middle + quicksort(right)\n\n"
                "# Test execution:\n"
                "test_data = [64, 25, 12, 22, 11, 90]\n"
                "print('Sorted Array:', quicksort(test_data))  # [11, 12, 22, 25, 64, 90]"
            )
            return {
                "type": "code",
                "direct_solution": "Quicksort Algorithm Implementation (Python):",
                "code": code,
                "complexity": "Time Complexity: O(n log n) average, O(n²) worst-case | Space: O(log n)",
                "steps": [
                    "Pick a pivot element from the middle of the sequence.",
                    "Partition elements into three sublists: less than, equal to, and greater than pivot.",
                    "Recursively sort partitions and concatenate."
                ]
            }

        if "binary search" in low:
            code = (
                "def binary_search(arr, target):\n"
                "    low, high = 0, len(arr) - 1\n"
                "    while low <= high:\n"
                "        mid = (low + high) // 2\n"
                "        if arr[mid] == target:\n"
                "            return mid  # Target index found\n"
                "        elif arr[mid] < target:\n"
                "            low = mid + 1\n"
                "        else:\n"
                "            high = mid - 1\n"
                "    return -1  # Target not found\n\n"
                "# Test execution (input must be sorted):\n"
                "arr = [10, 20, 30, 40, 50, 60, 70]\n"
                "idx = binary_search(arr, 40)\n"
                "print(f'Element 40 found at index: {idx}')  # Index: 3"
            )
            return {
                "type": "code",
                "direct_solution": "Binary Search Algorithm (Python):",
                "code": code,
                "complexity": "Time Complexity: O(log n) | Space Complexity: O(1)",
                "steps": [
                    "Requires a sorted collection as precondition.",
                    "Compares search key with middle array element.",
                    "Discards half the search interval on each comparison until found."
                ]
            }

        if "fibonacci" in low:
            code = (
                "def fibonacci(n):\n"
                "    if n <= 0:\n"
                "        return []\n"
                "    if n == 1:\n"
                "        return [0]\n"
                "    seq = [0, 1]\n"
                "    while len(seq) < n:\n"
                "        seq.append(seq[-1] + seq[-2])\n"
                "    return seq\n\n"
                "# Test execution:\n"
                "print('First 10 Fibonacci numbers:', fibonacci(10))\n"
                "# Output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]"
            )
            return {
                "type": "code",
                "direct_solution": "Fibonacci Sequence Generator (Python):",
                "code": code,
                "complexity": "Time Complexity: O(n) | Space Complexity: O(n)",
                "steps": [
                    "Initializes base terms F(0) = 0 and F(1) = 1.",
                    "Iteratively computes each next term as sum of previous two: F(n) = F(n-1) + F(n-2)."
                ]
            }

        if "reverse" in low and ("string" in low or "str" in low):
            code = (
                "def reverse_string(s):\n"
                "    # Method 1: Pythonic slice (O(n))\n"
                "    return s[::-1]\n\n"
                "# Test:\n"
                "original = 'Calculus Engine'\n"
                "print(f'Reversed: {reverse_string(original)}')  # 'enignE suluclaC'"
            )
            return {
                "type": "code",
                "direct_solution": "String Reversal Solution (Python):",
                "code": code,
                "complexity": "Time Complexity: O(n) | Space Complexity: O(n)",
                "steps": [
                    "Uses Python step-slice notation s[::-1] for efficient in-memory string reversal."
                ]
            }

        if "prime" in low:
            code = (
                "def is_prime(n):\n"
                "    if n < 2:\n"
                "        return False\n"
                "    if n in (2, 3):\n"
                "        return True\n"
                "    if n % 2 == 0 or n % 3 == 0:\n"
                "        return False\n"
                "    i = 5\n"
                "    while i * i <= n:\n"
                "        if n % i == 0 or n % (i + 2) == 0:\n"
                "            return False\n"
                "        i += 6\n"
                "    return True\n\n"
                "# Test:\n"
                "print('Is 97 prime?', is_prime(97))  # True\n"
                "print('Is 100 prime?', is_prime(100)) # False"
            )
            return {
                "type": "code",
                "direct_solution": "Optimized Prime Number Checker (O(√n)):",
                "code": code,
                "complexity": "Time: O(√n) with 6k±1 optimization | Space: O(1)",
                "steps": [
                    "Handles base cases (n < 2 is False, 2 and 3 are True).",
                    "Checks divisibility by 6k±1 up to √n."
                ]
            }

        return None

    @classmethod
    def _solve_factual_query(cls, query: str) -> dict:
        clean_q = re.sub(r'^(?:who\s+is|what\s+is|tell\s+me\s+about|explain|describe)\s+', '', query.strip(), flags=re.I).rstrip('?').strip()
        ctx = ssl.create_default_context()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Multi-Search: 1. DuckDuckGo Lite
        ddg_items = []
        try:
            ddg_data = urllib.parse.urlencode({'q': query}).encode('utf-8')
            req_d = urllib.request.Request('https://lite.duckduckgo.com/lite/', data=ddg_data, headers=headers)
            with urllib.request.urlopen(req_d, timeout=4.5, context=ctx) as r_d:
                body = r_d.read().decode('utf-8', errors='ignore')
                links = re.findall(r'<a[^>]+class=["\']result-link["\'][^>]*>(.*?)</a>', body, re.DOTALL)
                snippets = re.findall(r'<td[^>]+class=["\']result-snippet["\'][^>]*>(.*?)</td>', body, re.DOTALL)
                for i in range(min(len(links), len(snippets))):
                    lt = html.unescape(re.sub(r'<[^>]+>', '', links[i])).strip()
                    sn = html.unescape(re.sub(r'<[^>]+>', ' ', snippets[i])).strip()
                    sn = re.sub(r'\s+', ' ', sn)
                    if lt and sn and not any(k in sn.lower() for k in ("sponsored", "advertisement", "duckduckgo")):
                        ddg_items.append({"title": lt, "snippet": sn})
        except Exception:
            pass

        # Multi-Search: 2. Wikipedia Direct Extract
        wiki_extract = ""
        try:
            w_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={urllib.parse.quote(clean_q)}&format=json"
            req_w = urllib.request.Request(w_url, headers={"User-Agent": "SmartAssistant/2.0"})
            with urllib.request.urlopen(req_w, timeout=4.0, context=ctx) as r_w:
                wdata = json.loads(r_w.read().decode('utf-8'))
                pages = wdata.get('query', {}).get('pages', {})
                for _, p in pages.items():
                    ext = p.get('extract', '').strip()
                    if ext and len(ext) > 30:
                        wiki_extract = ext
                        break
        except Exception:
            pass

        # Clean citations: [1], [2], [a], etc.
        def clean_citations(text: str) -> str:
            t = re.sub(r'\[\s*\d+\s*\]', '', text)
            t = re.sub(r'\(/[^/]+/\s*ⓘ?[,;]?\s*\)', '', t)
            t = re.sub(r'\([a-zA-Z\s]+:\s*\[[^\]]+\]\s*ⓘ?\)', '', t)
            t = re.sub(r'\s+', ' ', t).strip()
            return t

        direct_solution = ""
        detail_lines = []

        # Analyze DDG Snippets for direct answer
        if ddg_items:
            # Check top snippet
            top_snip = clean_citations(ddg_items[0]["snippet"])
            top_title = re.sub(r'\s*[-|–]\s*(?:Wikipedia|Britannica|WorldAtlas|Investopedia).*$', '', ddg_items[0]["title"], flags=re.I).strip()

            # Pattern 1: Direct definition / identity: "X is the capital city of Canada"
            sentences = re.split(r'(?<=[.!?])\s+', top_snip)
            for s in sentences:
                s_low = s.lower()
                if any(k in s_low for k in ("is the capital", "was the capital", "is located in", "discovered by", "invented by", "equals", "result is", "stands for")):
                    direct_solution = s
                    break
            
            # Pattern 2: Title has answer: e.g. "Ottawa - Facts & Why It Was Chosen"
            if not direct_solution and top_title and not clean_q.lower() in top_title.lower():
                direct_solution = f"{top_title}: {sentences[0] if sentences else top_snip[:120]}"

            if not direct_solution and sentences:
                direct_solution = sentences[0]

            for item in ddg_items[:3]:
                c_snip = clean_citations(item["snippet"])
                if len(c_snip) > 130:
                    c_snip = c_snip[:130] + "..."
                detail_lines.append(f"{item['title']}: {c_snip}")

        # Fallback to Wikipedia extract
        if not direct_solution and wiki_extract:
            cleaned_wiki = clean_citations(wiki_extract)
            wiki_sents = re.split(r'(?<=[.!?])\s+', cleaned_wiki)
            direct_solution = wiki_sents[0] if wiki_sents else cleaned_wiki[:150]
            if len(wiki_sents) > 1:
                detail_lines.append(f"Wikipedia Background: {wiki_sents[1]}")

        if not direct_solution:
            direct_solution = f"Inquiry routed to Google Gemini: \"{query}\""
            detail_lines.append("No offline web consensus established. Use the Gemini session actions below.")

        return {
            "type": "factual",
            "direct_solution": direct_solution,
            "steps": detail_lines
        }

    @classmethod
    def format_solution_display(cls, query: str, sol: dict, session_url: str, session_title: str, tag: str) -> str:
        q_type = sol.get("type", "general")
        direct_ans = sol.get("direct_solution", "")
        steps = sol.get("steps", [])
        code = sol.get("code")
        complexity = sol.get("complexity")
        detail = sol.get("detail")

        lines = [
            f"╔══════════════════════════════════════════════════════════════════════════════╗",
            f"║ [{tag:<74}] ║",
            f"╚══════════════════════════════════════════════════════════════════════════════╝",
            f" Target Session : {session_title}",
            f" User Inquiry   : \"{query}\"",
            f"--------------------------------------------------------------------------------",
            f"╔══════════════════════════════════════════════════════════════════════════════╗",
            f"║ 🎯 ACTUAL DIRECT SOLUTION                                                    ║",
            f"╚══════════════════════════════════════════════════════════════════════════════╝",
            f" ▶ {direct_ans}",
        ]
        if detail:
            lines.append(f" ▶ {detail}")

        if code:
            lines.append(f"--------------------------------------------------------------------------------")
            lines.append(f"💻 EXECUTABLE CODE IMPLEMENTATION:")
            lines.append(code)
            if complexity:
                lines.append(f"")
                lines.append(f"📊 {complexity}")

        if steps:
            lines.append(f"--------------------------------------------------------------------------------")
            lines.append(f"📝 STEP-BY-STEP BREAKDOWN & CONSENSUS PROOF:")
            for st in steps:
                lines.append(f"  • {st}")

        lines.extend([
            f"================================================================================",
            f" Seamless Gemini Actions:",
            f"  • Direct Thread Link  : {session_url}",
            f"  • Open in Browser     : Type 'gemini open' to jump straight to your thread.",
            f"  • Type & Send Now     : Type 'gemini send {query}' to auto-paste into Gemini.",
            f"  • Connect API Key     : Type 'gemini key <your_key>' for direct ultra-fast API chat.",
            f"================================================================================"
        ])
        return "\n".join(lines)


# Run Test Cases
test_queries = [
    "what is 20 percent of 750",
    "what is 15% discount on 200",
    "solve 3x + 5 = 20",
    "100 km to miles",
    "100 celsius to fahrenheit",
    "write a python script for quicksort",
    "binary search in python",
    "what is the capital of Canada?",
    "who discovered penicillin?"
]

for tq in test_queries:
    sol = DirectSolutionSynthesizer.synthesize_direct_solution(tq)
    formatted = DirectSolutionSynthesizer.format_solution_display(
        tq, sol, "https://gemini.google.com/app/6930d10672c1261c",
        "Program Integration Preparation - Google Gemini",
        "⚡ AUTO-ROUTED TO GEMINI | OUT OF MATH DOMAIN"
    )
    print(formatted)
    print("\n" + "#" * 80 + "\n")
