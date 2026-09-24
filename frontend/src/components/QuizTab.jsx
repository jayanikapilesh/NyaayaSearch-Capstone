import { useState } from "react";
import { QUIZ_QUESTIONS } from "../quizData";

function QuizTab() {
  const [quizIndex, setQuizIndex] = useState(0);
  const [quizScore, setQuizScore] = useState(0);
  const [quizSelected, setQuizSelected] = useState(null);
  const [quizFinished, setQuizFinished] = useState(false);

  const handleQuizAnswer = function (optionIndex) {
    if (quizSelected !== null) return;
    setQuizSelected(optionIndex);
    if (optionIndex === QUIZ_QUESTIONS[quizIndex].correctIndex) {
      setQuizScore(function (prev) { return prev + 1; });
    }
  };

  const handleQuizNext = function () {
    if (quizIndex + 1 < QUIZ_QUESTIONS.length) {
      setQuizIndex(function (prev) { return prev + 1; });
      setQuizSelected(null);
    } else {
      setQuizFinished(true);
    }
  };

  const handleQuizRestart = function () {
    setQuizIndex(0);
    setQuizScore(0);
    setQuizSelected(null);
    setQuizFinished(false);
  };

  return (
    <div className="drafter-section">
      <h2>Legal IQ Daily</h2>
      {!quizFinished ? (
        <div>
          <p className="quiz-progress">Question {quizIndex + 1} of {QUIZ_QUESTIONS.length}</p>
          <p className="quiz-question">{QUIZ_QUESTIONS[quizIndex].question}</p>
          <div className="quiz-options">
            {QUIZ_QUESTIONS[quizIndex].options.map(function (option, i) {
              let optionClass = "quiz-option";
              if (quizSelected !== null) {
                if (i === QUIZ_QUESTIONS[quizIndex].correctIndex) optionClass += " correct";
                else if (i === quizSelected) optionClass += " incorrect";
              }
              return (
                <button key={i} className={optionClass} onClick={function () { handleQuizAnswer(i); }} disabled={quizSelected !== null}>
                  {option}
                </button>
              );
            })}
          </div>
          {quizSelected !== null && (
            <div className="quiz-feedback">
              <p className="quiz-explanation">{QUIZ_QUESTIONS[quizIndex].explanation}</p>
              <button className="search-button" onClick={handleQuizNext}>
                {quizIndex + 1 < QUIZ_QUESTIONS.length ? "Next Question" : "See Results"}
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="quiz-results">
          <p className="quiz-score">You scored {quizScore} out of {QUIZ_QUESTIONS.length}</p>
          <button className="search-button" onClick={handleQuizRestart}>Try Again</button>
        </div>
      )}
    </div>
  );
}

export default QuizTab;
