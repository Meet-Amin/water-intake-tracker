import math
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.agent import WaterIntakeAgent
from src.database import (
    add_reminder,
    delete_reminder,
    get_daily_totals,
    get_habit_summary,
    get_intake_history,
    get_leaderboard,
    get_mood_history,
    get_reminders,
    get_user_goal,
    log_habit,
    log_intake,
    log_mood,
    upsert_user_goal,
)


def calculate_streak(daily_totals, goal_ml):
    totals_by_date = {date: total for date, total in daily_totals}
    if not totals_by_date:
        return 0, 0

    sorted_dates = sorted(
        totals_by_date.keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d")
    )
    longest = 0
    running = 0
    prev_date = None

    for date_str in sorted_dates:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        meets_goal = totals_by_date[date_str] >= goal_ml

        if meets_goal:
            if prev_date and (date_obj - prev_date).days == 1:
                running += 1
            else:
                running = 1
            longest = max(longest, running)
        else:
            running = 0

        prev_date = date_obj

    current = 0
    today = datetime.today().date()
    while True:
        date_str = today.strftime("%Y-%m-%d")
        if totals_by_date.get(date_str, 0) >= goal_ml:
            current += 1
            today -= timedelta(days=1)
        else:
            break

    return current, longest


def suggest_reminder_schedule(goal_ml, today_total: int) -> list[str]:
    remaining = max(goal_ml - today_total, 0)
    if remaining == 0:
        return ["Every goal for today is met. No additional reminders needed."]

    now = datetime.now()
    last_hour = now.replace(hour=22, minute=0, second=0, microsecond=0)
    window_minutes = max(int((last_hour - now).total_seconds() // 60), 30)
    per_sip = 250
    needed = math.ceil(remaining / per_sip)
    interval_minutes = max(window_minutes // needed if needed else window_minutes, 10)

    suggestions = []
    for i in range(needed):
        slot = now + timedelta(minutes=interval_minutes * (i + 1))
        suggestions.append(slot.strftime("Drink by %I:%M %p for ~250 ml"))

    return suggestions


def weather_tip(temp_celsius: float | None, humidity: float | None) -> str:
    nuggets = []
    if temp_celsius is not None:
        if temp_celsius >= 30:
            nuggets.append("Hot day—add 250 ml and sip electrolytes.")
        elif temp_celsius <= 5:
            nuggets.append("Cold weather—warm drinks help circulation and hydration.")
        else:
            nuggets.append("Mild temperature—keep your current cadence.")

    if humidity is not None:
        if humidity >= 70:
            nuggets.append("High humidity can hide thirst; schedule reminders.")
        elif humidity <= 30:
            nuggets.append("Dry air evaporates moisture quickly—sip an extra 150 ml.")

    return " ".join(nuggets) if nuggets else "Enter weather data to generate hydration cues."


def describe_badges(current_streak, longest_streak, today_total, goal_ml, weekly_total):
    badges = []
    if today_total >= goal_ml:
        badges.append(("Goal Achiever", "Hit today's goal—keep the momentum."))
    if current_streak >= 3:
        badges.append(("Streak Starter", f"{current_streak}-day streak going strong."))
    if longest_streak >= 7:
        badges.append(("Hydration Hero", f"Longest streak: {longest_streak} days."))
    if weekly_total >= goal_ml * 5:
        badges.append(("Consistency Champ", "Nearly reached five full days of your goal!"))
    if not badges:
        badges.append(("Keep Going", "Log more water or increase your goal to unlock badges."))
    return badges


def build_share_message(user_id, today_total, goal_ml, weekly_total):
    return (
        f"Hydration update for {user_id}: {today_total} ml logged today "
        f"(goal {goal_ml} ml) and {weekly_total} ml over the last 7 days. "
        "Join me in staying hydrated!"
    )


st.set_page_config(page_title="AI Water Tracker", layout="wide")

agent = WaterIntakeAgent()

if "tracker_started" not in st.session_state:
    st.session_state.tracker_started = False

if "user_id" not in st.session_state:
    st.session_state.user_id = "user_123"

if "weather_temp" not in st.session_state:
    st.session_state.weather_temp = 22.0

if "weather_humidity" not in st.session_state:
    st.session_state.weather_humidity = 45.0

if not st.session_state.tracker_started:
    st.title("Welcome to AI Water Tracker")
    st.markdown(
        """
        Track your daily hydration with the help of an AI Assistant.
        Log your intake, get smart feedback, and stay healthy.
    """
    )

    if st.button("Start Tracking"):
        st.session_state.tracker_started = True
        st.rerun()

else:
    st.title("AI Water Tracker Dashboard")
    st.subheader("Comprehensive hydration insights powered by AI")

    with st.sidebar:
        st.header("Hydration Controls")
        user_id = st.text_input("User ID", value=st.session_state.user_id)
        st.session_state.user_id = user_id

        sanitized_user_id = user_id.strip()
        stored_goal = (
            get_user_goal(sanitized_user_id) if sanitized_user_id else 2000
        )
        goal_setting = st.slider(
            "Daily Hydration Goal (ml)",
            min_value=1000,
            max_value=6000,
            value=stored_goal,
            step=100,
        )

        if st.button("Save Goal"):
            if not sanitized_user_id:
                st.error("Provide a valid User ID before saving a goal.")
            else:
                upsert_user_goal(sanitized_user_id, goal_setting)
                st.success("Daily goal updated.")
                st.rerun()

        with st.expander("Reminders", expanded=True):
            reminder_time = st.time_input(
                "Reminder time", value=datetime.now().time(), key="reminder_time"
            )
            reminder_label = st.text_input(
                "Note (optional)", key="reminder_label"
            )

            if st.button("Add Reminder", key="add_reminder"):
                if not sanitized_user_id:
                    st.error("Set a User ID to register reminders.")
                else:
                    add_reminder(
                        sanitized_user_id,
                        reminder_time.strftime("%H:%M"),
                        reminder_label,
                    )
                    st.success("Reminder scheduled.")
                    st.rerun()

            reminders = (
                get_reminders(sanitized_user_id) if sanitized_user_id else []
            )

            for reminder_id, time_str, label, _ in reminders:
                cols = st.columns([3, 1])
                cols[0].markdown(f"**{time_str}** {label or ''}")
                if cols[1].button(
                    "Delete", key=f"delete_reminder_{reminder_id}"
                ):
                    delete_reminder(reminder_id)
                    st.info("Reminder removed.")
                    st.rerun()

        with st.expander("Weather-aware tips", expanded=False):
            temp_celsius = st.number_input(
                "Temperature (°C)",
                min_value=-30.0,
                max_value=50.0,
                value=st.session_state.weather_temp,
                key="weather_temp",
            )
            humidity = st.number_input(
                "Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.weather_humidity,
                key="weather_humidity",
            )
            st.markdown(weather_tip(temp_celsius, humidity))

    weather_tip_text = weather_tip(
        st.session_state.weather_temp, st.session_state.weather_humidity
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Import Data")
    with st.sidebar.expander("CSV Intake Import"):
        st.markdown(
            "Upload a CSV with `intake_ml`, `date` (YYYY-MM-DD), and optional `user_id`."
        )
        csv_upload = st.file_uploader(
            "Upload hydration log", type="csv", key="csv_upload"
        )

        if csv_upload:
            try:
                import_df = pd.read_csv(csv_upload)

                if "intake_ml" not in import_df.columns or "date" not in import_df.columns:
                    st.error("CSV requires intake_ml and date columns.")
                else:
                    imported = 0
                    for row in import_df.to_dict("records"):
                        target_user = row.get("user_id", sanitized_user_id) or sanitized_user_id
                        if not target_user:
                            continue

                        intake_ml = int(row["intake_ml"])
                        intake_date = str(row["date"]).strip()
                        datetime.strptime(intake_date, "%Y-%m-%d")
                        log_intake(target_user, intake_ml, date=intake_date)
                        imported += 1

                    st.success(f"Imported {imported} rows.")
                    st.rerun()
            except Exception as exc:
                st.error(f"Could not import CSV: {exc}")

    st.markdown("### Hydration Metrics")
    st.info(weather_tip_text)

    if not sanitized_user_id:
        st.warning("Enter a User ID to see personalized metrics.")
        st.stop()

    intake_ml = st.sidebar.number_input(
        "Water Intake (ml)", min_value=0, max_value=5000, step=50
    )

    if st.sidebar.button("Submit Intake"):
        if intake_ml <= 0:
            st.sidebar.error("Add a positive intake value.")
        else:
            log_intake(sanitized_user_id, intake_ml)
            st.success(f"Logged {intake_ml} ml for {sanitized_user_id}")
            analysis = agent.analyse_intake(intake_ml)
            st.info(f"AI Feedback: {analysis}")
            st.rerun()

    daily_totals = get_daily_totals(sanitized_user_id, days=30)
    today_str = datetime.today().strftime("%Y-%m-%d")
    totals_map = {date: total for date, total in daily_totals}
    today_total = totals_map.get(today_str, 0)
    week_start = (datetime.today() - timedelta(days=6)).strftime("%Y-%m-%d")
    weekly_total = sum(
        total for date, total in daily_totals if date >= week_start
    )

    current_streak, longest_streak = calculate_streak(daily_totals, goal_setting)

    st.metric("Today's Intake", f"{today_total} ml", delta=f"Goal {goal_setting} ml")
    st.metric("Weekly Total", f"{weekly_total} ml")
    st.metric("Current Streak", f"{current_streak} days")
    st.metric("Longest Streak", f"{longest_streak} days")

    progress = min(today_total / goal_setting, 1.0) if goal_setting else 0.0
    st.progress(progress)

    st.markdown("### Smart reminder suggestions")
    suggestions = suggest_reminder_schedule(goal_setting, today_total)
    for suggestion in suggestions:
        st.caption(suggestion)

    st.markdown("### Badges")
    badges = describe_badges(current_streak, longest_streak, today_total, goal_setting, weekly_total)
    badge_cols = st.columns(len(badges))
    for col, (title, desc) in zip(badge_cols, badges):
        col.markdown(f"**{title}**")
        col.caption(desc)

    history = pd.DataFrame(
        get_intake_history(sanitized_user_id),
        columns=["Water Intake (ml)", "date"],
    )

    if not history.empty:
        history["date"] = pd.to_datetime(history["date"])
        st.markdown("### Intake History")
        st.dataframe(history.sort_values(by="date", ascending=False))

        chart_data = (
            history.groupby(history["date"].dt.date)["Water Intake (ml)"]
            .sum()
            .reset_index()
        )
        chart_data.columns = ["Date", "Water Intake (ml)"]
        st.line_chart(chart_data.set_index("Date"))
        st.bar_chart(chart_data.set_index("Date"))
    else:
        st.info("No intake has been logged yet. Start by submitting an intake.")

    st.markdown("---")
    st.markdown("### Mood & Habit Journal")
    mood_col, habit_col = st.columns(2)

    with mood_col:
        mood_level = st.slider("Mood rating (1 low – 10 high)", 1, 10, 6)
        mood_note = st.text_area("Reflection note", placeholder="How do you feel today?")
        if st.button("Log mood", key="mood_log"):
            log_mood(sanitized_user_id, mood_level, mood_note)
            st.success("Mood recorded.")
            st.rerun()

        mood_history = get_mood_history(sanitized_user_id)
        if mood_history:
            mood_df = pd.DataFrame(mood_history, columns=["Date", "Mood", "Note"])
            mood_df["Date"] = pd.to_datetime(mood_df["Date"])
            st.line_chart(mood_df.set_index("Date")["Mood"])
            st.dataframe(mood_df.head(10))
        else:
            st.caption("No mood entries yet.")

    with habit_col:
        habit_name = st.text_input("Habit name (e.g., 'Drink before meetings')")
        habit_completed = st.checkbox("Completed today?", value=True, key="habit_done")
        if st.button("Log habit", key="habit_log"):
            if habit_name.strip():
                log_habit(sanitized_user_id, habit_name.strip(), habit_completed)
                st.success("Habit logged.")
                st.rerun()
            else:
                st.error("Enter a habit description first.")

        habit_summary = get_habit_summary(sanitized_user_id)
        if habit_summary:
            habit_df = pd.DataFrame(habit_summary, columns=["Habit", "Completed", "Total"])
            habit_df["Compliance"] = (habit_df["Completed"] / habit_df["Total"] * 100).round(1)
            st.table(habit_df)
        else:
            st.caption("No habit logs yet.")

    st.markdown("---")
    st.markdown("### AI Weekly Reflection")
    try:
        ai_summary = agent.summarize_history(daily_totals[-7:], goal_setting)
        st.info(ai_summary)
    except Exception as exc:
        st.error(f"Unable to generate AI reflection: {exc}")

    st.markdown("---")
    st.markdown("### Weekly Leaderboard")
    leaders = get_leaderboard()
    if leaders:
        leaderboard_df = pd.DataFrame(
            leaders, columns=["User ID", "7-day total (ml)"]
        )
        leaderboard_df.index = range(1, len(leaderboard_df) + 1)
        st.table(leaderboard_df)
    else:
        st.info("No leaderboard data available yet.")

    st.markdown("---")
    st.markdown("### Share & Export")
    export_df = pd.DataFrame(daily_totals[-14:], columns=["Date", "Water Intake (ml)"])
    export_csv = export_df.to_csv(index=False)
    st.download_button(
        "Download recent hydration summary",
        data=export_csv,
        file_name=f"{sanitized_user_id}_hydration_summary.csv",
        mime="text/csv",
    )

    share_message = build_share_message(
        sanitized_user_id, today_total, goal_setting, weekly_total
    )
    st.text_area("Share this update", value=share_message, height=120)
