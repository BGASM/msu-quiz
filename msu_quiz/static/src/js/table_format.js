$(document).ready(function() {
    var table = $('#quizTable').DataTable({
      "columnDefs": [{
        "visible": false,
        "targets": 5
      }],
      select: {
        style: 'multi'
      },
      dom: "<'row'<'col-sm-12 col-md-6'f><'col-sm-12 col-md-6'p>>" +
        "<'row'<'col-sm-12'tr>>" +
        "<'row'<'col-sm-12 col-md-6'i><'col-sm-12 col-md-6'B>>",
      buttons: [{
        text: 'Load Quizzes',
        action: function(e, dt, node, config) {
          return_data(table);
        }
      }]
    });
});

function return_data(table) {
  var selected = []
  table.rows({
    selected: true
  }).every(function(rowIdx) {
    selected.push(table.row(rowIdx).data())
  });
  console.log(selected)
  $.ajax({
    type: 'POST',
    url: "{{ url_for('quiz_bp.quiz')}}",
    data: JSON.stringify(selected),
    contentType: 'application/json; charset=ytf-8',
    success: function(response) {
      window.location.replace("/exam");
    },
    error: function(result) {
      alert('oops');
    }
  });
}