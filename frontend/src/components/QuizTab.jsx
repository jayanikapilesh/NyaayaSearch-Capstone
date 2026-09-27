import { useEffect, useState } from "react";
import { QUIZ_QUESTIONS } from "../quizData";
import { getQuizContent } from "../quizContent";
import { loadDailyQuizState, saveDailyQuizState, getTodayDateKey, getDailyQuizIndex, daysBetweenDateKeys } from "../utils";

// Works out which day's state to show, given whatever was last persisted
// (or nothing, on a first-ever visit). Pure given its argument - the only
// wall-clock read (getTodayDateKey) lives in utils.js, not here - so this
// is safe to call from a render body or an effect.
function computeDailyState(stored) {
  const dateKey = getTodayDateKey();
  const questionIndex = getDailyQuizIndex(dateKey, QUIZ_QUESTIONS.length);

  if (stored && stored.dateKey === dateKey) {
    // Same day as last visit - restore exactly as left it (answered or
    // not) rather than resetting, so revisiting today never loses progress.
    return { dateKey: dateKey, questionIndex: questionIndex, selected: stored.selected, streak: stored.streak };
  }

  // A new day (or nothing stored yet). The streak only carries forward if
  // the previous entry was answered yesterday specifically - a gap of more
  // than a day, or an unanswered day, breaks it.
  const wasYesterday = stored && daysBetweenDateKeys(dateKey, stored.dateKey) === 1;
  const continuedStreak = wasYesterday && stored.selected !== null ? stored.streak : 0;
  return { dateKey: dateKey, questionIndex: questionIndex, selected: null, streak: continuedStreak };
}

// NOTE: quiz question/option/explanation text comes from quizData.js and is
// still English-only by design (see quizContent.js for why). Only the
// surrounding UI chrome here is localized.
//
// "Legal IQ Daily" rotates through the existing question bank one question
// per calendar day (same day => same question for everyone), persists
// whether today's question has been answered so it doesn't reset on every
// visit, and tracks a small streak of consecutive days answered. No scores,
// leaderboards, badges, or notifications - just a lightweight daily habit.
function QuizTab({ uiLanguage = "en", isActive }) {
  const content = getQuizContent(uiLanguage);

  const [dailyState, setDailyState] = useState(function () {
    const computed = computeDailyState(loadDailyQuizState());
    saveDailyQuizState(computed);
    return computed;
  });

  // Tabs in this app never unmount (App.jsx just toggles display), so if
  // someone leaves this tab open across midnight, only switching back to it
  // will notice the day has changed - re-check whenever that happens.
  useEffect(function () {
    if (!isActive) return;
    const timer = setTimeout(function () {
      setDailyState(function (prev) {
        const computed = computeDailyState(loadDailyQuizState());
        if (computed.dateKey === prev.dateKey && computed.selected === prev.selected && computed.streak === prev.streak) {
          return prev;
        }
        saveDailyQuizState(computed);
        return computed;
      });
    }, 0);
    return function () { clearTimeout(timer); };
  }, [isActive]);

  const question = QUIZ_QUESTIONS[dailyState.questionIndex];
  const hasAnswered = dailyState.selected !== null;

  const handleAnswer = function (optionIndex) {
    if (hasAnswered) return;
    setDailyState(function (prev) {
      const updated = { dateKey: prev.dateKey, questionIndex: prev.questionIndex, selected: optionIndex, streak: prev.streak + 1 };
      saveDailyQuizState(updated);
      return updated;
    });
  };

  return (
    <div className="drafter-section">
      <div className="quiz-daily-header">
        <h2>{content.heading}</h2>
        {dailyState.streak > 0 && (
          <span className="quiz-streak-badge">{content.streakLabel(dailyState.streak)}</span>
        )}
      </div>
      <p className="quiz-question">{question.question}</p>
      <div className="quiz-options">
        {question.options.map(function (option, i) {
          let optionClass = "quiz-option";
          if (hasAnswered) {
            if (i === question.correctIndex) optionClass += " correct";
            else if (i === dailyState.selected) optionClass += " incorrect";
          }
          return (
            <button key={i} className={optionClass} onClick={function () { handleAnswer(i); }} disabled={hasAnswered}>
              {option}
            </button>
          );
        })}
      </div>
      {hasAnswered && (
        <div className="quiz-feedback">
          <p className="quiz-explanation">{question.explanation}</p>
          <p className="quiz-come-back">{content.comeBackTomorrow}</p>
        </div>
      )}
    </div>
  );
}

export default QuizTab;
