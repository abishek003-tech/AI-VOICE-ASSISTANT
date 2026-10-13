import ast
import logging
import math
import operator
import re
from typing import Tuple, Optional
import config
from assistant.actions import ActionResult

logger = logging.getLogger("ai_assistant.calculator")

_WORD_NUMBERS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000
}

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _words_to_number_string(text: str) -> str:
    """Replace spoken English number words with digits."""
    tokens = text.lower().split()
    output_tokens = []
    i = 0
    while i < len(tokens):
        w = tokens[i]
        if w in _WORD_NUMBERS:
            val = _WORD_NUMBERS[w]
            # Check for compounds like "twenty five" or "eighty one"
            if i + 1 < len(tokens) and tokens[i + 1] in _WORD_NUMBERS:
                next_val = _WORD_NUMBERS[tokens[i + 1]]
                if val in [20, 30, 40, 50, 60, 70, 80, 90] and next_val < 10:
                    val += next_val
                    i += 1
                elif next_val == 100:
                    val *= 100
                    i += 1
            output_tokens.append(str(val))
        else:
            output_tokens.append(w)
        i += 1
    return " ".join(output_tokens)

def _safe_ast_eval(node):
    """Safely evaluate an AST expression without arbitrary code execution."""
    if isinstance(node, ast.Expression):
        return _safe_ast_eval(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        left = _safe_ast_eval(node.left)
        right = _safe_ast_eval(node.right)
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type}")
        if op_type == ast.Div and right == 0:
            raise ZeroDivisionError("division by zero")
        return _SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_ast_eval(node.operand)
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return _SAFE_OPERATORS[op_type](operand)
    raise ValueError(f"Unsupported AST node: {type(node)}")

def solve_math_expression(raw_query: str) -> ActionResult:
    """
    Safely parse and evaluate spoken mathematical expressions.
    Returns structured ActionResult with natural spoken answer.
    """
    clean = raw_query.lower().strip()
    
    # Remove filler words
    for prefix in [
        "calculator", "calculate", "what is the answer to", "what is the answer for",
        "what is the answer", "what is", "how much is", "solve", "please"
    ]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):].strip()

    # Clean punctuation and trailing filler
    clean = re.sub(r"[?,!\.]", "", clean)
    clean = re.sub(r"\b(what is the answer|answer)\b", "", clean).strip()

    # Special case: Square root
    sqrt_match = re.search(r"(?:square\s*root|sqrt|root)\s*(?:of)?\s*([0-9a-z\s]+)", clean)
    if sqrt_match:
        target_str = _words_to_number_string(sqrt_match.group(1).strip())
        digits_only = re.search(r"[-+]?\d*\.?\d+", target_str)
        if digits_only:
            try:
                num = float(digits_only.group(0))
                if num < 0:
                    return ActionResult(
                        success=False,
                        message="Cannot calculate the square root of a negative number.",
                        detail="Negative sqrt"
                    )
                ans = math.sqrt(num)
                ans_str = str(int(ans)) if ans.is_integer() else f"{ans:.2f}"
                num_display = str(int(num)) if num.is_integer() else str(num)
                msg = f"The square root of {num_display} is {ans_str}."
                return ActionResult(success=True, message=msg, detail=f"sqrt({num})={ans}")
            except Exception as e:
                return ActionResult(success=False, message="Error calculating square root.", detail=str(e))

    # Convert spoken number words to digits
    normalized = _words_to_number_string(clean)

    # Standardize spoken verbal math operators
    replacements = [
        (r"\bplus\b|\badded to\b", "+"),
        (r"\bminus\b|\bsubtracted by\b", "-"),
        (r"\bmultiplied by\b|\btimes\b|\binto\b|\bx\b", "*"),
        (r"\bdivided by\b|\bover\b", "/"),
        (r"\bto the power of\b|\bpower\b", "**"),
        (r"\bmodulo\b|\bmod\b", "%"),
    ]
    for pattern, symbol in replacements:
        normalized = re.sub(pattern, symbol, normalized)

    # Strip any remaining non-math characters
    math_expr = re.sub(r"[^0-9\+\-\*\/\.\(\)\s]", "", normalized).strip()

    if not math_expr or not any(c.isdigit() for c in math_expr):
        return ActionResult(
            success=False,
            message="Sorry, I couldn't understand that mathematical expression.",
            detail=f"Failed to extract math expression from '{raw_query}'"
        )

    try:
        tree = ast.parse(math_expr, mode="eval")
        result = _safe_ast_eval(tree)
        
        # Format the result cleanly
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 4)

        # Build natural spoken description of the equation
        spoken_expr = clean
        # If the original query had clear spoken words like "2 plus 3"
        readable_eq = math_expr.replace("*", " times ").replace("/", " divided by ").replace("+", " plus ").replace("-", " minus ")
        readable_eq = re.sub(r"\s+", " ", readable_eq).strip()

        if config.RESPONSE_MODE == "tanglish":
            msg = f"{readable_eq} equals {result}."
        else:
            msg = f"{readable_eq} equals {result}."

        logger.info(f"Math calculation succeeded: {math_expr} = {result}")
        return ActionResult(success=True, message=msg, detail=f"{math_expr}={result}")

    except ZeroDivisionError:
        logger.warning(f"Math division by zero in expression: {math_expr}")
        return ActionResult(
            success=False,
            message="Division by zero is not defined.",
            detail="ZeroDivisionError"
        )
    except Exception as e:
        logger.warning(f"Math AST evaluation failed for '{math_expr}': {e}")
        return ActionResult(
            success=False,
            message="Sorry, I couldn't calculate that mathematical expression.",
            detail=str(e)
        )
