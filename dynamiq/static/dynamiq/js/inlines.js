/**
 * Django admin inlines
 *
 * Based on jQuery Formset 1.1
 * @author Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
 * @requires jQuery 1.2.6 or later
 *
 * Copyright (c) 2009, Stanislaus Madueke
 * All rights reserved.
 *
 * Spiced up with Code from Zain Memon's GSoC project 2009
 * and modified for Django by Jannis Leidel
 *
 * Remixed by Libération team to extend the API (2012).
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function($) {
    var totalForms;
    var nextIndex;
    var maxforms;
    var template;
    var options;

    var methods = {
        init : function( opts ) {
            return function($this) {
                // init stuff
                var data = $this.data('formset');
                var options;
                var totalForms;
                if (!data) {
                    options = $.extend({}, $.fn.formset.defaults, opts);
                    totalForms = $("#id_" + options.prefix + "-TOTAL_FORMS").attr("autocomplete", "off");
                    $this.data('formset', {
                        options: options,
                        totalForms: totalForms,
                        nextIndex: parseInt(totalForms.val()),
                        maxForms: $("#id_" + options.prefix + "-MAX_NUM_FORMS").attr("autocomplete", "off"),
                        template: $("#" + options.prefix + "-empty")
                    });
                    data = $this.data('formset');
                }

                // add form css class to every item we are calling the formset() function on (except empty ones)
                // and do fancyDeletion init on those items if necessary
                $this.each(function(i) {
                    $(this).not("." + data.options.emptyCssClass).addClass(data.options.formCssClass);
                    if (data.options.fancyDeletion && !($(this).hasClass(data.options.emptyCssClass))) {
                        $this.formset('initFancyDeletion', this);
                    }
                });

                // only show the add button if we are allowed to add more items,
                // note that max_num = None translates to a blank string.
                var showAddButton = data.options.showAddButton
                                    && (data.maxForms.val() == '' || (data.maxForms.val()-data.totalForms.val()) > 0);

                if ($this.length && showAddButton) {
                    if ($this.get(0).tagName.toUpperCase() == "TR") { // don't use .attr('tagName') in order to work with more recent versions of jQuery
                        // If forms are laid out as table rows, insert the
                        // "add" button in a new table row:
                        var numCols = $this.eq(0).children().length;
                        $this.parent().append('<tr class="' + data.options.addCssClass + '"><td colspan="' + numCols + '"><a href="javascript:void(0)">' + data.options.addText + "</a></tr>");
                        data.addButton = $this.parent().find("tr:last a");
                    } else {
                        // Otherwise, insert it immediately after the last form:
                        $this.filter(":last").after('<div class="' + data.options.addCssClass + '"><a href="javascript:void(0)">' + data.options.addText + "</a></div>");
                        data.addButton = $this.filter(":last").next().find("a");
                    }
                    data.addButton.click(function(e) {
                        $this.formset('addForm');
                    });
                }
            }(this);
        },
        
        initFancyDeletion : function(row) {
            // Fancy deletion hides the original -DELETE checkboxes and replace
            // them with the dynamic delete links, emulating the behaviour of
            // dynamically added rows. See softDeleteForm().
            var $this = $(this);
            var data = $this.data('formset');
            var row = $(row);
            var span;
            if (row.is('tr')) {
                // create span on the fly here, since we don't have one to begin with
                var input = $('.delete input', row).wrap('<span></span>');
                // .wrap() doesn't return the span...
                span = input.parent();
            } else {
                span = $('span.delete, span.deletelink', row)
            }
            span.hide();
            $(this).formset('addDeleteButton', row);
            row.find("a." + data.options.deleteCssClass).click(function(e) {
                var row = $(this).parents("." + data.options.formCssClass);
                $this.formset('softDeleteForm', row);
            });
            if (span.find('input:checked').length) {
                // span is already checked. hide the row.
                $this.formset('softDeleteForm', row);
            }
        },
        
        softDeleteForm : function(row) {
            // delete callback for rows that were already present when loading
            // the page (i.e., "static" ones). Only used if fancyDeletion is true
            // This hides the deleted row (but keeps it in the HTML!) and sets
            // the value of the -DELETE input
            var $this = $(this);
            var data = $this.data('formset');

            if (data.options.beforeRemoved) {
                data.options.beforeRemoved(row);
            }
            row.find('.delete input, .deletelink input').prop('checked', true);
            row.addClass('soft-deleted').hide();
            if (data.options.removed) {
                data.options.removed(row);
            }
            if (data.options.afterRemoved) {
                data.options.afterRemoved(row);
            }
        },

        updateElementIndex : function(el, prefix, ndx) {
            var id_regex = new RegExp("(" + prefix + "-(\\d+|__prefix__))");
            var replacement = prefix + "-" + ndx;
            if ($(el).attr("for")) {
                $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
            }
            if (el.id) {
                el.id = el.id.replace(id_regex, replacement);
            }
            if (el.name) {
                el.name = el.name.replace(id_regex, replacement);
            }
        },

        getRowIndex : function(row) {
            // get the row index
            var parts = row.attr('id').split('-');
            return parseInt(parts[parts.length-1], 10);
        },

        deleteForm : function(row) {
            var $this = $(this);
            if (!row) {
                row = $this.last();
            }
            var row_index = $this.formset('getRowIndex', row);
            var data = $(row).data('formset');
            // If a pre-delete callback was provided, call it with the deleted form:
            if (data.options.beforeRemoved) {
                result = data.options.beforeRemoved(row);
                if (!result) {
                    // if beforeRemoved returns false, then we prevent deletion
                    // completely.
                    return false;
                }
            }
            // Remove the parent form containing this button:
            row.remove();
            data.nextIndex -= 1;
            // If a post-delete callback was provided, call it with the deleted form:
            if (data.options.removed) {
                data.options.removed(row);
            }
            // Update the TOTAL_FORMS form count.
            var forms = $("." + data.options.formCssClass);
            $("#id_" + data.options.prefix + "-TOTAL_FORMS").val(forms.length);
            // Show add button again once we drop below max
            if ((data.maxForms.val() == '') || (data.maxForms.val()-forms.length) > 0) {
                if (typeof data.addButton != 'undefined') {
                    data.addButton.parent().show();
                }
            }
            // Also, update names and ids for all form controls with index greather
            // than the delete on so they remain in sequence:
            var new_index = row_index;
            for (var i=0, formCount=forms.length; i<formCount; i++)
            {
                var current_index = $this.formset('getRowIndex', $(forms).eq(i));
                if (current_index <= row_index) { continue; }
                $this.formset('updateElementIndex', $(forms).get(i), data.options.prefix, new_index);
                $(forms.get(i)).find("*").each(function() {
                    $this.formset('updateElementIndex', this, data.options.prefix, new_index);
                });
                new_index++;
            }
            // If a afterRemoved callback was provided, call it with the deleted form:
            // note that it's different from 'removed' and 'beforeRemoved', both
            // happen earlier.
            if (data.options.afterRemoved) {
                data.options.afterRemoved(row);
            }
            return false;
        },
        
        addDeleteButton : function(row) {
            var $this = $(this);
            var data = $this.data('formset');
            if (row.is("tr")) {
                // If the forms are laid out in table rows, insert
                // the remove button into the last table cell:
                row.children(":last").append('<div><a class="' + data.options.deleteCssClass +'" href="javascript:void(0)">' + data.options.deleteText + "</a></div>");
            } else if (row.is("ul") || row.is("ol")) {
                // If they're laid out as an ordered/unordered list,
                // insert an <li> after the last list item:
                row.append('<li><a class="' + data.options.deleteCssClass +'" href="javascript:void(0)">' + data.options.deleteText + "</a></li>");
            } else {
                // Otherwise, just insert the remove button as the
                // last child element of the form's container:
                row.children(":first").append('<span><a class="' + data.options.deleteCssClass + '" href="javascript:void(0)">' + data.options.deleteText + "</a></span>");
            }
        },

        addForm : function() {
            var $this = $(this);
            var data = $this.data('formset');
            var row = data.template.clone(true);
            row.removeClass(data.options.emptyCssClass)
                .addClass(data.options.formCssClass)
                .attr("id", data.options.prefix + "-" + data.nextIndex);
            row.data('formset', data);
            if (data.options.showDeleteButton) {
                $this.formset('addDeleteButton', row);
            }
            row.find("*").each(function() {
                methods.updateElementIndex(this, data.options.prefix, data.totalForms.val());
            });
            // Insert the new form when it has been fully edited
            row.insertBefore($(data.template));
            // Update number of total forms
            $(data.totalForms).val(parseInt(data.totalForms.val()) + 1);
            data.nextIndex += 1;
            // Hide add button in case we've hit the max, except we want to add infinitely
            if ((data.maxForms.val() != '') && (data.maxForms.val()-data.totalForms.val()) <= 0) {
                if (typeof data.addButton != 'undefined') {
                    data.addButton.parent().hide();
                }
            }
            // The delete button of each row triggers a bunch of other things
            row.find("a." + data.options.deleteCssClass).click(function(e) {
                var row = $(this).parents("." + data.options.formCssClass);
                $this.formset('deleteForm', row);
            });
            // If a post-add callback was supplied, call it with the added form:
            if (data.options.added) {
                data.options.added(row);
            }
            return row; // CHECKME: idea is to get the row added, to be able to modify it
        }
    };

    $.fn.formset = function( method ) {
        if ( methods[method] ) {
          return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
          return methods.init.apply( this, arguments );
        } else {
          $.error( 'Method ' +  method + ' does not exist on jQuery.formset' );
        }
    };

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: "form",                    // The form prefix for your django formset
        showAddButton: true,            // Boolean to prevent the add button from being automatically added
        showDeleteButton: true,         // Boolean to prevent the delete button from being automatically added
        addText: "add another",            // Text for the add link
        deleteText: "remove",            // Text for the delete link
        addCssClass: "add-row",            // CSS class applied to the add link
        deleteCssClass: "delete-row",    // CSS class applied to the delete link
        emptyCssClass: "empty-row",        // CSS class applied to the empty row
        formCssClass: "dynamic-form",    // CSS class applied to each form in a formset
        added: null,                    // Function called each time a new form is added
        beforeRemoved: null,            // Function called each time a form is deleted, before the deletion takes place (can prevent the deletion)
        removed: null,                    // Function called each time a form is deleted
        afterRemoved: null,               // Function called each time a form is deleted, after everything
        fancyDeletion: false              // Enable fancy deletion, which makes the elements already present behave like dynamically added ones
    };

})(jQuery);
