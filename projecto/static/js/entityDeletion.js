//adds two buttons within a specified place on the page and interacts with them: deletes the entity if the backend allows it
//should be called on a (liekly) empty container, where the deleteButton is to be appended to

(function ($) {
    var deleteButtonClicked = false;
    var deleteButton;
    var warningText = $('<div class="" role="alert" id="warning-text"></div>');


    $.fn.entityDeletionListener = function(url, newLocation, entityType) {
        if (entityType == 'author') {
            deleteButton = $('<button id="delete-button" class="btn btn-warning pull-right">Delete author</button>');
        } else if (entityType == 'book') {
            deleteButton = $('<button id="delete-button" class="btn btn-warning pull-right">Delete book</button>');
        } else {
            return;
        }
        this.append([deleteButton, warningText]);

        deleteButton.click(function() {
            if (!deleteButtonClicked) {
                deleteButtonClicked = true;
                deleteButton.removeClass('btn-warning');
                deleteButton.addClass('btn-danger');
                warningText.addClass('alert alert-danger');
                warningText.text('Are you sure you want to irreversibly delete this entity?');

                return;
            }

            $.ajax({
                "credentials": 'same-origin',
                "url": url,
                "method": 'DELETE',
                "statusCode": {
                    "403": function() {
                        warningText.text('You are not permitted to delete this entity.');
                    },
                    "200": function() {
                        location.href = newLocation;
                    }
                }
            });
        });
    }
}(jQuery));
