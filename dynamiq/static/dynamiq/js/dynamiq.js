/**
 * Object holding simple & advanced search form methods.
 * It's more of a poor man's namespace than a real object at the moment.
 */
var DynamiqSearchFormHandling = function($) {
    $ = $;

    /**
     * Show filter element, changing various stuff on it (class, disabled attribute,
     * etc)
     */
    function show_filter_elm(elm) {
        elm.show().removeClass('js-hidden').prop('disabled', false);
    }

    /**
     * Hide filter element
     */
    function hide_filter_elm(elm) {
        elm.hide().addClass('js-hidden').prop('disabled', true);
    }

    /**
     * Method handling the change of the lookup field.
     * Usually call when the selected option for the filter_name <select> changes.
     */
    function change_dynamic_lookup(elm) {
        // FIXME: disable and re-init old lookup (to prevent garbage when submitting) ?
        var query_filter = elm;
        var parentElm = $(query_filter).parents('.query_fragment');
        var selected_option = $(elm.options[elm.selectedIndex], parentElm);
        var filter_type = selected_option.data('filtertype')
        if (filter_type) {
            // If a new filter type needs to be shown, find it, show it, and hide the rest
            var lookup_elm = $('#id_' + parentElm[0].id + '-' + filter_type + '_lookup');
            hide_filter_elm($('.filter_lookup', parentElm).not(lookup_elm))
            show_filter_elm(lookup_elm);
            // Since we changed the lookup, make sure its initialization method
            // is called - init is not done while the widget is hidden
            // FIXME: a cleaner way to do it would be to just trigger the 
            // "onchange" event on the correct element.
            change_dynamic_value_receptacle(lookup_elm[0]);
        }
    }

    /**
     * Method handling the change of the value receptacle.
     * Can happen when the selected option for the filter_name or filter_lookup
     * changes.
     */
    function change_dynamic_value_receptacle(elm) {
        // FIXME: disable and re-init old value (to prevent garbage when submitting) ?
        var query_filter = elm;
        var parentElm = $(query_filter).parents('.query_fragment');
        var selected_option = $(query_filter.options[query_filter.selectedIndex], parentElm);
        var filter_value = selected_option.data('filtervalue');
        if (filter_value) {
            // If a new filter value receptacle needs to be shown, find it, show it, and hide the rest
            // In addition, handle complex multi-input cases, as well as the combine operator between them
            // if necessary.
            var combine = null;
            var value_elm = $('#id_' + parentElm[0].id + '-filter_value_' + filter_value);
            if (value_elm.length <= 0) {
                var autocomplete_url = selected_option.data('filterautocomplete');
                var selector = '#id_' + parentElm[0].id + '-filter_value_' + filter_value;
                value_elm = $(selector + '_0, ' + selector + '_1, ' + selector + '_and');
                combine = value_elm.next('.filter_value_combine');
                if (filter_value == "autocomplete" && autocomplete_url) {
                    // if filter_value is autocomplete, then we need to (re-)
                    // init autocompletion
                    var autocomplete_result_elm = $('input[type=hidden].autocompleted', parentElm);
                    var autocomplete_input_elm = $('input[type=text].autocompleted', parentElm);

                    autocomplete_input_elm.autocomplete('destroy');
                    autocomplete_input_elm.autocomplete({
                        minLength: 3,
                        source: autocomplete_url,
                        select: function(event, ui) {
                            autocomplete_input_elm.val(ui.item.label);
                            if (ui.item.pk === 'None') {
                                // if the autocomplete result is not returning 
                                // a pk, then simply use the .value
                                autocomplete_result_elm.val(ui.item.value);
                            } else {
                                autocomplete_result_elm.val(ui.item.pk);
                            }
                            autocomplete_result_elm.trigger("added");
                            return false;
                        }
                    }).autocompletehtml();
                }
            }
            hide_filter_elm($('.filter_value', parentElm).not(value_elm))
            show_filter_elm(value_elm);
            if (combine) {
                combine.show().removeClass('js-hidden');
            }
        }
    }

    /**
     * Method handling the change of the form's action.
     * Usually call when the selected option for the filter_name <select>
     * changes.
     */
    function change_dynamic_form_action(elm) {
        var selected_option = $(elm.options[elm.selectedIndex]);
        var action_url = selected_option.data('actionurl');
        var f = elm.form;
        f.action = action_url;
    }

    /**
     * Method handling operator changing. It adds new forms to the formset if 
     * necessary and also make sure to switch the previous form operator if
     * needed (last form should never have a selected operator, since 
     * it's "alone")
     */
    function change_operator(elm) {
        var query_filter = elm;
        var parentElm = $(query_filter).parents('.query_fragment');
        var selected_option = elm.options[elm.selectedIndex];
        if (selected_option.value) {
            // if we selected something, add a new form below
            var next = parentElm.next();
            if (!next.hasClass('query_fragment')) {
                add_dynamic_form();
            }
        }
        if (selected_option.value == 'OR') {
            parentElm.addClass('or');
        } else {
            parentElm.removeClass('or');
        }
    }

    /**
     * Method adding a dynamic form to our formset
     */
    function add_dynamic_form() {
        // .formset('addForm') needs some data that has been set when formset()
        // has been calling (without arguments) for the first time.
        //
        // We can't garantee it has been the case for 'elm', therefore, instead
        // of using 'elm', we fetch the first element matching the original
        // selector
        return $('.advanced_search form .query_fragment').first().formset('addForm');
    }

    /**
     * Method adding and binding the "add form" button
     */
    function add_dynamic_add_form_button(elm) {
        elm = $(elm);
        elm.append('<li><a href="javascript:void(0)" class="add-form"></a></li>');
        var addButton = $('a.add-form', elm);
        addButton.click(function(e) {
            add_dynamic_form();
        });
    }

    /**
     * Method adding and binding the "delete form" button
     */
    function add_dynamic_delete_form_button(elm) {
        elm = $(elm);
        elm.append('<li><a href="javascript:void(0)" class="delete-form"></a></li>');
        var deleteButton = $('a.delete-form', elm);
        deleteButton.click(function(e) {
            var fragment = $(this).parents(".query_fragment")
            fragment.formset('deleteForm', fragment);
        });
    }

    /**
    * Method that modify a filter according to given data
    */
    function modify_filter(row, data) {
        // Select given filter_name and trigger change on filter_name's <select>
        // to make other dynamic stuff (lookup, value_receptacle) change as well
        var filter_name = data.filter_name
        row.find('.filter_name').val(filter_name).change();
        // If given, select lookup corresponding to filtername and trigger
        // change on it
        if (data.filter_lookup) {
            row.find('.filter_lookup:visible').val(data.filter_lookup).change();
        }
        // If given, fill value_receptacle (the one corresponding to filtername,
        // i.e. visible) and trigger change on it
        if (data.filter_value) {
            row.find('.filter_value:visible').val(data.filter_value);
        }
        // If given, select right operator and trigger change (in order to 
        // build next filter)
        if (data.right_op) {
            row.find('.right_op').val(data.right_op).change();
        }
        // Fill previous filter's rightOp (unless filter is the first one)
        if (data.previous_right_op && row.prev()) {
            var prev_filter = row.prev();
            prev_filter.find('.right_op').val(data.previous_right_op);
        }
    }

    /**
    * Build new filter according to `data`. New filter can
    * either be appended to existing filters or replace all existing ones.
    */
    function apply_filters_builder(data) {
        if (data.replace) {
            // Remove all filters, and build brand new ones according to given data
            var filters = $('.advanced_search form .query_fragment');
            filters.each(function(idx, item) {
                var $item = $(item);
                if (idx > 0) {
                    $item.formset('deleteForm', $item);
                }
            });
            modify_filter(filters.first(), data);
        } else {
            // Append a new filter
            var new_filter = add_dynamic_form();
            // Apply given data to new filter
            modify_filter(new_filter, data);
        }
    }

    function bind_filters_builders() {
        $('#filters_builders a').click(function() {
            var data = $(this).data('filterbuilder');
            apply_filters_builder(data);
            return false;
        })
    }

    /**
     * Method binding form "fragments", i.e. a django form inside the formset
     */
    function bind_form_fragment(fragment) {
        bind_form_dynamic_selects(fragment);

        $('.right_op', fragment).each(function(idx, item) {
            item.onchange = function(e) {
                change_operator(this);
            }
            change_operator(this);
        });

        add_dynamic_add_form_button(fragment);
        add_dynamic_delete_form_button(fragment);
    }

    /**
     * Method binding <select>s that can change pretty much anything in the form,
     * like the value receptacle, the lookup type ...
     */
    function bind_form_dynamic_selects(container) {
        $('.dynamic_select', container).each(function(idx, item) {
            item.onchange = function(e) {
                // We need to change lookup *last* because both the name and
                // the lookup can change the value receptacle.
                change_dynamic_value_receptacle(this);
                change_dynamic_lookup(this);
            }
            if (!$(item).hasClass('js-hidden')) {
                // We need to check item visibility to make sure inactive selects
                // don't change the lookup or value receptacle.
                change_dynamic_value_receptacle(item);
                change_dynamic_lookup(item);
            }
        });
    }


    /**
     * Bind .js-change_model <select>s to make sure they change the form's
     * action and available filters and sort options when necessary.
     */
    function bind_form(form) {
        $('.js-change_model', form).each(function(idx, item) {
            item.onchange = function(e) {
                change_dynamic_form_action(this);
                change_available_filters(this);
                change_available_sort_options(this);
            }
            change_dynamic_form_action(this);
            change_available_filters(this);
            change_available_sort_options(this);
        });
    }

    /**
     * Called by change_available_filters and change_available_sort_options to
     * update available options in a select, based on a list of options found
     * in a data attribute of the selected model option
     */
    function _change_model_relatives(model_select, data_name, relative_class) {
        var selected_option = $(model_select.options[model_select.selectedIndex]),
            data_choices = selected_option.data(data_name),
            all = false, 
            choices = [],
            selects = $(model_select).parents('form.search_form').find('select.' + relative_class);

        if (!data_choices) { 
            all = true;
        } else {
            choices = data_choices.split('|');
        }

        for (var num_select = 0; num_select < selects.length; num_select++) {
            var select = selects[num_select];
            for (var num_option = 0; num_option < select.options.length; num_option++) {
                var option = $(select.options[num_option]),
                    choice = option.val();
                if (all || $.inArray(choice, choices) != -1) {
                    option.removeProp('disabled');
                } else {
                    option.prop('disabled', true);
                }
            }
            if (select.options[select.selectedIndex].disabled) {
                $(select).css({borderColor: 'red'});
            } else {
                $(select).css({borderColor: ''});
            }
        }
    }

    /**
     * Limit filters to display depending on the selected model in elm
     */
    function change_available_filters(elm) {
        _change_model_relatives(elm, 'filters', 'filter_name');
    }

    /**
     * Limit sort options to display depending on the selected model in elm
     */
    function change_available_sort_options(elm) {
        _change_model_relatives(elm, 'sort', 'sort');
    }

    /**
     * Init function (doh!)
     */
    function init() {
        // Base initialization shared by simple and advanced form
        $('.search_form').each(function(idx, item) {
            bind_form(item);
        });

        // Simple form init.
        $('.simple_search_form').each(function(idx, item) {
            bind_form_dynamic_selects(item);
        });

        // Advanced form init. It calls formset() to allow us to dynamically
        // add/remove "forms", binds the dynamic selects, etc.
        var query_fragments = $('.advanced_search_form .query_fragment');
        if (!query_fragments.length) { return; }
        query_fragments.formset({
            prefix: 'form', // FIXME: use a real, unique id for our advanced search form
            deleteCssClass: 'delete-form',
            addText: '',
            deleteText: '',
            showAddButton: false,
            showDeleteButton: false,
            added: function(item) {
                // when added action is done, add class to the form - empty-form
                // doesn't have it because we don't want to execute js on it - and
                // manually call the function that is called on all initial forms
                // when loading the page
                item.addClass('query_fragment');
                bind_form_fragment(item);
            },
            beforeRemoved: function(item) {
                if (!item.next().hasClass('query_fragment')) {
                    // if it's the last form, change the right_op selected value to ""
                    // on the previous form
                    var elm = $('.right_op', item.prev()).get(0);
                    if (elm) {
                        elm.value = "";
                        change_operator(elm);
                    }
                    if (!item.prev().hasClass('query_fragment')) {
                        // if it's both the last and the first form... then we
                        // must keep it ! return false to prevent deletion
                        return false;
                    }
                }
                // return true to let deletion take place normally.
                return true;
            }
        });

        // Bind filters builders
        bind_filters_builders();

        query_fragments.each(function(idx, item) {
            bind_form_fragment(item);
        });

        // Simple search "more options" button
        $('#more_search_options').click(function(){
            $('#simple_search_options').toggle('fast');
            return false;
        });

        // Advanced search "more options" button
        $('#more_search_options_advanced').click(function(){
            $('#advanced_search_options').toggle('fast');
            return false;
        });

        return {
            // expose public methods here if necessary
        }
    }

    // call init when calling the function, returning public methods
    return init();
}

jQuery(document).ready(function($) {
    // init search form handling object - it binds dynamic forms and stuff like that
    var searchForms = DynamiqSearchFormHandling($);
});
