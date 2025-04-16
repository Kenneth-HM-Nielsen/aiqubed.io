console.log("🚀 script.js loaded");

const input = document.getElementById('csvFileInput');
if (!input) {
  console.error("❌ #csvFileInput not found in DOM");
} else {
  console.log("✅ #csvFileInput found");

  input.addEventListener('change', function (e) {
    console.log("📁 File input changed");

    const file = e.target.files[0];
    if (!file) {
      console.warn("⚠️ No file selected");
      return;
    } else {
      console.log("✅ File selected:", file.name);
    }

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: function (results) {
        console.log("✅ CSV parsed", results);

        const data = results.data;
        const fields = results.meta.fields;

        if (!data.length) {
          console.warn("⚠️ CSV file contains no data");
          return;
        }

        document.getElementById('summary').innerHTML = generateSummaryTable(data, fields);

        // Clear chart divs before rendering new charts
        ['hist-principal', 'hist-outstanding', 'pie-product-type'].forEach(id => {
          const el = document.getElementById(id);
          if (el) el.innerHTML = '';
        });

        renderHistChart(data, 'principal_amount_at_initiation', 'hist-principal', 'Principal Amount at Initiation');
        renderHistChart(data, 'outstanding_debt', 'hist-outstanding', 'Outstanding Debt');
        renderPieChart(data, 'product_type', 'pie-product-type', 'Product Type Distribution');
      },
      error: function (err) {
        console.error("❌ Error parsing CSV:", err);
      }
    });
  });
}

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

function renderHistChart(data, column, containerId, title) {
  const values = data.map(row => parseFloat(row[column])).filter(val => !isNaN(val));
  console.log(`📊 Rendering histogram for ${column}:`, values.length, "valid values");

  if (values.length > 0) {
    Plotly.newPlot(containerId, [{
      x: values,
      type: 'histogram',
      marker: { color: '#66ccff' }
    }], {
      title: { text: title },
      margin: { t: 40 }
    });
  } else {
    console.warn(`⚠️ No valid numeric data found for column: ${column}`);
  }
}

function renderPieChart(data, column, containerId, title) {
  const counts = {};
  data.forEach(row => {
    const value = row[column];
    if (value) counts[value] = (counts[value] || 0) + 1;
  });

  const labels = Object.keys(counts);
  const values = Object.values(counts);

  console.log(`🥧 Rendering pie chart for ${column}:`, labels);

  if (labels.length > 0) {
    Plotly.newPlot(containerId, [{
      labels,
      values,
      type: 'pie',
      marker: { colors: ['#66ccff', '#ffaa00', '#00dd99'] }
    }], {
      title: { text: title },
      margin: { t: 40 }
    });
  } else {
    console.warn(`⚠️ No categorical values found for column: ${column}`);
  }
}
