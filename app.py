!pip install -qU langchain-google-genai

import sqlite3
import webbrowser
import json

from urllib.parse import quote
from typing import TypedDict, Optional
from datetime import datetime

from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from google.colab import userdata
DB_NAME = "music_memory.db"

# ==========================================

# 1. LLM INITIALIZATION

# ==========================================

# Initialize your LLM here (e.g., ChatOpenAI, ChatGoogleGenerativeAI, etc.)

try:
    api_key = userdata.get("flowt-v1")
    print("API Key configured successfully.")

except userdata.SecretNotFoundError:
    raise ValueError("Gemini API key 'flowt-v1' not found in Colab Secrets.")

llm_flash = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    google_api_key=api_key
)
llm = llm_flash


# ==========================================

# 2. STATE DEFINITION

# ==========================================

class MusicState(TypedDict):
    user_input: str
    mood: Optional[str]
    energy: Optional[str]
    activity: Optional[str]
    desired_feeling: Optional[str]

    music_preferences: dict
    recommendation: Optional[dict]

    selected_song: Optional[str]
    selected_artist: Optional[str]
    feedback: Optional[str]
    session_active: bool
    session_id: Optional[str]

    current_genre: Optional[str]
    current_direction: Optional[str]

    change_requested: bool

    next_step: Optional[str]




# ==========================================

# 3. TOOLS

# ==========================================

