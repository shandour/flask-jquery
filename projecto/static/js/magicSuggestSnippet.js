// variables for tracking suggestions wrapped in an object constructor; have to be defined
// if there is no initialValue pass null
function SuggestionsConfig(
    autoCompleteUrl,
    tagsInputElementId,
    currentQueryElementId,
    loadMoreElementId,
    wtFormInputId,
    entityType,
    displayField,
    initialValue)
{
    this.autoCompleteUrl = autoCompleteUrl;
    this.tagsInputElementId = tagsInputElementId;
    this.currentQueryElementId = currentQueryElementId;
    this.loadMoreElementId = loadMoreElementId;
    this.wtFormInputId = wtFormInputId;
    this.initialValue = initialValue;
    this.entityType = entityType;
    this.displayField = displayField;
    this.chunk = 1;
    this.lastQuery = null;
    this.finished = false;
    this.additionalSuggestions = [];
}

function applyMagicSuggest(config) {
    var suggestionsField = $(config.tagsInputElementId).magicSuggest({
        data: function(q) {
            q = q.trim();
            if (q.length == 0 || q == config.lastQuery) {
                return config.additionalSuggestions;
          }

            config.chunk = 1;
            config.additionalSuggestions = [];
            return config.autoCompleteUrl;
        },
        method: 'GET',
        dataUrlParams: {'chunk': 1, 't': config.entityType},
        allowFreeEntries: false,
        allowDuplicates: false,
        maxSelection: null,
        toggleOnClick: true,
        ajaxConfig: {

            complete: function(xhr, status) {
                config.finished = xhr.responseJSON.finished;
                config.additionalSuggestions = xhr.responseJSON.results;
                $(config.currentQueryElementId).text(config.lastQuery);
            },

            beforeSend: function(xhr, options) {
                var queryValue = options.url.match(/query=(\S*)&chunk/);
                if (queryValue === null) {
                    xhr.abort();
                    console.log('query empty');
                }
                queryValue = queryValue[1].trim();

                if (queryValue.endsWith('%20')) {
                    options.url = options.url.replace('%20', '');
                    queryValue = queryValue.slice(0, -3);
                }

                if (!(queryValue.length == 0)) {
                    if (queryValue.startsWith(config.lastQuery) && config.finished) {
                        xhr.abort();
                        console.log('no more suggestions to load for this query');
                    }
                    config.lastQuery = queryValue;
                } else {
                    xhr.abort();
                    console.log('query empty');
                }
            }

        },
        minChars: 2,
        hideTrigger: true,
        value: config.initialValue,
        displayField: config.displayField
    });


    $(config.loadMoreElementId).click( function(e) {
        if (config.finished || config.lastQuery === null) {
            $(this).addClass('disabled');
            return;
        }

        $(this).removeClass('disabled');
        config.chunk++;
        $.ajax({
            url: (config.autoCompleteUrl+ "?t=" +
                  config.entityType +"&query=" +
                  config.lastQuery + "&chunk=" + config.chunk)
        }).done(function(data, status, xhr) {
            config.additionalSuggestions = config.additionalSuggestions.concat(data.results);
            config.finished = data.finished;
        }).fail(function(xhr, status, error) {
            config.chunk--;
            console.log('query loading failed with status' + status);
        });

    });

    $('form').submit(function(e) {
        var valuesString = ''
        for (var i of suggestionsField.getSelection()) {
            valuesString += i.id + ',';
        }
        valuesString = valuesString.endsWith(',')? valuesString.slice(0, valuesString.lastIndexOf(',')) : valuesString;
        $(config.wtFormInputId).val(valuesString);
    });

}
