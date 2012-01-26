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

function closeRow(elemId) {
  var rowId = 'row' + elemId;
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
      $('table#links').trigger('update');
    },
    error: function(xhr, textStatus, errorThrown) {
      showError('Could not remove the link! Please try again later.');
    }
  });
}

// Append a row to the table
function appendRow(link, elemId, dateInsert, keywords) {
  var rowId = 'row' + elemId;

  var $table = $('table#links');
  $table.find('tbody').prepend(
    $('<tr>').attr('id', rowId).append(
      $('<td>').append(
        $('<a>')
          .attr('class', 'btn small danger')
          .attr('href', '#')
          .text('×')
        ).click(function(event) {
            closeRow(elemId);
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
      ).append(
        $('<td>').text(keywords)
      )
    );
    $table.trigger('update');
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

// Add table sorting parser. (TODO: is there no better solution than encoding back and forth?)
$.tablesorter.addParser({
  id: 'timestamp', // Set a unique id
  is: function(s) { // Return false so this parser is not auto detected
      return false;
  },
  format: function(s) {
      // format your data for normalization
      if (s == 'Now' || s == 'Some time ago') {
        return 0;
      }

      s = s.toLowerCase().replace(/about /, '').replace(/ ago/, '');
      var d = s.match(/\d+/);
      if (s.match(/minutes/)) {
        return d * 60;
      } else if (s.match(/hours/)) {
        return d * 3600;
      } else if (s.match(/days/)) {
        return d * 86400;
      } else if (s.match(/months/)) {
        return d * 86400 * 30;
      } else {
        return d * 86400 * 365;
      }
  },
  type: 'numeric'
});


function submitAddLink() {
  var $url = $('#url');
  var linkUrl = $url.val();
  var $keywords = $('#keywords');
  var keywordsValue = $keywords.val();

  if (linkUrl.length === 0) {
    showError('Please enter a link!');
    return;
  }

  if (linkUrl.substr(0, 7) != 'http://' && linkUrl.substr(0, 8) != 'https://') {
    linkUrl = 'http://' + linkUrl;
  }

  $url.attr('disabled');
  $keywords.attr('disabled');

  $.ajax({
    type : 'POST',
    url : '/add/',
    cache : false,
    data : { url: linkUrl, keywords: keywordsValue },
    dataType: 'json',
    success: function(result) {
      if (! result['ok']) {
        showError('Could not add the link! Please try again later');
        return;
      }

      appendRow(linkUrl, result['id'], 'Now', keywordsValue);

      $url.val('');
      $keywords.val('');
      $url.removeAttr('disabled');
      $keywords.removeAttr('disabled');
      enableOrDisableSubmit();

      showInfo('Link <a target="blank" href="' + linkUrl + '">' + getDisplayLink(linkUrl) + '</a> succesfully added.');
    },
    error: function(xhr, textStatus, errorThrown) {
      showError('Could not add the link! Please try again later');
    }
  });
}

$(document).ready(function() {
  // Enable - disable the "submit" button in accord with the length of the url field's content
  $('input#url').bind('keydown keyup', function(event) {
    enableOrDisableSubmit();
  });

  // Setup error message
  $('#errorMessage .close').click(function(event) {
    $('#errorMessage').addClass('hidden');
  });

  // Form submit action
  $('button#submit').click(function(event) {
    event.preventDefault();
    submitAddLink();
  });
  $('form#addlink').submit(function(event) {
    event.preventDefault();
    submitAddLink();
  });

  // Enable sorting for the table
  // if ($('table#links > tbody > td')) {
    $('table#links').tablesorter({
      headers: {
        2: {
          sorter: 'timestamp'
        },
        3: {
          sorter: false
        }
      },
      sortList: [[2, 0]]
    });
  // }

  // Enable modal button
  $('a#buttonInsert').click(function(event) {
    $('#insertModal').modal({
      keyboard: true
    })
  });

  // Enable search field
  var $search = $('input#search');
  $search.bind('keyup', function(event) {
    
  });
});
