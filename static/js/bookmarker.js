function showError(errorMessage) {
  $('#errorMessage').removeClass('hidden');
  $('#errorMessage p').html(errorMessage);
}

function showInfo(message) {
  var infoDiv = $('<div>')
                  .attr('class', 'alert-message success');
  infoDiv.append($('<a>')
                    .attr('class', 'close')
                    .attr('href', '#')
                    .text('×')
                    .click(function(event) {
                      infoDiv.remove();
                    })
                  );
  infoDiv.append($('<p>')
                    .html(message)
                  );
  infoDiv.insertBefore($('div.row'));
}

function getDisplayLink(link) {
  if (link.substr(0, 7) === 'http://') {
    return link.substr(7);
  } else if (link.substr(0, 8) === 'https://') {
  return link.substr(8);
  } else {
    return link;
  }
}

// Append a row to the table (TODO: performances!)
function appendRow(link, elemId, dateInsert) {
  var rowId = 'row' + elemId;

  $('table#links').find('tbody').append(
    $('<tr>').attr('id', rowId).append(
      $('<td>').append(
        $('<a>')
          .attr('class', 'btn small danger')
          .attr('href', '#')
          .text('×')
        ).click(function(event) {
          var tr = $('tr#' + rowId);
          var link = $('tr#' + rowId + ' a:last').attr('href');
          $.ajax({
            type : 'POST',
            url : '/remove/',
            dataType : 'json',
            data : { id: elemId },
            // TODO: id
            success: function(data) {
              showInfo('Link <a target="blank" href="' + link + '">' + link + '</a> successfully removed.');
              tr.remove();
            },
            error: function(xhr, textStatus, errorThrown) {
              showError('Could not remove the link! Please try again later.');
            }
          })
        })
      ).append(
        $('<td>').append(
          $('<a>')
            .attr('href', link)
            .attr('target', 'blank')
            .text(getDisplayLink(link))
        )
      ).append(
        $('<td>').text(dateInsert)
      )
    );
}

function enableOrDisableSubmit() {
    var $submit = $('button#submit');
    var $urlField = $('input#url');

    var currentLength = $urlField.val().length;
    if (currentLength > 0) {
      $submit.removeAttr('disabled');
      $submit.removeClass('disabled');
    } else {
      $submit.attr('disabled');
      $submit.addClass('disabled');
    }
}

$(document).ready(function() {
  // Parse starting URLs
  $.ajax({
    type : 'GET',
    url : '/list/',
    cache : false,
    dataType : 'json',
    success : function(links) {
      $.each(links, function(index) {
        var link = links[index];
        appendRow(link['url'], link['id'], link['dateInsert']);
      })
    }
  });

  // Enable - disable the "submit" button in accord with the length of the url field's content
  $('input#url').bind('keydown keyup', enableOrDisableSubmit);

  // Setup error message
  $('#errorMessage .close').click(function(event) {
    $('#errorMessage').addClass('hidden');
  });

  // Form submit action
  $('form').submit(function(event) {
    event.preventDefault();

    $url = $('#url');
    var linkUrl = $url.val();

    if (linkUrl.length === 0) {
      showError('Please enter a link!');
      return;
    }

    if (linkUrl.substr(0, 7) != 'http://' && linkUrl.substr(0, 8) != 'https://') {
      linkUrl = 'http://' + linkUrl;
    }

    $url.attr('disabled');

    $.ajax({
      type : 'POST',
      url : '/add/',
      cache : false,
      data : { url: linkUrl },
      dataType: 'json',
      success: function(result) {
        if (! result['ok']) {
          showError('Could not add the link! Please try again later');
          return;
        }

        appendRow(linkUrl, result['id'], 'Now')

        $url.val('');
        $url.removeAttr('disabled');
        enableOrDisableSubmit();

        showInfo('Link <a target="blank" href="' + linkUrl + '">' + getDisplayLink(linkUrl) + '</a> succesfully added.');
      },
      error: function(xhr, textStatus, errorThrown) {
        showError('Could not add the link! Please try again later');
      }
    });
  });
});
