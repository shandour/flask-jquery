function InfiniteLoadHelper(chunk, letter, url, type) {
    this.chunk = chunk;
    this.letter = letter;
    this.url = url;
    this.type = type;
    this.finished =-false;
    this.warning = $('<h3>No more results to load</h3>')
}

InfiniteLoadHelper.prototype.commenceLoad = function(getEntitiesUrl,
                                                     holderElement,
                                                     elementToAppendTo)
{
    if (!this.finished) {
        var $this = this;
        $.ajax(
            {url: (getEntitiesUrl + '?chunk=' + $this.chunk +
                   '&letter=' + $this.letter + '&type=' + $this.type)
            }).done(function(data){
                var get_items_url = $this.url;
                for (var item of data[$this.letter].items) {
                    if ($this.type == 'books') {
                        var row = $('<tr></tr>');
                        var col1 = $('<td> <a href="' + get_items_url +
                                     '/' + item.id + '">' + item.title +
                                     '</a></td>');
                        var col2 = $('<td>' + item.authors.join('; ') + '</td>');
                        row = row.append(col1.add(col2));
                    } else if ($this.type == 'authors') {
                        var row = $('<a href="' + get_items_url + '/'
                                    + item.id +
                                    '" class="list-group-item">'+
                                    (item.surname + ' ' + item.name).trim()
                                    + '</a>');
                    }
                    elementToAppendTo.append(row);
                }
                $this.chunk++
                $this.finished = data[$this.letter].finished;
            });
    } else {
        holderElement.append(this.warning);
    }
}


//get_items_url should be similar to '/books/show' without a following dash and a number
