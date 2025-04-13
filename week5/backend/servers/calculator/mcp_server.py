# basic import 
from mcp.server.fastmcp import FastMCP
import math

# instantiate an MCP server client
mcp = FastMCP("Calculator") 

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The sum of the two numbers.
    """
    return int(a + b)

@mcp.tool()
def add_list(l: list[int]) -> int:
    """
    Add all numbers in a list.

    Args:
        l (list[int]): A list of integers.

    Returns:
        int: The sum of all numbers in the list.
    """
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """
    Subtract two numbers.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The result of subtracting the second number from the first.
    """
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The product of the two numbers.
    """
    return int(a * b)

# division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """
    Divide two numbers.

    Args:
        a (int): The numerator.
        b (int): The denominator.

    Returns:
        float: The result of dividing the numerator by the denominator.
    """
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """
    Calculate the power of a number raised to another.

    Args:
        a (int): The base number.
        b (int): The exponent.

    Returns:
        int: The result of raising the base to the exponent.
    """
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """
    Calculate the square root of a number.

    Args:
        a (int): The number.

    Returns:
        float: The square root of the number.
    """
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """
    Calculate the cube root of a number.

    Args:
        a (int): The number.

    Returns:
        float: The cube root of the number.
    """
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """
    Calculate the factorial of a number.

    Args:
        a (int): The number.

    Returns:
        int: The factorial of the number.
    """
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """
    Calculate the natural logarithm of a number.

    Args:
        a (int): The number.

    Returns:
        float: The natural logarithm of the number.
    """
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """
    Calculate the remainder of the division of two numbers.

    Args:
        a (int): The dividend.
        b (int): The divisor.

    Returns:
        int: The remainder of the division.
    """
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """
    Calculate the sine of a number (in radians).

    Args:
        a (int): The angle in radians.

    Returns:
        float: The sine of the angle.
    """
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """
    Calculate the cosine of a number (in radians).

    Args:
        a (int): The angle in radians.

    Returns:
        float: The cosine of the angle.
    """
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """
    Calculate the tangent of a number (in radians).

    Args:
        a (int): The angle in radians.

    Returns:
        float: The tangent of the angle.
    """
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """
    Perform a special mining operation.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The result of the operation (a - b - b).
    """
    return int(a - b - b)

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """
    Convert a string to a list of ASCII values of its characters.

    Args:
        string (str): The input string.

    Returns:
        list[int]: A list of ASCII values of the characters in the string.
    """
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list[int]) -> float:
    """
    Calculate the sum of exponentials of numbers in a list.

    Args:
        int_list (list[int]): A list of integers.

    Returns:
        float: The sum of the exponentials of the numbers in the list.
    """
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list[int]:
    """
    Generate the first n Fibonacci numbers.

    Args:
        n (int): The number of Fibonacci numbers to generate.

    Returns:
        list[int]: A list of the first n Fibonacci numbers.
    """
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


if __name__ == "__main__":
    # run the server
    mcp.run()