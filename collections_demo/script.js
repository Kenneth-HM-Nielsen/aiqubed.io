document.getElementById('csvFileInput').addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (!file) return;
  
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: function (results) {
        const data = results.data;
        const fields = results.meta.fields;
        document.getElementById('summary').innerHTML = generateSummaryTable(data, fields);
        renderCharts(data, fields);
      }
    });
  });
  
  function generateSummaryTable(data, fields) {
    let html = '<h2>📄 Summary</h2>';
    html += '<table><thead><tr><th>Column</th><th>Non-Null Count</th><th>Unique</th></tr></thead><tbody>';
    fields.forEach(field => {
      const colData = data.map(row => row[field]);
      const nonNull = colData.filter(val => val !== "" && val !== null && val !== undefined).length;
      const unique = new Set(colData).size;
      html += `<tr><td>${field}</td><td>${nonNull}</td><td>${unique}</td></tr>`;
    });
    html += '</tbody></table>';
    return html;
  }
  
  function renderCharts(data, fields) {
    const chartsDiv = document.getElementById('charts');
    chartsDiv.innerHTML = '<h2>📈 Quick Column Visuals</h2>';
    fields.slice(0, 3).forEach(field => {
      const colData = data.map(row => row[field]).filter(x => x !== null && x !== undefined && x !== "");
      const numericData = colData.map(val => parseFloat(val)).filter(val => !isNaN(val));
  
      if (numericData.length > 0) {
        const divId = `chart-${field}`;
        chartsDiv.innerHTML += `<div id="${divId}" style="height:300px;"></div>`;
        Plotly.newPlot(divId, [{ x: numericData, type: 'histogram' }], { title: field });
      }
    });
  }
  