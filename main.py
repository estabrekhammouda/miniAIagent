# main.py
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# Tools as simple Python functions
def calculator(a: float, b: float) -> str:
    return f"The sum of {a} and {b} is {a + b}"

def say_hello(name: str) -> str:
    return f"Hello {name}, nice to meet you"

def main():
    # Local model
    model = ChatOllama(model="phi3:mini", temperature=0)

    print("🟢 Local AI Agent (phi3:mini) running — type 'quit' to exit")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        # Simple tool detection
        if user_input.lower().startswith("calc "):
            try:
                _, a, b = user_input.split()
                print(calculator(float(a), float(b)))
            except Exception as e:
                print(f"Error in calculation: {e}")
        elif user_input.lower().startswith("hello "):
            _, name = user_input.split(maxsplit=1)
            print(say_hello(name))
        else:
            # Correct way to get response from LangChain model
            response = model.invoke([HumanMessage(content=user_input)])
            print("Assistant:", response.content)

if __name__ == "__main__":
    main()