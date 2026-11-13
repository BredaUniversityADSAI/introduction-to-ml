// Multiple-choice questions for retrieval practice on Quarto pages.
//
// Markup in a .qmd page:
//
//   ::: {.quiz data-answer="2"}
//   What does training a model mean?
//
//   - First option. [Explanation shown when this option is chosen.]{.feedback}
//   - Second option. [...]{.feedback}
//   :::
//
// data-answer is the number of the correct option (counting from 1). The
// script turns the list into radio buttons; choosing one shows "Correct." or
// "Wrong." with that option's explanation. Learners can change their choice.
// All explanations are rendered up front, stacked in one grid cell and
// hidden, so the card already has room for the longest one and does not grow
// when an answer is chosen.
// Styles are in the quiz block of styles.css.

(() => {
  "use strict";

  let quizCount = 0;

  function mount(quiz) {
    const list = quiz.querySelector("ul, ol");
    if (!list) return;
    const answer = Number(quiz.dataset.answer);
    const name = `quiz-${++quizCount}`;

    const options = document.createElement("div");
    options.className = "quiz-options";
    options.setAttribute("role", "radiogroup");
    const question = quiz.querySelector("p");
    if (question) {
      question.classList.add("quiz-question");
      question.id = `${name}-question`;
      options.setAttribute("aria-labelledby", question.id);
    }

    const result = document.createElement("div");
    result.className = "quiz-result";
    result.setAttribute("aria-live", "polite");

    const labels = [];
    const messages = [];
    Array.from(list.children).forEach((item, i) => {
      const correct = i + 1 === answer;
      const feedback = item.querySelector(".feedback");
      const explanation = feedback ? feedback.innerHTML : "";
      if (feedback) feedback.remove();

      const label = document.createElement("label");
      label.className = "quiz-option";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = name;
      const text = document.createElement("span");
      // Pandoc may wrap list items in <p>; keep only the inline content.
      const inner = item.querySelector("p");
      text.innerHTML = (inner || item).innerHTML.trim();
      label.append(input, text);
      options.append(label);
      labels.push(label);

      const message = document.createElement("p");
      message.className = `quiz-message ${correct ? "is-correct" : "is-wrong"}`;
      message.innerHTML =
        `<strong>${correct ? "Correct." : "Wrong."}</strong> ${explanation}`;
      result.append(message);
      messages.push(message);

      input.addEventListener("change", () => {
        labels.forEach((l) => l.classList.remove("is-correct", "is-wrong"));
        label.classList.add(correct ? "is-correct" : "is-wrong");
        messages.forEach((m) => m.classList.toggle("is-shown", m === message));
      });
    });

    list.replaceWith(options);
    quiz.append(result);
    quiz.classList.add("is-ready");
  }

  function init() {
    document.querySelectorAll(".quiz[data-answer]").forEach(mount);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
