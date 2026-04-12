window.addEventListener("DOMContentLoaded", function() {
    const template = document.querySelector("#answer-template");
    const trigger = document.querySelector(".js-add-new-answer");
    const wrapper = document.querySelector(".js-answers-wrapper");

    if (trigger && template && wrapper) {
        trigger.addEventListener("click", function(e) {
            e.preventDefault();

            // Clone the answer template content
            const clone = template.content.cloneNode(true);

            // Find the TOTAL_FORMS hidden input and increment its value
            const totalForms = document.querySelector('[name$="-TOTAL_FORMS"]');
            if (!totalForms) return;
            const formIdx = parseInt(totalForms.value, 10);

            // Replace __prefix__ in the cloned fields with the correct index
            clone.querySelectorAll("*").forEach(function(node) {
                if (node.name) {
                    node.name = node.name.replace(/__prefix__/g, formIdx);
                }
                if (node.id) {
                    node.id = node.id.replace(/__prefix__/g, formIdx);
                }
                // Fix labels 'for' attributes
                if (node.getAttribute && node.getAttribute("for")) {
                    node.setAttribute("for", node.getAttribute("for").replace(/__prefix__/g, formIdx));
                }
            });

            // Increment the total forms count
            totalForms.value = formIdx + 1;

            // Find the root of the new answer element (outermost div with .js-answer-element)
            let answerElem = null;
            // Try to find first element with .js-answer-element inside the clone
            clone.querySelectorAll(".js-answer-element").forEach(function(elem) {
                if (!answerElem) answerElem = elem;
            });

            // Ensure remove button exists and attach click handler
            if (answerElem) {
                let removeBtn = answerElem.querySelector(".js-remove-answer");
                if (!removeBtn) {
                    // Create remove button if not exists (for safety)
                    removeBtn = document.createElement("button");
                    removeBtn.type = "button";
                    removeBtn.className = "btn btn-error btn-xs js-remove-answer";
                    removeBtn.setAttribute("aria-label", "Remove answer");
                    removeBtn.innerHTML = "&times;";
                    answerElem.appendChild(removeBtn);
                }
                removeBtn.addEventListener("click", function() {
                    answerElem.remove();
                    // Decrement the total forms count
                    const newTotal = Math.max(parseInt(totalForms.value, 10) - 1, 0);
                    totalForms.value = newTotal;
                });
            }

            // Append the new answer element to the DOM
            wrapper.appendChild(clone);
        });
    }
});