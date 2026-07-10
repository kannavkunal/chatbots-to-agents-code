#!/usr/bin/env python3
"""
Output Guardrails: Checking What the Agent Says
Validates agent output before it reaches users or other systems.
"""
import re
import json
from typing import Any


def check_grounding(response: str, sources: list[str]) -> dict:
    """
    Verify that claims in the response are grounded in the provided sources.

    Returns:
        {
            'grounded': bool,
            'citations_found': int,
            'citations_verified': int,
            'unverified_claims': list[str]
        }
    """
    # Find all citations in the response (URLs or source references)
    # Exclude trailing punctuation like commas and periods
    url_pattern = r'https?://[^\s),.]+'
    cited_urls = re.findall(url_pattern, response)

    verified = 0
    unverified = []

    for url in cited_urls:
        # Check if URL appears in any source
        if any(url in source for source in sources):
            verified += 1
        else:
            unverified.append(url)

    return {
        'grounded': len(unverified) == 0,
        'citations_found': len(cited_urls),
        'citations_verified': verified,
        'unverified_claims': unverified
    }


def validate_schema(output: Any, expected_type: str) -> dict:
    """
    Validate that output matches the expected schema.

    Args:
        output: The output to validate
        expected_type: 'json', 'sql', 'python', etc.

    Returns:
        {'valid': bool, 'error': str or None}
    """
    try:
        if expected_type == 'json':
            json.loads(output) if isinstance(output, str) else output
            return {'valid': True, 'error': None}

        elif expected_type == 'sql':
            # Simple SQL validation (real version would use sqlparse)
            forbidden = ['drop', 'delete', 'truncate', 'alter']
            lower = output.lower()
            for word in forbidden:
                if word in lower:
                    return {'valid': False, 'error': f'Forbidden keyword: {word}'}
            return {'valid': True, 'error': None}

        elif expected_type == 'python':
            # Attempt to parse as Python
            compile(output, '<string>', 'exec')
            return {'valid': True, 'error': None}

        else:
            return {'valid': False, 'error': f'Unknown type: {expected_type}'}

    except json.JSONDecodeError as e:
        return {'valid': False, 'error': f'Invalid JSON: {str(e)}'}
    except SyntaxError as e:
        return {'valid': False, 'error': f'Syntax error: {str(e)}'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}


def check_toxicity(text: str) -> dict:
    """
    Simple content policy check (real version would use a proper classifier).

    Returns:
        {'safe': bool, 'issues': list[str]}
    """
    # Simplified: check for obvious problematic content
    # In production, use Google's Perspective API or similar
    forbidden_patterns = [
        (r'\b(hack|crack|exploit)\s+into\b', 'unauthorized_access'),
        (r'\b(steal|theft)\b', 'illegal_activity'),
        (r'\b(kill|murder|harm)\b', 'violence'),
    ]

    issues = []
    for pattern, issue_type in forbidden_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(issue_type)

    return {
        'safe': len(issues) == 0,
        'issues': issues
    }


def apply_output_guardrails(
    response: str,
    sources: list[str] = None,
    expected_type: str = None
) -> dict:
    """
    Apply all output guardrails before returning response to user.

    Returns:
        {
            'safe_to_return': bool,
            'grounding_check': dict,
            'schema_check': dict,
            'toxicity_check': dict,
            'issues': list[str]
        }
    """
    results = {
        'safe_to_return': True,
        'grounding_check': None,
        'schema_check': None,
        'toxicity_check': None,
        'issues': []
    }

    # Check 1: Grounding (if sources provided)
    if sources:
        grounding = check_grounding(response, sources)
        results['grounding_check'] = grounding
        if not grounding['grounded']:
            results['safe_to_return'] = False
            results['issues'].append('ungrounded_claims')

    # Check 2: Schema validation (if type specified)
    if expected_type:
        schema = validate_schema(response, expected_type)
        results['schema_check'] = schema
        if not schema['valid']:
            results['safe_to_return'] = False
            results['issues'].append('invalid_schema')

    # Check 3: Toxicity/policy
    toxicity = check_toxicity(response)
    results['toxicity_check'] = toxicity
    if not toxicity['safe']:
        results['safe_to_return'] = False
        results['issues'].append('policy_violation')

    return results


# ============================================================
# Demo
# ============================================================

if __name__ == "__main__":
    print("Output Guardrails Demo")
    print("=" * 60)

    # Example 1: Good response with grounding
    print("\n1. Well-grounded response:")
    response1 = "According to https://example.com/data, the value is 42."
    sources1 = ["Retrieved from https://example.com/data: value=42"]
    result = apply_output_guardrails(response1, sources=sources1)
    print(f"Safe to return: {result['safe_to_return']}")
    print(f"Grounding: {result['grounding_check']}")

    # Example 2: Hallucinated URL
    print("\n2. Hallucinated citation:")
    response2 = "According to https://totally-fake-url.com/stats, the value is 99."
    sources2 = ["Retrieved from https://real-source.com: value=42"]
    result = apply_output_guardrails(response2, sources=sources2)
    print(f"Safe to return: {result['safe_to_return']}")
    print(f"Issues: {result['issues']}")
    print(f"Unverified: {result['grounding_check']['unverified_claims']}")

    # Example 3: Invalid JSON
    print("\n3. Invalid JSON schema:")
    response3 = '{"name": "John", "age": invalid}'
    result = apply_output_guardrails(response3, expected_type='json')
    print(f"Safe to return: {result['safe_to_return']}")
    print(f"Schema error: {result['schema_check']['error']}")

    # Example 4: Policy violation
    print("\n4. Policy violation:")
    response4 = "Here's how to hack into the system..."
    result = apply_output_guardrails(response4)
    print(f"Safe to return: {result['safe_to_return']}")
    print(f"Issues: {result['toxicity_check']['issues']}")

    # Example 5: Clean output
    print("\n5. Clean, valid output:")
    response5 = '{"status": "success", "value": 42}'
    result = apply_output_guardrails(response5, expected_type='json')
    print(f"Safe to return: {result['safe_to_return']}")
    print("✓ All checks passed")

    print("\n" + "=" * 60)
    print("Key Takeaway: Catch the 1-in-500 disaster before it ships.")
