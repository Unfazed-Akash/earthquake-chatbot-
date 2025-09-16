# main.py
from modules.data_loader import load_dataframe, dataset_summary
from modules.chatbot import handle_query

def main():
    print("Loading dataset...")
    try:
        df = load_dataframe("data/earthquakes.csv")
    except Exception as e:
        print("❌ Failed to load dataset:", e)
        return

    print("✅ Loaded!\n")
    print(dataset_summary(df))
    print("\n🤖 Earthquake Chatbot — type a question, or 'help' for examples, 'exit' to quit.\n")

    while True:
        user = input("You: ").strip()
        if user.lower() in {"exit", "quit"}:
            print("Bot: Bye! 👋")
            break
        if user.lower() in {"help", "examples"}:
            print("Bot: try things like:\n"
                  "  - largest earthquake in Japan after 2015\n"
                  "  - count earthquakes with mag >= 6 in 2020\n"
                  "  - plot trend in Chile between 2000 and 2005\n"
                  "  - histogram of magnitude in Japan\n"
                  "  - earthquakes per year\n"
                  "  - sample\n")
            continue

        try:
            reply = handle_query(df, user)
        except Exception as e:
            reply = f"⚠️ Error while processing your query: {e}"
        print("Bot:", reply)

if __name__ == "__main__":
    main()
