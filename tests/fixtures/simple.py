"""Simple test fixture for complexity analysis."""


def simple_function():
    """A simple function with minimal complexity."""
    return "hello"


def function_with_if(x):
    """Function with an if statement."""
    if x > 0:
        return "positive"
    else:
        return "negative"


def complex_function(a, b, c):
    """Function with higher complexity."""
    result = 0

    if a > 0:
        if b > 0:
            if c > 0:
                result = a + b + c
            else:
                result = a + b
        else:
            result = a
    else:
        if b > 0:
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
        result = 0

    return result


async def async_function():
    """An async function."""
    return await some_async_operation()


def some_async_operation():
    """Mock async operation."""
    return "async_result"


class TestClass:
    """Test class with methods."""

    def method_one(self):
        """Simple method."""
        return 1

    def method_with_loops(self):
        """Method with nested loops."""
        result = []
        for i in range(5):
            for j in range(5):
                if i == j:
                    result.append(i)
        return result
