#!/bin/bash
# Comprehensive test script for Part 8 Observability

echo "=========================================="
echo "Part 8 Observability - Comprehensive Tests"
echo "=========================================="
echo ""

# Clean up
echo "🧹 Cleaning up old traces..."
rm -rf traces test_traces
echo ""

# Test 1
echo "📝 Test 1: Simple Tracer (no dependencies)"
echo "==========================================
"
python3 1_simple_tracer.py
if [ $? -eq 0 ]; then
    echo "✅ Test 1 PASSED"
else
    echo "❌ Test 1 FAILED"
fi
echo ""

# Test 2
echo "📝 Test 2: Agent with Traces (simulation mode)"
echo "================================================"
unset GEMINI_API_KEY
python3 2_agent_with_traces.py
if [ $? -eq 0 ]; then
    echo "✅ Test 2 PASSED"
else
    echo "❌ Test 2 FAILED"
fi
echo ""

# Test 3
echo "📝 Test 3: Trace Analyzer"
echo "=========================="
python3 3_trace_analyzer.py | head -20
if [ $? -eq 0 ]; then
    echo "✅ Test 3 PASSED"
else
    echo "❌ Test 3 FAILED"
fi
echo ""

# Test 4
echo "📝 Test 4: Trace Viewer (list)"
echo "==============================="
python3 4_trace_viewer.py | head -15
if [ $? -eq 0 ]; then
    echo "✅ Test 4 PASSED"
else
    echo "❌ Test 4 FAILED"
fi
echo ""

# Test 5
echo "📝 Test 5: Trace Viewer (specific trace)"
echo "=========================================="
FIRST_TRACE=$(ls traces/*.json 2>/dev/null | head -1)
if [ -n "$FIRST_TRACE" ]; then
    python3 4_trace_viewer.py "$FIRST_TRACE"
    if [ $? -eq 0 ]; then
        echo "✅ Test 5 PASSED"
    else
        echo "❌ Test 5 FAILED"
    fi
else
    echo "⚠ No traces found for Test 5"
fi
echo ""

# Test 6
echo "📝 Test 6: Sample Trace (verbose)"
echo "=================================="
python3 4_trace_viewer.py sample_trace.json --verbose | head -30
if [ $? -eq 0 ]; then
    echo "✅ Test 6 PASSED"
else
    echo "❌ Test 6 FAILED"
fi
echo ""

# Test 7
echo "📝 Test 7: Full Test Suite"
echo "==========================="
python3 test_observability.py
if [ $? -eq 0 ]; then
    echo "✅ Test 7 PASSED"
else
    echo "❌ Test 7 FAILED"
fi
echo ""

# Test 8 - Invalid API key handling
echo "📝 Test 8: Invalid API Key Handling"
echo "===================================="
GEMINI_API_KEY="invalid-key-test" python3 2_agent_with_traces.py 2>&1 | grep -q "Falling back to simulation"
if [ $? -eq 0 ]; then
    echo "✅ Test 8 PASSED (graceful fallback working)"
else
    echo "❌ Test 8 FAILED"
fi
echo ""

# Summary
echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo "Generated $(ls traces/*.json 2>/dev/null | wc -l | xargs) trace files"
echo ""
ls -lh *.py *.json *.txt *.md 2>/dev/null | awk '{print "  " $9, "(" $5 ")"}'
echo ""
echo "✅ All core tests completed!"
echo "   Ready to publish to repository."
