(function ($) {
    $.fn.InfiniteLoadHelper = function(options)
    {
        var config = $.extend({}, $.fn.InfiniteLoadHelper.defaults, options);

        this.commenceLoad = function() {
            if (!config.finished) {
                var self = this;
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
                            self.append(config.warning);
                        }
                    });
            }
        }
        return this;
    }


    //basic config;
    $.fn.InfiniteLoadHelper.defaults = {
        "warning": $('<h3>No more results to load</h3>'),
        "chunk": 2,
        "letter": 'A',

        //the following four are required
        //should be similar to '/books/show' without a following dash and a number
        "getItemsUrl": null,
        "type": null,
        //the url the ajax call is made to
        "getEntitiesUrl": null,
        //should be the one inside the this element
        "elementToAppendTo": null,

        //do not change the finished variable unless you want to disallow loading entities
        "finished": false
    };

} (jQuery));
