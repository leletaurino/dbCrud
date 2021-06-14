var editor; // use a global for the submit and return data rendering in the examples
var office;
$(document).ready(function() {

    function showAlert(message) {
        $('#exampleModalLabel').html('Warning');
        $('#WarningMessage').html(message);
        $('#exampleModal').modal('show');
    }

    editor = new $.fn.dataTable.Editor( {
        ajax: {
            cache: true,
            create: {
                type: 'POST',
                url: "/insert_data",
                dataType: "text",
                contentType: 'application/json',
                data: function (d) {
                    var dteAction = d.action;
                    var dteData = d.data;
                    var key = Object.keys(dteData)[0];
                    var formData = dteData[key];
                    formData.office = $('#DTE_Field_office').val();
                    return JSON.stringify(formData);
                },
                success: function(response) {
                    console.log('success: ', response);
                    location.reload();
                }, error: function(jqXHR) {
                    console.log('error:', jqXHR);
                    //console.log('resp text:', jqXHR.responseText);
                    switch(jqXHR.status)
                    {
                        case 404:
                            showAlert('Requested page not found. [404]');
                            break;

                        case 500:
                            showAlert('Server error, check mandatory fields');
                            break;

                        case 512:
                            showAlert('Check the type of salary field.');
                            break;

                        case 513:
                            showAlert('Check the date format.');
                            break;

                        case 514:
                            showAlert('Salary must be greater then 0.');
                            break;

                        default:
                            showAlert('Unexpected unknow error');
                            break;
                    }
                }
            },
            edit: {
                type: 'POST',
                url: "/update_data",
                dataType: "text",
                contentType: 'application/json',
                data: function (d) {
                    var dteAction = d.action;
                    var dteData = d.data;
                    var key = Object.keys(dteData)[0];
                    var formData = dteData[key];
                    formData.office = $('#DTE_Field_office').val();
                    formData.salary = formData.salary.replace(',', '.');
                    formData.DT_RowId = key.split('_')[1];
                    return JSON.stringify(formData);
                    },
                success: function(response) {
                    console.log('success: ', response);
                    location.reload();
                },
                error: function(jqXHR) {
                    console.log('error:', jqXHR);
                    //console.log('resp text:', jqXHR.responseText);

                    switch(jqXHR.status)
                    {
                        case 404:
                            showAlert('Requested page not found. [404]');
                        break;

                        case 500:
                            showAlert('Server error, check mandatory fields');
                        break;

                        case 512:
                            showAlert('Check the type of salary field.');
                        break;

                        case 513:
                            showAlert('Check the date format.');
                        break;

                        case 514:
                            showAlert('Salary must be greater then 0.');
                        break;

                        default:
                            showAlert('Unexpected unknow error');
                        break;
                    }
                }
            },

            remove: {
                type: 'POST',
                url: "/delete_data",
                dataType: "text",
                contentType: 'application/json',
                data: function (d) {
                    var dteAction = d.action;
                    var dteData = d.data;
                    var key = Object.keys(dteData)[0];
                    var formData = dteData[key];
                    console.log('datae: ', formData);
                    return JSON.stringify(formData);
                },
                success: function(response) {
                    if(JSON.parse(response)['response'] !== 0)
                        alert('Attenzione, si è verificato un errore in fase di eliminaziione.');
                }
            }
        },
        table: "#example",
        template: '#customForm',
        fields: [ {
            label: "First name (*):",
            name: "first_name"
        }, {
            label: "Last name (*):",
            name: "last_name"
        }, {
            label: "Position:",
            name: "position"
        },
        {
            label: "Name:",
            name: "office",
            type: "select",
            options: []
        },

            {
            label: "Extension:",
            name: "extn"
        }, {
            label: "Start date (*):",
            name: "start_date",
            type: "datetime"
        }, {
            label: "Salary:",
            name: "salary"
        }
        ],
        /*formOptions: {
          main: {
            onComplete: 'none',
              fn: function () {
                  var that = this;
                  this.submit();
                  that.create();
              }
          }
        }*/
    } );

    editor.on( 'initEdit', function ( e, type ) {
        $.ajax({
            url: "/get_office_data",
            type: "GET",
            dataType: "text",
            contentType: 'application/json',
            success: function (response) {
                $("#DTE_Field_office").html('');
                var dati = JSON.parse(response)['data'];
                for (var i in dati){
                    var o = new Option(dati[i]['name'], dati[i]['id']);
                    $(o).html(dati[i]['name']);
                    $("#DTE_Field_office").append(o);
                }

                //$('#DTE_Field_salary').attr('type','number').attr('min', 0);
            }
        });

    });


    editor.on( 'initCreate', function ( e, type ) {

        $.ajax({
            url: "/get_office_data",
            type: "GET",
            dataType: "text",
            contentType: 'application/json',
            success: function (response) {
                $("#DTE_Field_office").html('');
                var dati = JSON.parse(response)['data'];
                for (var i in dati){
                    var o = new Option(dati[i]['name'], dati[i]['id']);
                    $(o).html(dati[i]['name']);
                    $("#DTE_Field_office").append(o);
                }
            }
        });
    });

/*    editor.on( 'preClose', function ( e ) {

        console.log('evento: ', e);
        console.log('editor: ', editor.get());

        return confirm( 'You have unsaved changes. Are you sure you want to exit?' );

    });*/
        /*.on( 'postCreate postEdit close', function () {
        editor.off( 'preClose' );
    });*/

    $('#example').DataTable( {
        ajax: {
                "url": "/get_data",
			    "cache": true
                },
        columns: [
            { data: null, render: function ( data, type, row ) {
                    // Combine the first and last names into a single table field
                    return data.first_name+' '+data.last_name;
                } },
            { data: "position" },
            { data: "office" },
            { data: "extn" },
            { data: "start_date" },
            { data: "salary", render: $.fn.dataTable.render.number( '.', ',', 2, '$' ) }
        ],
        select: true,
        dom: 'Bfrtip',
        buttons: [
            { extend: "create", editor: editor },
            { extend: "edit",   editor: editor },
            { extend: "remove", editor: editor }
        ]
    } );
} );