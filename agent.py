from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tools import (
    calculator, say_hello, get_time, get_date, coin_flip, dice_roll,
    random_number, unit_converter, word_counter, password_generator,
    reminder_format, json_formatter, get_tool_list
)
import logging
import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize model
model = ChatOllama(model="phi3:mini", temperature=0.7)

# Conversation memory storage (in-memory)
# For production, use Redis or a database
conversation_history: Dict[str, List] = defaultdict(list)
conversation_metadata: Dict[str, Dict] = defaultdict(dict)

# Maximum messages to keep in memory per session
MAX_HISTORY_LENGTH = 30

def get_system_message() -> SystemMessage:
    """Get the system message with AI instructions."""
    return SystemMessage(content="""You are a helpful AI assistant with conversation memory and powerful tools.
You remember the context of our conversation and can reference previous messages.

When users ask questions, use the conversation history to provide contextual, relevant responses.
You have access to many tools - use them when appropriate to help users effectively.

Be friendly, helpful, and concise in your responses.""")

def parse_command(text: str) -> Tuple[str, str]:
    """
    Parse user input into command and arguments.
    
    Args:
        text: User input string
        
    Returns:
        Tuple of (command, arguments)
    """
    text = text.strip()
    parts = text.split(maxsplit=1)
    
    if not parts:
        return "", ""
    
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    return command, args

