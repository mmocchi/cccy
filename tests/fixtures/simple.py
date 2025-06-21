"""Simple test fixture for complexity analysis."""


def simple_function() -> str:
    """A simple function with minimal complexity."""
    return "hello"


def function_with_if(x: int) -> str:
    """Function with an if statement."""
    if x > 0:
        return "positive"
    return "negative"


def complex_function(a: int, b: int, c: int) -> float:
    """Function with higher complexity."""
    result = 0.0

    if a > 0:
        result = (a + b + c if c > 0 else a + b) if b > 0 else a
    elif b > 0:
        result = b
    else:
        result = 0

    for i in range(10):
        if i % 2 == 0:
            result += i
        else:
            result -= i

    try:
        result = result / a
    except ZeroDivisionError:
        result = 0.0

    return result


async def async_function() -> str:
    """An async function."""
    return await some_async_operation_async()


async def some_async_operation_async() -> str:
    """Mock async operation."""
    return "async_result"


class TestClass:
    """Test class with methods."""

    def method_one(self) -> int:
        """Simple method."""
        return 1

    def method_with_loops(self) -> list[int]:
        """Method with nested loops."""
        result = []
        for i in range(5):
            for j in range(5):
                if i == j:
                    result.append(i)
        return result
