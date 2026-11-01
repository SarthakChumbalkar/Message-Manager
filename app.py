from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from telegram_client import connect_telegram, get_chats, get_messages, send_message
from ai_service import get_samples, analyze_sample

app = Flask(__name__)
app.secret_key = "change-this-local-secret"


# Local rules are used for live Telegram chats. Telegram's API terms restrict
# AI/ML use of Telegram-derived data unless Telegram grants an applicable exception.
def classify_chat(chat):
    message = (chat.get("last_message") or "").lower()
    unread = int(chat.get("unread_count") or 0)

    urgent_words = (
        "urgent", "asap", "emergency", "damaged", "broken", "refund",
        "complaint", "not received", "payment failed", "cancel", "immediately",
        "late delivery", "wrong item", "missing item"
    )
    business_words = (
        "price", "quotation", "wholesale", "bulk", "purchase", "order",
        "invoice", "payment", "booking", "interested", "availability"
    )

    if any(word in message for word in urgent_words):
        priority, score, category = "HIGH", 90, "Urgent / Complaint"
        reason = "The latest message contains an urgent-issue keyword."
    elif any(word in message for word in business_words):
        priority, score, category = "MEDIUM", 70, "Business Enquiry"
        reason = "The latest message may relate to a sale, order, or payment."
    elif unread > 0:
        priority, score, category = "MEDIUM", 60, "Unread Message"
        reason = "This conversation has unread messages."
    else:
        priority, score, category = "LOW", 30, "General"
        reason = "No configured priority keywords were detected."

    chat.update({
        "priority": priority,
        "priority_score": score,
        "category": category,
        "priority_reason": reason,
    })
    return chat


@app.route("/", methods=["GET", "POST"])
def home():
    try:
        connect_telegram()
        chats = [classify_chat(chat) for chat in get_chats(30)]
        priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        chats.sort(
            key=lambda chat: (
                priority_order[chat["priority"]],
                int(chat.get("unread_count") or 0),
                chat["priority_score"],
            ),
            reverse=True,
        )
    except Exception as exc:
        app.logger.exception("Could not load Telegram chats")
        return render_template(
            "index.html", chats=[], selected=None, messages=[],
            error=f"Could not connect to Telegram: {exc}", notices=[]
        ), 500

    if request.method == "POST":
        chat_id = request.form.get("chat_id", type=int)
        reply = request.form.get("reply", "").strip()
        if chat_id is None:
            flash("Select a valid conversation.", "error")
        elif reply:
            try:
                send_message(chat_id, reply)
                flash("Message sent successfully!", "success")
            except Exception:
                app.logger.exception("Failed to send Telegram reply")
                flash("Failed to send the reply. Check the terminal for details.", "error")
        return redirect(url_for("home", chat=chat_id))

    chat_id = request.args.get("chat", type=int)
    selected = next((chat for chat in chats if chat["id"] == chat_id), chats[0] if chats else None)
    messages = []

    if selected:
        try:
            messages = get_messages(selected["id"], limit=50)
        except Exception:
            app.logger.exception("Could not load message history")
            flash("Could not load this conversation's history.", "error")

    return render_template(
        "index.html", chats=chats, selected=selected, messages=messages,
        error=None, notices=get_flashed_messages(with_categories=True)
    )


@app.route("/ai-demo", methods=["GET", "POST"])
def ai_demo():
    samples = get_samples()
    selected_sample = request.form.get("sample", "urgent_complaint")
    if selected_sample not in samples:
        selected_sample = "urgent_complaint"

    result = None
    error = None
    if request.method == "POST":
        try:
            result = analyze_sample(selected_sample)
        except Exception as exc:
            app.logger.exception("Gemini demo analysis failed")
            error = str(exc)

    return render_template(
        "ai_demo.html", samples=samples, result=result,
        error=error, selected_sample=selected_sample
    )


if __name__ == "__main__":
    # threaded=False keeps the simple Telethon sync client on one request thread.
    app.run(debug=True, threaded=False, use_reloader=False)
