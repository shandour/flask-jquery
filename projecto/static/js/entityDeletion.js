//adds two buttons within a specified place on the page and interacts with them: deletes the entity if the backend allows it
//should be called on a (liekly) empty container, where the deleteButton is to be appended to

(function ($) {
    $.fn.entityDeletionListener = function(url, newLocation, entityType, loadingImage) {
        if (entityType == 'author') {
            var deleteButton = $('<button id="delete-button" class="btn btn-warning pull-right">Delete author</button>');
        } else if (entityType == 'book') {
            var deleteButton = $('<button id="delete-button" class="btn btn-warning pull-right">Delete book</button>');
        } else {
            return;
        }
        var warningText = $('<div class="" role="alert" id="warning-text"></div>');
        this.append([deleteButton, warningText]);

        var deleteButtonClicked = false;

        deleteButton.click(function() {
            if (!deleteButtonClicked) {
                deleteButtonClicked = true;
                deleteButton.removeClass('btn-warning');
                deleteButton.addClass('btn-danger');
                warningText.addClass('alert alert-danger');
                warningText.text('Are you sure you want to irreversibly delete this entity?');

                return;
            }

            warningText.remove();
            deleteButton.replaceWith(loadingImage);

            $.ajax({
                "credentials": 'same-origin',
                "url": url,
                "method": 'DELETE',
                "statusCode": {
                    "403": function() {
                        loadingImage.replaceWith('<div>You do not have the permissions required to delete this entity</div>');
                    },
                    "200": function() {
                        location.href = newLocation;
                    }
                }
            });
        });
    }
}(jQuery));
