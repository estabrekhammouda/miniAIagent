from typing import Union, List, Dict
from datetime import datetime, timedelta
import random
import json
import re

def calculator(a: float, b: float, operation: str = "add") -> str:
    """
    Perform mathematical operations on two numbers.
    
    Args:
        a: First number
        b: Second number
        operation: Type of operation (add, subtract, multiply, divide, power, modulo)
    
    Returns:
        Result string
    """
    try:
        operations = {
            "add": (lambda x, y: x + y, f"{a} + {b}"),
            "subtract": (lambda x, y: x - y, f"{a} - {b}"),
            "multiply": (lambda x, y: x * y, f"{a} × {b}"),
            "divide": (lambda x, y: x / y if y != 0 else None, f"{a} ÷ {b}"),
            "power": (lambda x, y: x ** y, f"{a} ^ {b}"),
            "modulo": (lambda x, y: x % y if y != 0 else None, f"{a} mod {b}")
        }
        
        if operation not in operations:
            return f"Unknown operation: {operation}. Available: add, subtract, multiply, divide, power, modulo"
        
        func, expr = operations[operation]
        result = func(a, b)
        
        if result is None:
            return "Error: Cannot divide by zero"
        
        return f"{expr} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

def say_hello(name: str) -> str:
    """Generate a friendly greeting."""
    if not name or len(name.strip()) == 0:
        return "Hello! Please provide a name."
    
    name = name.strip()[:50]
    greetings = [
        f"Hello {name}, nice to meet you! 👋",
        f"Hi {name}! How can I help you today?",
        f"Greetings {name}! Welcome!",
        f"Hey {name}! Great to see you here! 😊"
    ]
    return random.choice(greetings)

def get_time(timezone: str = "local") -> str:
    """
    Get current time and date.
    
    Args:
        timezone: Timezone (local, utc)
    
    Returns:
        Formatted time string
    """
    try:
        now = datetime.now()
        
        if timezone.lower() == "utc":
            now = datetime.utcnow()
            tz_label = "UTC"
        else:
            tz_label = "Local"
        
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%A, %B %d, %Y")
        
        return f"🕐 {tz_label} Time: {time_str}\n📅 Date: {date_str}"
    except Exception as e:
        return f"Error getting time: {str(e)}"

def get_date(days_offset: int = 0) -> str:
    """
    Get date with optional offset.
    
    Args:
        days_offset: Number of days to add/subtract from today
    
    Returns:
        Formatted date string
    """
    try:
        target_date = datetime.now() + timedelta(days=days_offset)
        date_str = target_date.strftime("%A, %B %d, %Y")
        
        if days_offset == 0:
            return f"📅 Today: {date_str}"
        elif days_offset == 1:
            return f"📅 Tomorrow: {date_str}"
        elif days_offset == -1:
            return f"📅 Yesterday: {date_str}"
        elif days_offset > 0:
            return f"📅 {days_offset} days from now: {date_str}"
        else:
            return f"📅 {abs(days_offset)} days ago: {date_str}"
    except Exception as e:
        return f"Error getting date: {str(e)}"

def coin_flip() -> str:
    """Flip a coin."""
    result = random.choice(["Heads", "Tails"])
    emoji = "🪙"
    return f"{emoji} Coin flip result: **{result}**"

def dice_roll(sides: int = 6, count: int = 1) -> str:
    """
    Roll dice.
    
    Args:
        sides: Number of sides on the die
        count: Number of dice to roll
    
    Returns:
        Roll results
    """
    try:
        if sides < 2 or sides > 100:
            return "Dice must have between 2 and 100 sides"
        if count < 1 or count > 10:
            return "Can roll between 1 and 10 dice at once"
        
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        
        if count == 1:
            return f"🎲 Rolled 1d{sides}: **{rolls[0]}**"
        else:
            rolls_str = ", ".join(map(str, rolls))
            return f"🎲 Rolled {count}d{sides}: [{rolls_str}] = **{total}**"
    except Exception as e:
        return f"Error rolling dice: {str(e)}"

def random_number(min_val: int = 1, max_val: int = 100) -> str:
    """
    Generate a random number.
    
    Args:
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Random number string
    """
    try:
        if min_val >= max_val:
            return "Minimum must be less than maximum"
        
        num = random.randint(min_val, max_val)
        return f"🎲 Random number between {min_val} and {max_val}: **{num}**"
    except Exception as e:
        return f"Error generating random number: {str(e)}"

