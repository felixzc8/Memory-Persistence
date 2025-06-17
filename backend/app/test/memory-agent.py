from openai import OpenAI
from mem0 import Memory
from app.config import OPENAI_API_KEY, DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, MODEL_CHOICE

config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": MODEL_CHOICE,
        }
    },
    "vector_store": {
        "provider": "supabase",
        "config": {
            "connection_string": DATABASE_URL,
            "collection_name": "memories"
        }
    }
}

openai_client = OpenAI()
memory = Memory.from_config(config)

def chat_with_memory(message: str, user_id: str = "default_user") -> str:
    relevant_memories = memory.search(query=message, user_id=user_id, limit=3)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
    
    system_promt = f"You are a helpful assistant. Answer the question based on the query and memories.\nUser memories:\n{memories_str}"
    messages = [{"role": "system", "content": system_promt}, {"role": "user", "content": message}]
    response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    assistant_response = response.choices[0].message.content
    
    messages.append({"role": "assistant", "content": assistant_response})
    memory.add(messages, user_id=user_id)
    
    return assistant_response

def main():
    print("chat with homi")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        print(f"Assistant: {chat_with_memory(user_input)}")

if __name__ == "__main__":
    main()