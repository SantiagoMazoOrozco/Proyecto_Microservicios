const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./CSDB.db');

db.serialize(() => {
  // Ejemplo de consulta: Obtener todos los registros de una tabla específica
  db.each("SELECT * First Name", (err, row) => {
    if (err) {
      console.error(err.message);
    }
    console.log(row);
  });
});

db.close();