def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert between units.
    
    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit
    
    Returns:
        Conversion result
    """
    try:
        # Length conversions (to meters)
        length_units = {
            "m": 1, "meter": 1, "meters": 1,
            "km": 1000, "kilometer": 1000, "kilometers": 1000,
            "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
            "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
            "mi": 1609.34, "mile": 1609.34, "miles": 1609.34,
            "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
            "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
            "yd": 0.9144, "yard": 0.9144, "yards": 0.9144
        }
        
        # Temperature conversions
        if from_unit.lower() in ["c", "celsius"] and to_unit.lower() in ["f", "fahrenheit"]:
            result = (value * 9/5) + 32
            return f"🌡️ {value}°C = {result:.2f}°F"
        elif from_unit.lower() in ["f", "fahrenheit"] and to_unit.lower() in ["c", "celsius"]:
            result = (value - 32) * 5/9
            return f"🌡️ {value}°F = {result:.2f}°C"
        elif from_unit.lower() in ["c", "celsius"] and to_unit.lower() in ["k", "kelvin"]:
            result = value + 273.15
            return f"🌡️ {value}°C = {result:.2f}K"
        elif from_unit.lower() in ["k", "kelvin"] and to_unit.lower() in ["c", "celsius"]:
            result = value - 273.15
            return f"🌡️ {value}K = {result:.2f}°C"
        
        # Length conversions
        from_unit_lower = from_unit.lower()
        to_unit_lower = to_unit.lower()
        
        if from_unit_lower in length_units and to_unit_lower in length_units:
            meters = value * length_units[from_unit_lower]
            result = meters / length_units[to_unit_lower]
            return f"📏 {value} {from_unit} = {result:.4f} {to_unit}"
        
        return f"Conversion from {from_unit} to {to_unit} not supported yet"
    except Exception as e:
        return f"Conversion error: {str(e)}"

def word_counter(text: str) -> str:
    """
    Count words, characters, and lines in text.
    
    Args:
        text: Text to analyze
    
    Returns:
        Statistics string
    """
    try:
        if not text:
            return "Please provide text to analyze"
        
        words = len(text.split())
        chars = len(text)
        chars_no_spaces = len(text.replace(" ", ""))
        lines = len(text.split("\n"))
        sentences = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        
        return f"""📊 Text Statistics:
• Words: {words}
• Characters: {chars} (with spaces), {chars_no_spaces} (without spaces)
• Lines: {lines}
• Sentences: {sentences}"""
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

def password_generator(length: int = 12, include_symbols: bool = True) -> str:
    """
    Generate a random password.
    
    Args:
        length: Password length (8-32)
        include_symbols: Include special characters
    
    Returns:
        Generated password
    """
    try:
        import string
        
        if length < 8 or length > 32:
            return "Password length must be between 8 and 32 characters"
        
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        return f"🔐 Generated password: `{password}`\n⚠️ Make sure to save this securely!"
    except Exception as e:
        return f"Error generating password: {str(e)}"

def reminder_format(task: str, time_str: str = "") -> str:
    """
    Format a reminder (simulated - no actual scheduling).
    
    Args:
        task: Task to remember
        time_str: Time description
    
    Returns:
        Formatted reminder
    """
    if not task:
        return "Please specify a task for the reminder"
    
    if time_str:
        return f"⏰ Reminder set: '{task}' {time_str}\n(Note: This is a simulated reminder)"
    else:
        return f"⏰ Reminder noted: '{task}'\n(Note: This is a simulated reminder)"

def json_formatter(json_str: str) -> str:
    """
    Format and validate JSON.
    
    Args:
        json_str: JSON string to format
    
    Returns:
        Formatted JSON or error message
    """
    try:
        parsed = json.loads(json_str)
        formatted = json.dumps(parsed, indent=2)
        return f"✅ Valid JSON:\n```json\n{formatted}\n```"
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON: {str(e)}"

def get_tool_list() -> str:
    """Return a formatted list of all available tools."""
    return """🛠️ Available Tools:

**Math & Numbers:**
• calc [num1] [+/-/*/÷/^/%] [num2] - Calculate
• random [min] [max] - Random number
• dice [sides] [count] - Roll dice
• coin - Flip a coin

**Time & Date:**
• time - Current time
• date [offset] - Get date (±N days)

**Text & Data:**
• count [text] - Word/character counter
• json [data] - Format/validate JSON

**Utilities:**
• convert [value] [from] [to] - Unit converter
• password [length] - Generate password
• hello [name] - Greeting

**Help:**
• help - Show this message
• tools - List all tools"""