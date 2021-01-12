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
  checkModelsPresence()
});

function checkModelsPresence() {
  $('#text-input').prop('disabled', 'disabled')
  $('#launch span').css('visibility', 'visible')
  $('#retrain span').css('visibility', 'visible')
  
  $.ajax({
    url: `/checkModelsPresence`,
    method: 'GET'
  })
  .done((res) => {
    getPresenceCheck(res.data.task_id)
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to check models presence! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}
function getPresenceCheck(taskID) {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: 'GET'
  })
  .done((res) => {
    const taskStatus = res.data.task_status;
    const taskResults = res.data.task_result;
    if (taskStatus === 'finished') {
      if (taskResults.present === 0) {
        ab = alertBox(`Models not found! Training in progress...`, 'warning')
        $('#alerts').append(ab)
        
        console.log('trained models not found')
        processModels('train')
      }
      else {
        ab = alertBox(`Models loading in progress...`, 'info')
        $('#alerts').append(ab)
        
        console.log('trained models found')
        processModels('load')
      }
    }
    else if (taskStatus === 'failed') {
      ab = alertBox('Error! Failed to check models presence!', 'danger')
      $('#alerts').append(ab)
      return false
    }
    else {
      setTimeout(function() {
        getPresenceCheck(res.data.task_id);
      }, 1000);
    }
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to check models presence! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}



$('#retrain').on('click', function() {
  if ($('span', this).css('visibility') !== 'visible') {
    ab = alertBox(`Retraining in progress...`, 'info')
    $('#alerts').append(ab)
    
    $('#text-input').prop('disabled', 'disabled')
    $('#launch span').css('visibility', 'visible')
    $('span', this).css('visibility', 'visible')
    
    processModels('retrain')
  } 
});



function processModels(procType='train') {
  console.log(`${procType}ing models`)
  
  $.ajax({
    url: `/processModels/${procType}`,
    method: 'GET'
  })
  .done((res) => {
    getVerification(res.data.task_id, procType)
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to ${procType} models! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}
function getVerification(taskID, procType='train') {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: 'GET'
  })
  .done((res) => {
    const taskStatus = res.data.task_status;
    const taskResults = res.data.task_result;
    if (taskStatus === 'finished') {
      console.log(`${procType}ing finished`)
      ab = alertBox(`Success! Models ${procType}ed successfully.`, 'success')
      $('#alerts').append(ab)
      
      html = infoTable(taskResults)
      $('#data-info-table').html(html[0])
      $('#ml-info-table').html(html[1])
      
      $('#text-input').removeAttr('disabled')
      $('#launch span').css('visibility', 'hidden')
      $('#retrain span').css('visibility', 'hidden')
      return false
    }
    else if (taskStatus === 'failed') {
      ab = alertBox(`Error! Failed to ${procType} models!`, 'danger')
      $('#alerts').append(ab)
      
      $('#text-input').removeAttr('disabled')
      $('#launch span').css('visibility', 'hidden')
      $('#retrain span').css('visibility', 'hidden')
      return false
    }
    else {
      setTimeout(function() {
        getVerification(res.data.task_id, procType);
      }, 1000);
    }
  })
  .fail((err) => {
    ab = alertBox(`Error! Failed to ${procType} models! ${err}`, 'danger')
    $('#alerts').append(ab)
  })
}




$('#launch').on('click', function() {
  if ($('span', this).css('visibility') !== 'visible') {
    if ($('#text-input').val() === '') {
      ab = alertBox('Error! Input must have a text!', 'danger')
      $('#alerts').append(ab)
      
      return false
    }
    
    ab = alertBox(`Testing in progress...`, 'info')
    $('#alerts').append(ab)
    
    $('span', this).css('visibility', 'visible')
    $('#retrain span').css('visibility', 'visible')
    
    testModels()
  } 
});
function testModels() {
  console.log(`Testing models`)
  
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
      $('#retrain span').css('visibility', 'hidden')
      return false
    }
    else if (taskStatus === 'failed') {
      ab = alertBox('Error! Failed to get model testing results!', 'danger')
      $('#alerts').append(ab)
      
      $('#launch span').css('visibility', 'hidden')
      $('#retrain span').css('visibility', 'hidden')
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



$('#load').on('click', function() {
  console.log($(this).text().toLowerCase());
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

