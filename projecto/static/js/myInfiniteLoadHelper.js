(function ($) {
    $.fn.InfiniteLoadHelper = function(options)
    {
        var config = $.extend({}, $.fn.InfiniteLoadHelper.defaults, options);
        var entityContainer = this;

        $(config.loadButton).click(function() {
            var button = $(this).clone(withDataAndEvents=true);

            if (config.loadImage) {
                var img = config.loadImage
                $(this).replaceWith(img);
            }

            commenceLoad(config, entityContainer);

            if (config.loadImage) {
                img.replaceWith(button);
            }
        });
    }

    function commenceLoad(config, entityContainer) {
            if (!config.finished) {
                $.ajax(
                    {"url": (config.getEntitiesUrl + '?chunk=' + config.chunk +
                             '&letter=' + config.letter + '&type=' + config.type)
                    }).done(function(data){
                        for (var item of data[config.letter].items) {
                            if (config.type == 'books') {
                                var row = $('<tr></tr>');
                                var col1 = $('<td> <a href="' + config.getItemsUrl +
                                             '/' + item.id + '">' + item.title +
                                             '</a></td>');
                                var col2 = $('<td>' + item.authors.join('; ') + '</td>');
                                row = row.append(col1.add(col2));
                            } else if (config.type == 'authors') {
                                var row = $('<a href="' + config.getItemsUrl + '/'
                                            + item.id +
                                            '" class="list-group-item">'+
                                            (item.surname + ' ' + item.name).trim()
                                            + '</a>');
                            }
                            config.elementToAppendTo.append(row);
                        }
                        config.chunk++;
                        config.finished = data[config.letter].finished;
                        if (config.finished) {
                            entityContainer.append(config.warning);
                        }
                    });
            }
        }

    //basic config;
    $.fn.InfiniteLoadHelper.defaults = {
        "warning": $('<h3>No more results to load</h3>'),
        "chunk": 2,
        "letter": 'A',

        //the following five are required
        //should be similar to '/books/show' without a following dash and a number
        "getItemsUrl": null,
        "type": null,
        //the url the ajax call is made to
        "getEntitiesUrl": null,
        //should be the one inside the this element
        "elementToAppendTo": null,
        'loadButton': null,

        //an image to dispaly while the request is being processed
        'loadImage': null,

        //do not change the finished variable unless you want to disallow loading entities
        "finished": false
    };

} (jQuery));