@tool
def get_music_memory() -> str:
    """Retrieve the user's historical music preferences."""

    conn = sqlite3.connect(DB_NAME)

    rows = conn.execute("""
        SELECT song, artist, mood, activity, action
        FROM music_history
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()

    conn.close()

    if not rows:
        return "No listening history available yet."

    return "\n".join(
        f"Song: {song} | Artist: {artist} | "
        f"Mood: {mood} | Activity: {activity} | Action: {action}"
        for song, artist, mood, activity, action in rows
    )




def initialize_music_memory():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS music_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song TEXT,
            artist TEXT,
            mood TEXT,
            activity TEXT,
            action TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()
initialize_music_memory()

def music_player_node(state: MusicState):

    print("\n[Player] Preparing music...")

    recommendation = state["recommendation"]
    search_query = recommendation["search_query"]

    url = "https://www.youtube.com/results?search_query=" + quote(search_query)

    print(f"Search URL generated:")
    print(url)

    return {
        "selected_song": search_query,
        "selected_artist": None,
        "next_step": "feedback"
    }
def record_music_feedback(
    song: str,
    artist: str,
    mood: str,
    activity: str,
    action: str
):
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        INSERT INTO music_history
        (song, artist, mood, activity, action, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        song,
        artist,
        mood,
        activity,
        action,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()



# ==========================================

# 4. GRAPH NODES

# ==========================================

def user_input_node(state: MusicState):

    print("\n" + "=" * 50)
    print("--- MUSIC ASSISTANT ---")

    user_input = input(
    "Tell me your mood, activity, or what you need music for: ").strip()

    if user_input.lower() == "exit":
        return {"next_step": "exit"}

    return {
        "user_input": user_input,
        "next_step": "analyze"
    }

def feedback_node(state: MusicState):

    feedback = input(
        "\nFeedback [esc = change | exit = end | Enter = continue]: "
    ).strip().lower()

    if feedback == "":
        return {
            "feedback": None,
            "change_requested": False,
            "next_step": "player"
        }

    if feedback == "esc":
        return {
            "feedback": "change",
            "change_requested": True,
            "next_step": "recommend"
        }

    if feedback == "exit":
        return {
            "feedback": "exit",
            "change_requested": False,
            "next_step": "exit"
        }

    # Treat any other text as actual feedback.
    return {
        "feedback": feedback,
        "change_requested": False,
        "next_step": "player"
    }


def update_memory_node(state: MusicState):

    feedback = state.get("feedback", "continue")

    if feedback == "exit":
        print("[Session] Ending music session.")

        return {
            "session_active": False,
            "next_step": "exit"
        }

    if feedback == "change":
        print("[Session] User requested a new musical direction.")

        return {
            "change_requested": True,
            "next_step": "recommend"
        }

    # Normal feedback
    if feedback not in ["like", "okay", "continue"]:
        feedback = "continue"

    # Only record actual preference feedback.
    if feedback in ["like", "okay"]:
        record_music_feedback(
            song=state.get("selected_song", "unknown"),
            artist=state.get("selected_artist", "unknown"),
            mood=state.get("mood", "unknown"),
            activity=state.get("activity", "unknown"),
            action=feedback
        )

        print(f"[Memory] Recorded feedback: {feedback}")

    return {
        "change_requested": False,
        "next_step": "player"
    }

def route_after_memory(state: MusicState):

    if state.get("next_step") == "exit":
        return END

    if state.get("next_step") == "recommend":
        return "recommend"

    return "input"

def mood_analyzer_node(state: MusicState):

    print("\n[Mood Agent] Analyzing your current state...")

    prompt = f"""
You are a music recommendation assistant.

Analyze the user's statement:

"{state['user_input']}"

Determine:

1. Current mood
2. Energy level
3. Current activity
4. Desired emotional state

Return ONLY valid JSON:

{{
    "mood": "...",
    "energy": "...",
    "activity": "...",
    "desired_feeling": "..."
}}
"""

    response = llm_flash.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        content = content[0].get("text", "")


    content = content.strip()

    if content.startswith("```"):
      content = content.replace("```json", "")
      content = content.replace("```", "")
      content = content.strip()
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {
            "mood": "neutral",
            "energy": "medium",
            "activity": "general",
            "desired_feeling": "comfortable"
        }

    print(result)

    return {
        "mood": result["mood"],
        "energy": result["energy"],
        "activity": result["activity"],
        "desired_feeling": result["desired_feeling"],
        "next_step": "recommend"
    }


def recommendation_node(state: MusicState):

    print("\n[Music Agent] Creating personalized recommendation...")

    memory = get_music_memory.invoke({})

    prompt = f"""
You are a personalized music recommendation engine.

USER'S CURRENT STATE:

Mood: {state['mood']}
Energy: {state['energy']}
Activity: {state['activity']}
Desired feeling: {state['desired_feeling']}

USER'S MUSIC HISTORY:

{memory}

Use the user's actual listening history as the primary
source of their preferences.

Recommend music that fits BOTH:

1. Their current situation
2. Their established music taste

Do not assume that a genre is preferred merely because
it is popular.

CURRENT SESSION DIRECTION:

Current genre:
{state.get("current_genre", "None")}

Current direction:
{state.get("current_direction", "None")}

Change requested:
{state.get("change_requested", False)}

If a change has been requested, deliberately choose a
different musical direction from the current one.

Do not simply recommend another song from the same
direction unless the user's history strongly indicates
that it is appropriate.

Return ONLY valid JSON:

{{
    "genre": "...",
    "energy": "...",
    "vocals": "...",
    "reason": "...",
    "search_query": "..."
}}
"""

    response = llm_flash.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        content = content[0].get("text", "")

    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        result = {
            "genre": "unknown",
            "energy": "medium",
            "vocals": "mixed",
            "reason": "Fallback recommendation",
            "search_query": "music for your current mood"
        }

    print("\nRecommendation:")
    print(result)

    return {
    "recommendation": result,
    "current_genre": result.get("genre"),
    "current_direction": result.get("reason"),
    "change_requested": False,
    "next_step": "player"
}

# ==========================================
# 5. GRAPH CONSTRUCTION & ROUTING
# ==========================================

workflow = StateGraph(MusicState)

workflow.add_node("input", user_input_node)
workflow.add_node("mood", mood_analyzer_node)
workflow.add_node("recommend", recommendation_node)
workflow.add_node("player", music_player_node)

workflow.add_edge(START, "input")


def route_after_input(state: MusicState):

    if state.get("next_step") == "exit":
        return END

    return "mood"


workflow.add_conditional_edges(
    "input",
    route_after_input
)

workflow.add_edge("mood", "recommend")
workflow.add_edge("recommend", "player")

# IMPORTANT:
# The graph stops after preparing the current song.
# It does NOT wait for feedback.
workflow.add_edge("player", END)


music_graph = workflow.compile()

print("Music LangGraph compiled and ready.")

# ==========================================
# 6. EXECUTION LOOP
# ==========================================

if __name__ == "__main__":

    while True:

        try:

            result = music_graph.invoke({
                "user_input": "",
                "mood": None,
                "energy": None,
                "activity": None,
                "desired_feeling": None,
                "music_preferences": {},
                "recommendation": None,
                "selected_song": None,
                "selected_artist": None,
                "feedback": None,
                "change_requested": False,
                "next_step": None
            })

            print("\n[Session] Recommendation generated.")

            command = input(
                "\nCommand [new = new mood | exit = quit]: "
            ).strip().lower()

            if command == "exit":
                print("\nMusic assistant stopped.")
                break

            # Anything else starts another recommendation session

        except KeyboardInterrupt:
            print("\nStopped by user.")
            break

        except Exception as e:
            print(f"\nAn error occurred: {e}")
            break