def handle_calculator(args: str) -> Optional[str]:
    """
    Handle calculator commands with various operations.
    
    Args:
        args: Arguments containing the calculation
        
    Returns:
        Calculation result or error message
    """
    patterns = [
        (r'(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)', 'add'),
        (r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', 'subtract'),
        (r'(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)', 'multiply'),
        (r'(\d+\.?\d*)\s*/\s*(\d+\.?\d*)', 'divide'),
        (r'(\d+\.?\d*)\s*\^\s*(\d+\.?\d*)', 'power'),
        (r'(\d+\.?\d*)\s*%\s*(\d+\.?\d*)', 'modulo'),
    ]
    
    for pattern, operation in patterns:
        match = re.search(pattern, args)
        if match:
            a, b = float(match.group(1)), float(match.group(2))
            return calculator(a, b, operation)
    
    return "Format: calc [num1] [+/-/*/÷/^/%] [num2]"

def handle_dice(args: str) -> str:
    """
    Handle dice roll commands.
    
    Args:
        args: Arguments for dice (sides and/or count)
        
    Returns:
        Dice roll result
    """
    if not args:
        return dice_roll()
    
    parts = args.split()
    try:
        if len(parts) == 1:
            return dice_roll(int(parts[0]))
        elif len(parts) == 2:
            return dice_roll(int(parts[0]), int(parts[1]))
        else:
            return "Format: dice [sides] [count]"
    except ValueError:
        return "Please provide valid numbers"

def handle_random(args: str) -> str:
    """
    Handle random number generation.
    
    Args:
        args: Min and max values
        
    Returns:
        Random number result
    """
    if not args:
        return random_number()
    
    parts = args.split()
    try:
        if len(parts) == 2:
            return random_number(int(parts[0]), int(parts[1]))
        else:
            return "Format: random [min] [max]"
    except ValueError:
        return "Please provide valid numbers"

def handle_date(args: str) -> str:
    """
    Handle date commands with optional offset.
    
    Args:
        args: Day offset (optional)
        
    Returns:
        Date string
    """
    if not args:
        return get_date()
    
    try:
        offset = int(args)
        return get_date(offset)
    except ValueError:
        return "Format: date [offset_days]"

def handle_convert(args: str) -> str:
    """
    Handle unit conversion.
    
    Args:
        args: Value, from_unit, to_unit
        
    Returns:
        Conversion result
    """
    parts = args.split()
    if len(parts) != 3:
        return "Format: convert [value] [from_unit] [to_unit]"
    
    try:
        value = float(parts[0])
        from_unit = parts[1]
        to_unit = parts[2]
        return unit_converter(value, from_unit, to_unit)
    except ValueError:
        return "Please provide a valid number for the value"

def handle_password(args: str) -> str:
    """
    Handle password generation.
    
    Args:
        args: Password length (optional)
        
    Returns:
        Generated password
    """
    if not args:
        return password_generator()
    
    try:
        length = int(args)
        return password_generator(length)
    except ValueError:
        return "Format: password [length]"

def add_to_history(session_id: str, role: str, content: str):
    """
    Add a message to conversation history.
    
    Args:
        session_id: Unique session identifier
        role: Message role (user, assistant, system)
        content: Message content
    """
    timestamp = datetime.now()
    
    # Create appropriate message type
    if role == "user":
        message = HumanMessage(content=content)
    elif role == "assistant":
        message = AIMessage(content=content)
    else:
        message = SystemMessage(content=content)
    
    conversation_history[session_id].append(message)
    
    # Update metadata
    if 'message_count' not in conversation_metadata[session_id]:
        conversation_metadata[session_id]['message_count'] = 0
        conversation_metadata[session_id]['started_at'] = timestamp
    
    conversation_metadata[session_id]['message_count'] += 1
    conversation_metadata[session_id]['last_activity'] = timestamp
    
    # Trim history if too long (keep most recent messages)
    if len(conversation_history[session_id]) > MAX_HISTORY_LENGTH:
        has_system = isinstance(conversation_history[session_id][0], SystemMessage)
        if has_system:
            # Keep system message + recent messages
            conversation_history[session_id] = [conversation_history[session_id][0]] + \
                                               conversation_history[session_id][-(MAX_HISTORY_LENGTH-1):]
        else:
            # Keep only recent messages
            conversation_history[session_id] = conversation_history[session_id][-MAX_HISTORY_LENGTH:]

def get_conversation_summary(session_id: str) -> str:
    """
    Get a summary of the conversation statistics.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Formatted summary string
    """
    metadata = conversation_metadata.get(session_id, {})
    history = conversation_history.get(session_id, [])
    
    if not metadata:
        return "No conversation history"
    
    msg_count = metadata.get('message_count', 0)
    started = metadata.get('started_at')
    
    # Calculate duration
    if started:
        duration = datetime.now() - started
        minutes = int(duration.total_seconds() / 60)
        time_str = f"{minutes} minute(s)" if minutes > 0 else "less than a minute"
    else:
        time_str = "unknown"
    
    # Count message types
    user_msgs = sum(1 for msg in history if isinstance(msg, HumanMessage))
    ai_msgs = sum(1 for msg in history if isinstance(msg, AIMessage))
    
    return f"""💬 Conversation Summary:
• Total messages: {msg_count}
• Your messages: {user_msgs}
• My responses: {ai_msgs}
• Duration: {time_str}
• Memory: {len(history)} messages stored"""

def clear_conversation(session_id: str):
    """
    Clear conversation history for a session.
    
    Args:
        session_id: Session identifier to clear
    """
    if session_id in conversation_history:
        del conversation_history[session_id]
    if session_id in conversation_metadata:
        del conversation_metadata[session_id]
    logger.info(f"Cleared history for session: {session_id}")

def run_agent(user_input: str, session_id: str) -> str:
    """
    Process user input with conversation memory and tools.
    
    This is the main entry point for processing user messages.
    It routes commands to appropriate tools or uses the LLM for general conversation.
    
    Args:
        user_input: User's message
        session_id: Session identifier for memory tracking
    
    Returns:
        Response string
    """
    try:
        # Add user message to history
        add_to_history(session_id, "user", user_input)
        
        # Parse command
        command, args = parse_command(user_input)
        
        # Tool routing dictionary
        tools = {
            # Calculator
            "calc": lambda: handle_calculator(args),
            "calculate": lambda: handle_calculator(args),
            
            # Greetings
            "hello": lambda: say_hello(args) if args else "Please provide a name",
            "hi": lambda: say_hello(args) if args else "Please provide a name",
            
            # Time & Date
            "time": lambda: get_time(args if args else "local"),
            "date": lambda: handle_date(args),
            
            # Random
            "coin": lambda: coin_flip(),
            "flip": lambda: coin_flip(),
            "dice": lambda: handle_dice(args),
            "roll": lambda: handle_dice(args),
            "random": lambda: handle_random(args),
            
            # Utilities
            "convert": lambda: handle_convert(args),
            "count": lambda: word_counter(args) if args else "Provide text to count",
            "password": lambda: handle_password(args),
            "pwd": lambda: handle_password(args),
            "json": lambda: json_formatter(args) if args else "Provide JSON to format",
            "reminder": lambda: reminder_format(args) if args else "Specify a task",
            
            # Help & Info
            "help": lambda: get_tool_list(),
            "tools": lambda: get_tool_list(),
            "summary": lambda: get_conversation_summary(session_id),
            "stats": lambda: get_conversation_summary(session_id),
        }
        
        # Check if it's a tool command
        if command in tools:
            response = tools[command]()
            add_to_history(session_id, "assistant", response)
            return response
        
        # Use LLM with conversation history
        history = conversation_history.get(session_id, [])
        
        # Ensure system message is first
        if not history or not isinstance(history[0], SystemMessage):
            history = [get_system_message()] + history
        
        logger.info(f"Processing with LLM (history: {len(history)} messages)")
        
        # Invoke the model with full conversation context
        response = model.invoke(history)
        
        response_text = response.content
        add_to_history(session_id, "assistant", response_text)
        
        return response_text
    
    except Exception as e:
        logger.error(f"Error in run_agent: {str(e)}", exc_info=True)
        error_msg = "I encountered an error processing your request. Please try again."
        add_to_history(session_id, "assistant", error_msg)
        return error_msg