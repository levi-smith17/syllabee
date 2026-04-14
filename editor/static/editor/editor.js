let editor = (function() {
    "use strict"; let self = {};

    self.offcanvas_full = null;

    $(window).on("load",(function() { self.initialize(); }));

    /**
     * Initializes all required variables and objects when the page is first loaded.
     */
    self.initialize = function() {
        const offcanvas_full_generic = $("#offcanvas-full-generic");
        if (offcanvas_full_generic.length) { self.offcanvas_full = new bootstrap.Offcanvas("#offcanvas-full-generic"); }
        if (offcanvas_full_generic.length) {
            const offcanvas_full = document.getElementById("offcanvas-full-generic");
            offcanvas_full.addEventListener("show.bs.offcanvas", event => {
                if (event.target === offcanvas_full) {
                    $(".offcanvas-full-backdrop").fadeIn().show();
                }//endif
            });
            offcanvas_full.addEventListener("hide.bs.offcanvas", event => {
                if (event.target === offcanvas_full) {
                    $(".offcanvas-full-backdrop").fadeOut().hide();
                }//endif
            });
        }//endif
    };//end initialize() function

    /**
     * Activates all event listeners across the entire web app (including those in other modules).
     */
    self.activate_handlers = function() {
        $(".add-form-row").off("click").on("click", function(e) {
            e.preventDefault();
            self.clone_form_row(".form-row:last", $(this).data("prefix"));
            return false;
        });
        $(".arrange").off("click").on("click", function(e) {
            e.stopPropagation();
            let direction = $(this).data("direction");
            let target = $(this).data("target");
            let index = $(target + " input[name='arrange']:checked").parent().attr("data-index");
            let count = $(target + " div").length, submit = "";
            let selected = $(target + " div[data-index='" + index + "']");
            if (direction === "up") {
                if (index > 1) {
                    let previous = selected.prev();
                    selected.after(previous);
                    previous.attr("data-index", index);
                    selected.attr("data-index", (parseInt(index) - 1));
                }
            } else {
                if (index <= (count - 1)) {
                    let next = selected.next();
                    selected.before(next);
                    next.attr("data-index", index);
                    selected.attr("data-index", (parseInt(index) + 1));
                }//endif
            }//endif-else
            for (let i = 1; i <= count; i++) {
                submit += $(target + " div[data-index='" + i + "'] input[name='arrange']").val();
                if (i !== count) { submit += "|"; }//endif
            }//endfor
            $(target + "-submit").val(submit);
            $(".editor-form button[type='submit']").prop('disabled', false);
        });
        $(".batch-copy-check").off("change").on("change", function() {
            let selected_id = $(this).data("selected-id");
            let selected_elements = $("#batch-copy-selected");
            if(this.checked) {
                let selected = $(this).data("selected");
                if (!~selected_elements.val().indexOf(selected_id + "|")) {
                    $("#batch-copy-preview-selected").append(selected);
                    selected_elements.val(selected_elements.val() + selected_id + "|");
                }//endif
            } else {
                $("#batch-copy-" + selected_id + "-selected").remove();
                selected_elements.val(selected_elements.val().replace(selected_id + "|", ""));
            }//endif-else
        });
        $(".clipboard").off("click").on("click", function() {
            const element = document.getElementById($(this).data("id")); // Get the text field
            element.select(); // Select the text field
            element.setSelectionRange(0, 99999); // For mobile devices.
            navigator.clipboard.writeText(element.value); // Copy the text to the clipboard.
            core.build_toast({}, "info", "URL copied to clipboard!")
        });
        $(".delete-form-row").off("click").on("click", function(e) {
            e.preventDefault();
            self.delete_form_row($(this).data("prefix"), $(this));
            core.activate_handlers_all();
            return false;
        });
        $(".editor-form").off("submit").on("submit", function(e) {
            e.preventDefault();
            let formData = new FormData(this);
            let url = $(this).attr("action");
            let model = $(this).data("model");
            let name = $(this).data("name");
            let operation = $(this).data("operation");
            let target = $(this).data("target");
            let callback = $(this).data("callback");
            let content_id = $(this).data("content-id");
            core.ajax("POST", target, url, true, formData, function() {
                if (typeof editor[callback] === "function") {
                    return editor[callback](model, name, operation, content_id);
                } else {
                    let error = {"responseText": '{"class": "danger", "code": 500, "text": ' +
                            '{"format": "A nontemporal problem occurred with the server\'s response. Please click ' +
                            'the version button at the bottom of the left-hand navbar to report this issue, and ' +
                            'include the following issue code when doing so: [<strong>tarsier-'+model+'-'+
                            operation+'</strong>]."}, "type": "Bad Request"}'};
                    core.build_toast(error);
                }//endif-else
            })
        });
        $(".modal-btn, .offcanvas-btn").off("click").on("click", function (e) {
            e.preventDefault();
            let title = $(this).attr("title");
            let control = $(this).data("control");
            let target = "#" + control + "-generic ." + control + "-container";
            let url = $(this).data("url");
            core.ajax("GET", target, url, true, "", function() {
                self.load_quill();
                $("#" + control + "-generic ." + control + "-title").html(title);
                if (control === "offcanvas" || control === "offcanvas-full") {
                    $("." + control + "-container").animate({scrollTop: 0}, 1);
                    if (control === "offcanvas") { core.offcanvas.show(); }
                    if (control === "offcanvas-full") { self.offcanvas_full.show(); }
                }//endif
                if (control === "modal") {
                    core.modal.show();
                }//endif
            });
        });
        $(".offcanvas-full-backdrop").off("click").on("click", function(e) {
            e.preventDefault(); self.offcanvas_full.hide(); $(this).hide();
        });
    };//end activate_handlers() function

    /**
     * Clones a selected form row and adds it to the form.
     *
     * @param {string} selector - A selector used to clone a form row as a DOM ID.
     * @param {string} prefix - A prefix for a form (to differentiate it from other forms).
     */
    self.clone_form_row = function(selector, prefix) {
        let new_element = $(selector).clone(true);
        let total = parseInt($("#id_" + prefix + "-TOTAL_FORMS").val());
        let max_rows = parseInt($("#id_" + prefix + "-MAX_NUM_FORMS").val());
        if (total < max_rows) {
            new_element.find(":input:not([type=button]):not([type=submit]):not([type=reset])").each(function () {
                let name = $(this).attr("name").replace("-" + (total - 1) + "-", "-" + total + "-");
                let id = "id_" + name;
                $(this).attr({"name": name, "id": id}).val("").removeAttr("checked");
                if ($(this).is(":checkbox")) { $(this).addClass("delete-form-row"); }//endif
            });
            new_element.find("label").each(function () {
                let for_value = $(this).attr("for");
                if (for_value) {
                    for_value = for_value.replace("-" + (total - 1) + "-", "-" + total + "-");
                    $(this).attr({"for": for_value});
                }//endif
            });
            total++;
            $("#id_" + prefix + "-TOTAL_FORMS").val(total);
            $(selector).after(new_element);
            core.activate_handlers_all();
        } else {
            let error = {"responseText": '{"class": "danger", "code": 400, "text": {"format": ' +
                    '"Maximum number of rows reached."}, "type": "Bad Request"}'};
            core.build_toast(error);
        }//endif-else
    }//end clone_form_row() function

    /**
     * Deletes a form row.
     *
     * @param {string} prefix - A prefix for a form (to differentiate it from other forms).
     * @param {string} btn - The button object that was clicked.
     */
    self.delete_form_row = function(prefix, btn) {
        let total = parseInt($("#id_" + prefix + "-TOTAL_FORMS").val());
        if (total > 1){
            btn.closest(".form-row").remove();
            let forms = $(".form-row");
            let form_count = forms.length;
            $("#id_" + prefix + "-TOTAL_FORMS").val(form_count);
            for (let i = 0; i < form_count; i++) {
                $(forms.get(i)).find(":input:selected").each(function() {
                    self.update_element_index(this, prefix, i);
                });
            }//endfor
        }//endif
    }//end delete_form_row() function

    /**
     * A generic callback handler for a POST AJAX call.
     *
     * @param {string} model - The name of the model affected by the POST request.
     * @param {string} name - The name of the object affected by the POST request.
     * @param {string} operation - The operation performed on the object.
     *
     * @returns {string} - A structured message for use in a notification to the user.
     */
    self.done_generic = function(model, name, operation) {
        core.offcanvas.hide();
        core.modal.hide();
        model = model.charAt(0).toUpperCase() + model.slice(1);
        self.load_quill();
        if (typeof name === "undefined") {
            return model + " " + operation + " successfully.";
        } else {
            return model + " (<strong>" + name + "</strong>) " + operation + " successfully.";
        }//endif-else
    }//end done_generic() function

    /**
     * A callback handler for a POST AJAX call that triggers the closing of the full offcanvas.
     *
     * @param {string} model - The name of the model affected by the POST request.
     * @param {string} name - The name of the object affected by the POST request.
     * @param {string} operation - The operation performed on the object.
     *
     * @returns {string} - A structured message for use in a notification to the user.
     */
    self.done_close_full = function(model, name, operation) {
        self.offcanvas_full.hide();
        return self.done_generic(model, name, operation);
    }//end done_close_full() function

    /**
     * A callback handler for a POST AJAX call that triggers the reloading of the content region.
     *
     * @param {string} model - The name of the model affected by the POST request.
     * @param {string} name - The name of the object affected by the POST request.
     * @param {string} operation - The operation performed on the object.
     * @param {string} request_content_id - The DOM ID of the content region affected.
     *
     * @returns {string} - A structured message for use in a notification to the user.
     */
    self.done_load_content = function(model, name, operation, request_content_id) {
        let content_container_data = $("#content-container-data");
        let dom_content_id = content_container_data.data("content-id");
        if (typeof dom_content_id !== "undefined" && typeof request_content_id !== "undefined") {
            if (~request_content_id.indexOf(dom_content_id)) {
                if (operation === 'locked' || operation === 'revised' || operation === 'unlocked'
                    || operation === 'updated') {
                    let content_json = content_container_data.data("content-json");
                    if (typeof content_json !== "undefined") {
                        loader.build_region(content_json, "content");
                    }//endif
                    let content_lock_json = content_container_data.data("content-lock-json");
                    if (typeof content_lock_json !== "undefined" && (operation === 'locked'
                        || operation === 'unlocked')) {
                        $.each(content_lock_json, function (target, url) {
                            core.ajax("GET", target, url, false);
                        });
                    }//endif
                } else {
                    let content_missing_json = content_container_data.data("content-missing-json");
                    if (typeof content_missing_json !== "undefined") {
                        loader.build_region(content_missing_json, "content");
                    }//endif
                }//endif-else
            }//endif
        }//endif
        return self.done_close_full(model, name, operation);
    }//end done_load_content() function

    /**
     * A callback handler for a POST AJAX call that triggers the reloading of all regions.
     *
     * @param {string} model - The name of the model affected by the POST request.
     * @param {string} name - The name of the object affected by the POST request.
     * @param {string} operation - The operation performed on the object.
     *
     * @returns {string} - A structured message for use in a notification to the user.
     */
    self.done_load_regions = function(model, name, operation) {
        loader.initialize_regions("#main-grid");
        return self.done_close_full(model, name, operation);
    }//end done_load_regions() function

    /**
     * A callback handler for a POST AJAX call (that replaced a segment), which triggers the reloading of all regions.
     *
     * @param {string} model - The name of the model affected by the POST request.
     * @param {string} name - The name of the object affected by the POST request.
     * @param {string} operation - The operation performed on the object.
     *
     * @returns {string} - A structured message for use in a notification to the user.
     */
    self.done_load_regions_replace = function(model, name, operation) {
        loader.initialize_regions("#main-grid");
        return self.done_close_full(model, name, "updated (<strong>and segment/block replaced</strong>)");
    }//end done_load_regions() function

    /**
     * A callback handler for a POST AJAX call that triggers the reloading of all regions with the search context.
     *
     * @param {string} model - The name of the model affected by the POST request.
     * @param {string} name - The name of the object affected by the POST request.
     * @param {string} operation - The operation performed on the object.
     *
     * @returns {string} - A structured message for use in a notification to the user.
     */
    self.done_load_search = function(model, name, operation) {
        loader.initialize_regions(".search-syllabi");
        return self.done_generic(model, name, operation);
    }//end done_load_regions() function

    /**
     * A callback handler for a POST AJAX call that triggers the reloading of a segment.
     *
     * @param {string} model - The name of the model affected by the POST request.
     * @param {string} name - The name of the object affected by the POST request.
     * @param {string} operation - The operation performed on the object.
     *
     * @returns {string} - A structured message for use in a notification to the user.
     */
    self.done_reload_segment = function(model, name, operation) {
        let new_url = $("#offcanvas-form").attr("action");
        core.ajax("GET", "#content-container", new_url.split("block/")[0], false)
        return self.done_generic(model, name, operation);
    }//end done_reload_segment() function

    /**
     * A callback handler for a POST AJAX call that triggers the reloading of the master syllabi dropdown.
     *
     * @param {string} model - The name of the model affected by the POST request.
     * @param {string} name - The name of the object affected by the POST request.
     * @param {string} operation - The operation performed on the object.
     *
     * @returns {string} - A structured message for use in a notification to the user.
     */
    self.done_reload_syllabi = function(model, name, operation) {
        core.ajax("GET", "#master-syllabi", $("#master-syllabi").data("url"), false)
        return self.done_generic(model, name, operation);
    }//end done_reload_syllabi() function

    /**
     * Loads the Quill editor.
     */
    self.load_quill = function() {
        $("#offcanvas-form .quill-editor").each(function() {
            /*var Block = Quill.import('blots/block');
            Block.tagName = "DIV";
            Quill.register(Block);*/
            const text_id = $(this).parent().next().attr("id");
            const quill = new Quill("#" + $(this).attr("id"), {
                modules: {
                    syntax: true,
                    toolbar: "#toolbar-container" ,
                },
                theme: "snow", // Specify theme in configuration
            });
            quill.on('text-change', (delta, oldDelta, source) => {
                $("#" + text_id).text(quill.getSemanticHTML(0, quill.getLength()));
            });
        });
    }//end load_quill() function

    /**
     * Triggers the preview of a segment (for use in the Copy Content interface).
     *
     * @param {string} target - The target element to receive the result of the AJAX request.
     * @param {string} url - The URL used in the AJAX request.
     * @param {string} segment_id - A unique identifier for a segment.
     */
    self.segment_preview = function(target, url, segment_id) {
        $("#lib-segment-" + segment_id + "-loader").show();
        $("#lib-segment-" + segment_id + "-content").empty();
        if (url) {
            core.ajax("GET", target, url, false, "", function() {
                $("#lib-segment-" + segment_id + "-loader").hide();
            });
        } else { core.url_error(); }//endif-else
    };//end segment() function

    /**
     * Updates an element's index within a form.
     *
     * @param {Object} element - The DOM element to be updated.
     * @param {string} prefix - A prefix to differentiate the element between forms.
     * @param {string} index - A unique identifier to replace on the element.
     */
    self.update_element_index = function(element, prefix, index) {
        let id_regex = new RegExp('(' + prefix + '-\\d+)');
        let replacement = prefix + "-" + index;
        if ($(element).attr("for")) $(element).attr("for", $(element).attr("for").replace(id_regex, replacement));
        if ($("label[for='" + element.id + "']").attr("for")) $("label[for='" + element.id + "']").attr("for", $("label[for='" + element.id + "']").attr("for", ).replace(id_regex, replacement));
        if (element.id) element.id = element.id.replace(id_regex, replacement);
        if (element.name) element.name = element.name.replace(id_regex, replacement);
    }//end update_element_index() function

    return self;
}());