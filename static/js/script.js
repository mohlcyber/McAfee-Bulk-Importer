$(function() {
    $('#upload-file-btn').click(function() {
        var form_data = new FormData($('#upload-file')[0]);
        var tie = document.getElementById("TIE").checked;
        var tie_rep = document.getElementById("dropdown-tie-rep").value;
        var tie_prov = document.getElementById("dropdown-tie-prov").value;
        var edr = document.getElementById("EDR").checked;

        form_data.append('tie', tie);
        form_data.append('tie_rep', tie_rep);
        form_data.append('tie_prov', tie_prov);
        form_data.append('edr', edr);

        $.ajax({
            type: 'POST',
            url: '/process',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            beforeSend: function() {
                $('#successAlert').text('In Progress. Please wait...').show();
            },
            success: function(data) {
                console.log('Success!');
            },
        })
        .done(function(data) {

      if (data.error) {
        $('#errorAlert').text(data.error).show();
        $('#successAlert').hide();
        $('#inProgress').hide();
      }
      else {
        $('#successAlert').text(data.msg).show();
        $('#table_res').html(data.res);
        $('#tableResult').show();
        $('#errorAlert').hide();
        $('#inProgress').hide();
      }

    });
    });
});