function search() {
    $(document).ready(function () {
        var form_data = new FormData($('#upload-file')[0]);
        var tie = document.getElementById("TIE").checked;
        var tie_rep = document.getElementById("dropdown-tie-rep").value;
        var tie_prov = document.getElementById("dropdown-tie-prov").value;
        var edr = document.getElementById("EDR").checked;

        var file_input = document.getElementsByClassName("custom-file-input")[0]

        form_data.append('tie', tie);
        form_data.append('tie_rep', tie_rep);
        form_data.append('tie_prov', tie_prov);
        form_data.append('edr', edr);

        //Check if file got selected
        if (file_input.files.length === 0) {
            $('#errorAlert').text('No file selected. Please select file.').show();
            $('#successAlert').hide();
            $('#inProgress').hide();
            return
        }

        //Check if correct file got uploaded
        if (file_input.files[0].type != 'text/csv') {
            $('#errorAlert').text('Wrong file type. Please upload csv file.').show();
            $('#successAlert').hide();
            $('#inProgress').hide();
            return
        }

        //Check if option got selected
        if (edr == false && tie == false) {
            console.log("No option selected.");
            $('#errorAlert').text('Please select an option to either set TIE reputations or run EDR lookups.').show();
            $('#successAlert').hide();
            $('#inProgress').hide();
            return;
        }

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
                console.log('Started Search.');
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

                //This is Unquarantine Action
                table = document.getElementById('table_res')
                for (index = 1; index < table.childNodes.length; index++) {
                    row = table.childNodes[index].childNodes;
                    cells = row[0].cells;
                    if (cells[2].innerText == 'Quarantined') {
                        qbnt = document.getElementById('reaction-' + index);
                        qbnt.innerText = 'Unquarantine';
                        qbnt.className = 'btn btn-primary btn-sm';
                        qbnt.setAttribute('onClick', 'unreact(this.id)');
                    }
                }
            }
        });
    });
};

function react(id) {
    $(document).ready(function () {
        var elem = document.getElementById(id);
        var cell = elem.parentElement;
        var value = elem.value
        var row = elem.closest("tr").children
        var hostname = row[0].innerText

        var formData = new FormData();
        formData.append('ids', value)

        for (index = 0; index < row.length; index++) {
            //console.log(row[index]);
        };

        $.ajax({
            type: 'POST',
            url: '/reaction',
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log('Reaction Execution');
            }
        })
        .done(function(data) {
            if (data.error) {
                console.log(error);
            }
            else {
                console.log('Success');
                elem.parentElement.removeChild(elem);

                var cancel = document.getElementById('cancel-'+id);
                cancel.parentElement.removeChild(cancel);

                var textobj = document.createElement('p');
                textobj.style.color = 'green';

                var text = document.createTextNode('Success');
                textobj.append(text);

                cell.append(textobj);
            }
        });
    });
};

function preq(id) {
    $(document).ready(function () {
        var confirm = document.getElementById(id);
        var elem = confirm.closest("tr").children[6];

        confirm.innerText = 'Confirm';
        confirm.setAttribute('onClick', 'react(this.id)');

        var back = document.createElement('BUTTON');
        btn.innerText = 'Cancel';
        btn.id = 'cancel-' + id
        btn.className = 'btn btn-primary btn-sm';
        btn.style.marginLeft = "10px";
        btn.setAttribute('onClick', 'cancel(this.id)')

        elem.append(btn);
    });
};

function cancel(id) {
    $(document).ready(function () {
        var cancel = document.getElementById(id);
        cancel.parentElement.removeChild(cancel);

        const ids = id.split('-');

        var confirm = document.getElementById(ids[1] + '-' + ids[2])
        confirm.innerText = 'Quarantine';
        confirm.setAttribute('onClick', 'preq(this.id)');

        return false;
    });
};

function unreact(id) {
    $(document).ready(function () {
        var elem = document.getElementById(id);
        var cell = elem.parentElement;
        var value = elem.value;

        var formData = new FormData();
        formData.append('ids', value);

        $.ajax({
            type: 'POST',
            url: '/unreact',
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log('Unquarantine Execution');
            }
        })
        .done(function(data) {
            if (data.error) {
                console.log(error);
            }
            else {
                elem.parentElement.removeChild(elem);
                var textobj = document.createElement('p');
                textobj.style.color = 'green';

                var text = document.createTextNode('Success');
                textobj.append(text);

                cell.append(textobj);
            }
        });
    });
};