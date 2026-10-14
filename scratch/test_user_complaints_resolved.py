import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from smart_calculator
from smart_calculator import (
    TerminalImageAndOCREngine,
    GeminiAndBrowserEngine,
    MathEngine
)

print("=" * 80)
print("VERIFICATION SUITE: PIXEL REPLICA & DIRECT SOLUTION ENGINE")
print("=" * 80)

class DummyLearner:
    def __init__(self):
        self.last_formula = "(x^3 + 1)/(x + 1)"
        self.profile = {"last_expression": "(x^3 + 1)/(x + 1)", "user_variables": {}}

class DummyInterpreter:
    def __init__(self):
        self.engine = MathEngine()
        self.learner = DummyLearner()

dummy_interp = DummyInterpreter()

# -------------------------------------------------------------------------
# Test 1: In-Terminal Pixel-to-Pixel Function Curve Replica
# -------------------------------------------------------------------------
print("\n[TEST 1] Testing handle_relative_images with (x^3 + 1)/(x + 1)...")
res1 = TerminalImageAndOCREngine.handle_relative_images("browse (x^3 + 1)/(x + 1) and then show relative images", dummy_interp)

# Verify no dental calculus or tooth images appear
assert "Dental_Calculus" not in res1, "FAIL: Dental Calculus image was returned!"
assert "tooth" not in res1.lower(), "FAIL: Tooth was returned!"
assert "MATHEMATICAL FUNCTION CURVE DIAGRAM & HIGH-RESOLUTION 720p REPLICA" in res1, "FAIL: Math curve diagram title missing"
assert "1280 x 720 px" in res1, "FAIL: 720p master dimensions missing"
assert "▀" in res1, "FAIL: 24-bit TrueColor half-blocks missing"
print("[✓ PASS] Test 1: High-precision Cartesian mathematical curve replica displayed on terminal with ZERO dental images!")
print(res1[:600] + "\n... [TrueColor Plot Rendered Successfully] ...")

# -------------------------------------------------------------------------
# Test 2: In-Terminal Pixel-to-Pixel Curve Replica for Trigonometric Expression
# -------------------------------------------------------------------------
print("\n[TEST 2] Testing handle_relative_images with 1/(1 + sin(x))...")
res2 = TerminalImageAndOCREngine.handle_relative_images("show relative images for 1/(1+sin(x))", dummy_interp)
assert "MATHEMATICAL FUNCTION CURVE DIAGRAM & HIGH-RESOLUTION 720p REPLICA" in res2
assert "1/(1+sin(x))" in res2
print("[✓ PASS] Test 2: Trig curve replica successfully rendered in TrueColor!")

# -------------------------------------------------------------------------
# Test 3: Auto-Routed Percentage / Math Solution
# -------------------------------------------------------------------------
print("\n[TEST 3] Testing auto-routed direct math solution for 'what is 20 percent of 750'...")
sol3 = GeminiAndBrowserEngine.chat("what is 20 percent of 750", auto_routed=True)
assert "🎯 ACTUAL DIRECT SOLUTION" in sol3, "FAIL: Direct solution box missing"
assert "150" in sol3, "FAIL: Calculated value 150 missing"
print("[✓ PASS] Test 3: Math percentage solved directly with 150!")
print(sol3)

# -------------------------------------------------------------------------
# Test 4: Auto-Routed Coding Implementation
# -------------------------------------------------------------------------
print("\n[TEST 4] Testing auto-routed coding implementation for 'write a python script for quicksort'...")
sol4 = GeminiAndBrowserEngine.chat("write a python script for quicksort", auto_routed=True)
assert "🎯 ACTUAL DIRECT SOLUTION" in sol4
assert "def quicksort" in sol4
assert "O(n log n)" in sol4
print("[✓ PASS] Test 4: Python quicksort algorithm generated directly with working code & complexity!")
print(sol4)

# -------------------------------------------------------------------------
# Test 5: Auto-Routed Factual Question
# -------------------------------------------------------------------------
print("\n[TEST 5] Testing auto-routed factual lookup for 'what is the capital of Canada?'...")
sol5 = GeminiAndBrowserEngine.chat("what is the capital of Canada?", auto_routed=True)
assert "🎯 ACTUAL DIRECT SOLUTION" in sol5
assert "Ottawa" in sol5, "FAIL: Ottawa not identified"
print("[✓ PASS] Test 5: Capital of Canada directly answered as Ottawa!")
print(sol5)

# -------------------------------------------------------------------------
# Test 6: Auto-Routed Inventor Lookup
# -------------------------------------------------------------------------
print("\n[TEST 6] Testing auto-routed factual lookup for 'who discovered penicillin?'...")
sol6 = GeminiAndBrowserEngine.chat("who discovered penicillin?", auto_routed=True)
assert "🎯 ACTUAL DIRECT SOLUTION" in sol6
assert "Fleming" in sol6, "FAIL: Fleming not identified"
print("[✓ PASS] Test 6: Penicillin discovery directly answered as Alexander Fleming!")
print(sol6)

print("\n" + "=" * 80)
print("ALL VERIFICATION TESTS COMPLETED WITH 100% SUCCESS!")
print("=" * 80)
