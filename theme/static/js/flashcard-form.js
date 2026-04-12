const FLASHCARD_FORM = {
    SELECTORS: {
        TEMPLATE: "#answer-template",
        ADD_BTN: ".js-add-new-answer",
        WRAPPER: ".js-answers-wrapper",
        TOTAL_FORMS: '[name$="-TOTAL_FORMS"]',
        REMOVE_ANSWER: ".js-remove-answer"
    },

    init() {
        this.template = document.querySelector(this.SELECTORS.TEMPLATE);
        this.addBtn = document.querySelector(this.SELECTORS.ADD_BTN);
        this.wrapper = document.querySelector(this.SELECTORS.WRAPPER);
        this.totalFormsInput = document.querySelector(this.SELECTORS.TOTAL_FORMS);

        // Bind add event
        if (this.addBtn && this.template && this.wrapper) {
            this.addBtn.addEventListener("click", this.handleAddAnswer.bind(this));
        }
        // Re-bind remove to any initial buttons (edit mode)
        document.querySelectorAll(this.SELECTORS.REMOVE_ANSWER).forEach(btn => {
            btn.addEventListener("click", this.handleRemoveAnswer.bind(this));
        });
    },

    handleAddAnswer(e) {
        e.preventDefault();
        if (!this.totalFormsInput) return;
        const formIdx = parseInt(this.totalFormsInput.value, 10);

        // Build new answer element from template
        const clone = this.template.content.cloneNode(true);
        this.replacePrefix(clone, formIdx);

        // Increment TOTAL_FORMS immediately
        this.totalFormsInput.value = formIdx + 1;

        // Find the answer element root and wire up remove button
        const answerElem = clone.querySelector(".js-answer-element");
        if (answerElem) {
            const removeBtn = answerElem.querySelector(this.SELECTORS.REMOVE_ANSWER);
            if (removeBtn) {
                removeBtn.addEventListener("click", this.handleRemoveAnswer.bind(this));
            }
        }

        this.wrapper.appendChild(clone);
    },

    handleRemoveAnswer(e) {
        e.preventDefault && e.preventDefault();
        const answerElem = e.currentTarget.closest(".js-answer-element");
        if (answerElem) {
            answerElem.remove();
            // Update TOTAL_FORMS appropriately
            if (this.totalFormsInput) {
                this.totalFormsInput.value = Math.max(parseInt(this.totalFormsInput.value, 10) - 1, 0);
            }
        }
    },

    replacePrefix(fragment, idx) {
        fragment.querySelectorAll("*").forEach(function(node) {
            if (node.name) {
                node.name = node.name.replace(/__prefix__/g, idx);
            }
            if (node.id) {
                node.id = node.id.replace(/__prefix__/g, idx);
            }
            if (node.getAttribute && node.getAttribute("for")) {
                node.setAttribute("for", node.getAttribute("for").replace(/__prefix__/g, idx));
            }
        });
    }
};

window.addEventListener("DOMContentLoaded", () => FLASHCARD_FORM.init());