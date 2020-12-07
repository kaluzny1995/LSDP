// custom javascript

function alertBox(text, type) {
  html =
  `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
     <strong>${text}<button type="button" class="close" data-dismiss="alert" aria-label="Close">
       <span aria-hidden="true">&times;</span>
     </button>
   </div>`
   
   return html
}

function infoTable(results) {
  html_data =
  `<table class="table table-sm">
     <thead>
       <tr>
         <th>Total count</th>
         <th>Training  count</th>
         <th>Test count</th>
       </tr>
     </thead>
   <tbody>
     <tr>
       <td>${results.total}</td>
       <td>${results.train}</td>
       <td>${results.test}</td>
     </tr>
   </tbody>
  </table>`
  
  html_info =
  `<table class="table table-sm">
     <thead>
       <tr>
         <th>Model of ML</th>
         <th>Measure</th>
         <th>Value</th>
       </tr>
     </thead>
   <tbody>
     <tr>
       <td>${results.lr_title}</td>
       <td>${results.lr_abbr}</td>
       <td>${results.lr_result}</td>
     </tr>
     <tr>
       <td>${results.bc_title}</td>
       <td>${results.bc_abbr}</td>
       <td>${results.bc_result}</td>
     </tr>
     <tr>
       <td>${results.mcc_title}</td>
       <td>${results.mcc_abbr}</td>
       <td>${results.mcc_result}</td>
     </tr>
   </tbody>
  </table>`
  
  return [html_data, html_info]
}

function resultsTable(results) {
  html =
  `<table class="table table-sm">
     <thead>
       <tr>
         <th>Question/problem</th>
         <th>Decisional model</th>
         <th>Prediction</th>
       </tr>
     </thead>
   <tbody>
     <tr>
       <td>${results.lr_q}</td>
       <td>${results.lr_m}</td>
       <td>${results.lr_pred}</td>
     </tr>
     <tr>
       <td>${results.bc_q}</td>
       <td>${results.bc_m}</td>
       <td>${results.bc_pred}</td>
     </tr>
     <tr>
       <td>${results.mcc_q}</td>
       <td>${results.mcc_m}</td>
       <td>${results.mcc_pred}</td>
     </tr>
   </tbody>
  </table>`
  
  return html
}

$(document).ready(() => {
  ab = alertBox(`Warning! Models training in progress...`, 'warning')
  $('#alerts').append(ab)
  $('#retrain span').css('visibility', 'visible')
  
  trainModels()
});

/*$('#retrain').on('click', function() {
  ab = alertBox(`Warning! Models training in progress...`, 'warning')
  $('#alerts').append(ab)
  $('span', this).css('visibility', 'visible')
  
  trainModels()
});*/

$('#launch').on('click', function() {
  if ($('#text-input').val() === '') {
    ab = alertBox('Error! Field must have a text!', 'danger')
    $('#alerts').append(ab)
  }
  else {
    testModels()
  }
});

/*$('.b').on('click', function() {
  console.log($(this).text());
  $.ajax({
    url: '/tasks',
    data: {words: $(this).text()},
    method: 'POST'
  })
  .done((res) => {
    getStatus(res.data.task_id)
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to receive tasks! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
})*/

$('#load').on('click', function() {
  console.log($(this).text());
  $('span', this).css('visibility', 'visible')
  $.ajax({
    url: '/mongo',
    method: 'GET'
  })
  .done((res) => {
    getMongoResults(res.data.task_id)
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to receive submissions! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
})

function trainModels() {
  $('#text-input').prop('disabled', 'disabled')
  
  $.ajax({
    url: `/trainAll`,
    method: 'GET'
  })
  .done((res) => {
    getVerification(res.data.task_id)
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to train models! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}

function testModels() {
  $('#launch span').css('visibility', 'visible')
  
  $.ajax({
    url: `/testModels`,
    data: {text: $('#text-input').val()},
    method: 'POST'
  })
  .done((res) => {
    getResults(res.data.task_id)
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to train models! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}

function getResults(taskID) {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: 'GET'
  })
  .done((res) => {
    const taskStatus = res.data.task_status;
    const taskResults = res.data.task_result;
    if (taskStatus === 'finished') {
      ab = alertBox('Success! Tests done', 'success')
      $('#alerts').append(ab)
      html = resultsTable(taskResults)
      $('#results-table').html(html)
      $('#results-table').prepend(`<span><b>Text</b>:&nbsp;${$('#text-input').val()}</span><br /><br />`)
      $('#launch span').css('visibility', 'hidden')
      return false
    }
    else if (taskStatus === 'failed') {
      ab = alertBox('Error! Failed to test models!', 'danger')
      $('#alerts').append(ab)
      $('#launch span').css('visibility', 'hidden')
      return false
    }
    else {
      setTimeout(function() {
        getResults(res.data.task_id);
      }, 1000);
    }
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to get model testing results! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}

function getVerification(taskID) {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: 'GET'
  })
  .done((res) => {
    const taskStatus = res.data.task_status;
    const taskResults = res.data.task_result;
    if (taskStatus === 'finished') {
      ab = alertBox(`Success! Models trained successfully.`, 'success')
      $('#alerts').append(ab)
      html = infoTable(taskResults)
      $('#data-info-table').html(html[0])
      $('#ml-info-table').html(html[1])
      $('#text-input').removeAttr('disabled')
      $('#retrain span').css('visibility', 'hidden')
      return false
    }
    else if (taskStatus === 'failed') {
      ab = alertBox('Error! Failed to load train all models!', 'danger')
      $('#alerts').append(ab)
      $('#text-input').removeAttr('disabled')
      $('#retrain span').css('visibility', 'hidden')
      return false
    }
    else {
      setTimeout(function() {
        getVerification(res.data.task_id);
      }, 1000);
    }
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to load models! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}

/*function getStatus(taskID) {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: 'GET'
  })
  .done((res) => {
    const html = `
      <tr>
        <td>${res.data.task_id}</td>
        <td>${res.data.task_status}</td>
        <td>${JSON.stringify(res.data.task_result)}</td>
      </tr>`
    $('#tasks').prepend(html)
    const taskStatus = res.data.task_status;
    if (taskStatus === 'finished' || taskStatus === 'failed') return false;
    setTimeout(function() {
      getStatus(res.data.task_id);
    }, 1000);
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to get task status! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}*/

function getMongoResults(taskID) {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: 'GET'
  })
  .done((res) => {
    
    const taskStatus = res.data.task_status;
    const taskResults = res.data.task_result;
    if (taskStatus === 'finished') {
      $('#load span').css('visibility', 'hidden')
      taskResults.forEach(function(taskResult) {
        var html =
        `<tr>
          <td>${taskResult.id}</td>
          <td>${taskResult.author}</td>
          <td>${taskResult.title}</td>
          <td>${moment(new Date(1000*taskResult.time)).format('YYYY-MM-DD, HH:mm:ss')}</td>
        </tr>`
        $('#submissions').append(html)
      })
      return false
    }
    else if (taskStatus === 'failed') {
      $('#load span').css('visibility', 'hidden')
      alert('Error! Failed to receive MongoDB submissions!')
      return false
    }
    else {
      console.log('go again...')
      setTimeout(function() {
        getMongoResults(res.data.task_id);
      }, 1000);
    }
    
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to receive submissions! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}


